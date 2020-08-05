#!/usr/bin/python3

import argparse
import requests
import re
import sqlite3
from pathlib import Path
from subprocess import run
from os import path, makedirs, remove
from shutil import copyfile
from datetime import datetime, timedelta


MINECRAFT_DIR = '/mnt/lvm/series/Minecraft'
MAX_DAYS_BACK = 3

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Prints out helpful debug messages.')
parser.add_argument('-p', '--pretend', action='store_true',
                    help='Only pretent to download, convert, and store files')
args = parser.parse_args()


def log_message(message):
    if args.verbose:
        print(message)


class Model:
    FILE_PATH = path.expanduser('~/.youtube-series.downloader.db')
    FILE = Path(FILE_PATH)

    def __init__(self):
        log_message('Sqlite DB location: {}'.format(Model.FILE_PATH))
        self.connection = sqlite3.connect(Model.FILE_PATH)
        self.cursor = self.connection.cursor()

        # Create DB (if not exists)
        self._create_db()

    def _create_db(self):
        self.connection.execute(
            'Create TABLE IF NOT EXISTS video (id TEXT, episode_number INTEGER, channel_name TEXT)')
        self.connection.commit()

    def add_downloaded(self, channel_name, video_id):
        episode_number = self.get_next_episode_number(channel_name)

        log_message("{} Add to downloaded with episode number {}.".format(
            video_id, episode_number))

        if not args.pretend:
            sql = "INSERT INTO video (id, episode_number, channel_name) VALUES(?, ?, ?)"
            self.connection.execute(
                sql, (video_id, episode_number, channel_name))
            self.connection.commit()

    def get_next_episode_number(self, channel_name):
        sql_get_latest_episode = "SELECT episode_number FROM video WHERE channel_name=? ORDER BY episode_number DESC"
        self.cursor.execute(sql_get_latest_episode, [channel_name])
        row = self.cursor.fetchone()
        if row:
            return row[0] + 1
        else:
            return 1

    def has_downloaded(self, video_id):
        sql = "SELECT episode_number FROM video WHERE id=?"
        self.cursor.execute(sql, [video_id])
        row = self.cursor.fetchone()
        return bool(row)


class Video:
    def __init__(self, id, date, title, channel_name):
        self.id = id
        self.date = date
        self.title = title
        self.channel_name = channel_name


class Channel:
    RSS_PREFIX = "https://www.youtube.com/feeds/videos.xml?channel_id="
    REGEX = re.compile(
        "<entry>.*?<yt:videoId>(.*?)<\/yt:videoId>.*?<title>(.*?)<\/title>.*?<published>(.*?)<\/published>.*?<\/entry>", re.DOTALL)

    def __init__(self, name, channel_id, filters=[]):
        self.name = name
        self.channel_id = channel_id
        self.filters = filters

    def get_videos(self):
        log_message('\n\nGetting videos from ' + self.name)
        url = Channel.RSS_PREFIX + self.channel_id
        xml = requests.get(url).text

        matches = Channel.REGEX.findall(xml)

        videos = []

        for groups in matches:
            id = groups[0]
            title = groups[1]
            date = groups[2]
            log_message('{}: Checking video ({})'.format(id, date))

            if not self._matches_filter(title) and self._is_new(date):
                video = Video(id, date, title, self.name)
                log_message('{}: Appending video: {}'.format(id, title))
                videos.append(video)

        return videos

    def _is_new(self, dateString):
        date = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')
        diff_time = datetime.now() - date.replace(tzinfo=None)

        if diff_time.days <= MAX_DAYS_BACK:
            log_message('Is new by {} days'.format(diff_time.days))
            return True
        else:
            log_message('is old by {} days'.format(diff_time.days))
            return False

    def _matches_filter(self, title):
        for filter in self.filters:
            if re.search(filter, title):
                log_message('({}) Matched filter: {}'.format(title, filter))
                return True
        return False


class Downloader:
    TMP_DOWNLOAD = '/tmp/downloaded.mkv'
    TMP_CONVERTED = '/tmp/converted.mp4'

    def __init__(self, db, video):
        self.db = db
        self.video = video

    def has_downloaded(self):
        return self.db.has_downloaded(self.video.id)

    def download(self):
        completed_process = True
        if not args.pretend:
            completed_process = run(['youtube-dl', '-o', Downloader.TMP_DOWNLOAD, '-f', 'bestvideo[height>=1080,fps=60]+bestaudio',
                                     '--merge-output-format', 'mkv', '--restrict-filenames', '--', self.video.id]).returncode == 0
        if completed_process:
            self._convert()
        else:
            print('Failed to download video {} - {}, from channel {}'.format(
                self.video.title, self.video.id, self.video.channel_name))

        print(str(self._get_out_filepath()))

    def _convert(self):
        self._create_out_dir()
        out_filepath = self._get_out_filepath()
        downloaded = False

        if not args.pretend:
            completed_process = run(['ffmpeg', '-i', Downloader.TMP_DOWNLOAD, '-metadata', 'title="{}"'.format(self.video.title), '-threads', '2', '-filter_complex',
                                     '[0:v]setpts=(2/3)*PTS[v];[0:a]atempo=1.5[a]', '-map', '[v]', '-map', '[a]', Downloader.TMP_CONVERTED]).returncode == 0

            if completed_process:
                downloaded = True
                # Copy the temprory file to series/Minecraft
                log_message('{} Copying file to {}'.format(
                    self.video.id, out_filepath))
                copyfile(Downloader.TMP_CONVERTED, out_filepath)

                # Delete temporary files original file
                log_message(
                    '{} Deleting temporary files'.format(self.video.id))
                remove(Downloader.TMP_CONVERTED)
                remove(Downloader.TMP_DOWNLOAD)

        if downloaded or args.pretend:
            self.db.add_downloaded(self.video.channel_name, self.video.id)

    def _get_out_dir(self):
        return path.join(MINECRAFT_DIR, self.video.channel_name, 'Season 01')

    def _create_out_dir(self):
        makedirs(self._get_out_dir(), exist_ok=True)

    def _get_filename_safe(self):
        # Replace : or | with -
        title = re.sub(r'[:\|]', ' -', self.video.title)

        # Remove illegal characters
        title = re.sub(r'[^\w\ \-\.,]', '', title)

        # Remove all places where there are two whitespaces
        title = ' '.join(title.split())

        return title

    def _get_out_filepath(self):
        date_string = self.video.date[:10]
        episode_number = self.db.get_next_episode_number(
            self.video.channel_name)
        out_filename = '{} - s01e{} - {}.mp4'.format(
            self.video.channel_name, episode_number, self._get_filename_safe())
        out_filepath = path.join(self._get_out_dir(), out_filename)

        return out_filepath


channels = [
    Channel('Cubfan', 'UC9lJXqw4QZw-HWaZH6sN-xw'),
    Channel('Xisuma', 'UCU9pX8hKcrx06XfOB-VQLdw', [r'Live Now', r'LIVE NOW']),
    Channel('Keralis', 'UCcJgOennb0II4a_qi9OMkRA'),
    Channel('Etho', 'UCFKDEp9si4RmHFWJW1vYsMA'),
    Channel('Iskall', 'UCZ9x-z3iOnIbJxVpm1rsu2A'),
    Channel('Logical Geek Boy', 'UCJx74HaacAjDZk8LPdOfUFQ'),
    Channel('Grian', 'UCR9Gcq0CMm6YgTzsDxAxjOQ'),
    Channel('False Symmetry', 'UCuQYHhF6on6EXXO-_i_ClHQ'),
    Channel('ImpulseSV', 'UCuMJPFqazQI4SofSFEd-5zA'),
    Channel('Hypnotizd', 'UChi5MyXJLQuPni3dM19Ar3g', [r'Modded']),
    Channel('Tango Tek', 'UC4YUKOBld2PoOLzk0YZ80lw'),
    Channel('Good Times With Scar', 'UCodkNmk9oWRTIYZdr_HuSlg'),
    Channel('Mumbo Jumbo', 'UChFur_NwVSbUozOcF_F2kMg',
            [r'^(?!Hermitcraft).*']),
    Channel('BDoubleO', 'UClu2e7S8atp6tG2galK9hgg'),
    Channel('Zombie Cleo', 'UCjI5qxhtyv3srhWr60HemRw'),
    Channel('Docm', 'UC4O9HKe9Jt5yAhKuNv3LXpQ'),
    Channel('Ilmango', 'UCHSI8erNrN6hs3sUK6oONLA'),
    Channel('Gnembon', 'UCRtyLX-ej-H1PSiaw8g9aIA'),
    Channel('Rendog', 'UCDpdtiUfcdUCzokpRWORRqA'),
    Channel('Stressmonster', 'UC24lkOxZYna9nlXYBcJ9B8Q'),
    Channel('Zedaph', 'UCPK5G4jeoVEbUp5crKJl6CQ'),
]

db = Model()
total_downloaded = 0

for channel in channels:
    videos = channel.get_videos()

    for video in videos:
        downloader = Downloader(db, video)

        if not downloader.has_downloaded():
            downloader.download()
            total_downloaded += 1
        else:
            log_message('Skipping, already downloaded video')

log_message('Downloaded {} episodes'.format(total_downloaded))
