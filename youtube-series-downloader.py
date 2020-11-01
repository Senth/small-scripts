#!/usr/bin/python3

import argparse
import requests
import re
import sqlite3
from pathlib import Path
from subprocess import run
from os import path, makedirs, remove
from shutil import copyfile
from datetime import datetime
from typing import List, Pattern


SERIES_DIR = '/mnt/lvm/series/'
MINECRAFT_DIR = 'Minecraft'
YOUTUBE_DIR = 'YouTube'
MAX_DAYS_BACK = 3
THREADS = 2

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

    def add_downloaded(self, channel_name: str, video_id: str):
        episode_number = self.get_next_episode_number(channel_name)

        log_message("{} Add to downloaded with episode number {}.".format(
            video_id, episode_number))

        if not args.pretend:
            sql = "INSERT INTO video (id, episode_number, channel_name) VALUES(?, ?, ?)"
            self.connection.execute(
                sql, (video_id, episode_number, channel_name))
            self.connection.commit()

    def get_next_episode_number(self, channel_name) -> int:
        sql_get_latest_episode = "SELECT episode_number FROM video WHERE channel_name=? ORDER BY episode_number DESC"
        self.cursor.execute(sql_get_latest_episode, [channel_name])
        row = self.cursor.fetchone()
        if row:
            return int(row[0]) + 1
        else:
            return 1

    def has_downloaded(self, video_id):
        sql = "SELECT episode_number FROM video WHERE id=?"
        self.cursor.execute(sql, [video_id])
        row = self.cursor.fetchone()
        return bool(row)


class Video:
    def __init__(self, id: str, date: str, title: str, channel_name: str):
        self.id = id
        self.date = date
        self.title = title
        self.channel_name = channel_name


class Channel:
    RSS_PREFIX = "https://www.youtube.com/feeds/videos.xml?channel_id="
    REGEX = re.compile(
        "<entry>.*?<yt:videoId>(.*?)<\/yt:videoId>.*?<title>(.*?)<\/title>.*?<published>(.*?)<\/published>.*?<\/entry>", re.DOTALL)

    def __init__(self, name: str, channel_id: str, collection_dir: str, excludes: List[Pattern] = [], includes: List[Pattern] = []):
        self.name = name
        self.channel_id = channel_id
        self.collection_dir = collection_dir
        self.excludes = excludes
        self.includes = includes

    def get_videos(self) -> List[Video]:
        log_message('\n\n**********************************')
        log_message(self.name.center(34))
        log_message('**********************************')

        url = Channel.RSS_PREFIX + self.channel_id
        xml = requests.get(url).text

        matches = Channel.REGEX.findall(xml)

        videos = []

        for groups in matches:
            id = groups[0]
            title = groups[1]
            date = groups[2]
            log_message('{}: Checking video ({})'.format(id, date))

            if not self._matches_excludes(title) and self._matches_includes(title) and self._is_new(date):
                video = Video(id, date, title, self.name)
                log_message('{}: Appending video: {}'.format(id, title))
                videos.append(video)

        return videos

    def _is_new(self, dateString: str) -> bool:
        date = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')
        diff_time = datetime.now() - date.replace(tzinfo=None)

        if diff_time.days <= MAX_DAYS_BACK:
            log_message('Is new by {} days'.format(diff_time.days))
            return True
        else:
            log_message('is old by {} days'.format(diff_time.days))
            return False

    def _matches_excludes(self, title: str) -> bool:
        for filter in self.excludes:
            if re.search(filter, title):
                log_message(
                    '--- ({}) Matched exclude: {}'.format(title, filter))
                return True
        return False

    def _matches_includes(self, title: str) -> bool:
        if len(self.includes) == 0:
            return True

        for filter in self.includes:
            if re.search(filter, title):
                log_message(
                    '+++ ({}) Matched include: {}'.format(title, filter))
                return True
        return False


class Downloader:
    TMP_DOWNLOAD = '/tmp/downloaded.mkv'
    TMP_CONVERTED = '/tmp/converted.mp4'

    def __init__(self, db: Model, video: Video, collection_dir: str):
        self.db = db
        self.video = video
        self.collection_dir = collection_dir

    def has_downloaded(self) -> bool:
        return self.db.has_downloaded(self.video.id)

    def download(self):
        completed_process = True
        if not args.pretend:
            completed_process = run(['youtube-dl', '-o', Downloader.TMP_DOWNLOAD, '-f', 'bestvideo[height>=1080,fps=60]+bestaudio',
                                     '--merge-output-format', 'mkv', '--restrict-filenames', '--', self.video.id]).returncode == 0
        if completed_process:
            self._convert()
        else:
            log_message('Failed to download video {} - {}, from channel {}'.format(
                self.video.title, self.video.id, self.video.channel_name))

        log_message(str(self._get_out_filepath()))

    def _convert(self):
        self._create_out_dir()
        out_filepath = self._get_out_filepath()
        downloaded = False

        if not args.pretend:
            completed_process = run(['ffmpeg', '-i', Downloader.TMP_DOWNLOAD, '-metadata', 'title="{}"'.format(self.video.title), '-threads', str(THREADS), '-filter_complex',
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

    def _get_out_dir(self) -> str:
        return path.join(SERIES_DIR, self.collection_dir, self.video.channel_name, 'Season 01')

    def _create_out_dir(self):
        makedirs(self._get_out_dir(), exist_ok=True)

    def _get_filename_safe(self) -> str:
        # Replace : or | with -
        title = re.sub(r'[:\|]', ' -', self.video.title)

        # Remove illegal characters
        title = re.sub(r'[^\w\ \-\.,]', '', title)

        # Remove all places where there are two whitespaces
        title = ' '.join(title.split())

        return title

    def _get_out_filepath(self) -> str:
        episode_number = self.db.get_next_episode_number(
            self.video.channel_name)
        out_filename = '{} - s01e{} - {}.mp4'.format(
            self.video.channel_name, episode_number, self._get_filename_safe())
        out_filepath = path.join(self._get_out_dir(), out_filename)

        return out_filepath


channels = [
    # --------------------------
    # --- MINECRAFT CHANNELS ---
    # --------------------------
    Channel('Cubfan', 'UC9lJXqw4QZw-HWaZH6sN-xw', MINECRAFT_DIR),
    Channel('Xisuma', 'UCU9pX8hKcrx06XfOB-VQLdw', MINECRAFT_DIR,
            excludes=[r'Live Now', r'LIVE NOW']),
    Channel('Keralis', 'UCcJgOennb0II4a_qi9OMkRA', MINECRAFT_DIR,
            includes=[r'Hermitcraft']),
    Channel('Etho', 'UCFKDEp9si4RmHFWJW1vYsMA', MINECRAFT_DIR),
    Channel('Iskall', 'UCZ9x-z3iOnIbJxVpm1rsu2A', MINECRAFT_DIR),
    Channel('Logical Geek Boy', 'UCJx74HaacAjDZk8LPdOfUFQ', MINECRAFT_DIR),
    Channel('Grian', 'UCR9Gcq0CMm6YgTzsDxAxjOQ', MINECRAFT_DIR),
    Channel('False Symmetry', 'UCuQYHhF6on6EXXO-_i_ClHQ', MINECRAFT_DIR),
    Channel('ImpulseSV', 'UCuMJPFqazQI4SofSFEd-5zA', MINECRAFT_DIR),
    Channel('Hypnotizd', 'UChi5MyXJLQuPni3dM19Ar3g', MINECRAFT_DIR,
            excludes=[r'Modded']),
    Channel('Tango Tek', 'UC4YUKOBld2PoOLzk0YZ80lw', MINECRAFT_DIR),
    Channel('Good Times With Scar', 'UCodkNmk9oWRTIYZdr_HuSlg', MINECRAFT_DIR),
    Channel('Mumbo Jumbo', 'UChFur_NwVSbUozOcF_F2kMg', MINECRAFT_DIR,
            includes=[r'Hermitcraft']),
    Channel('BDoubleO', 'UClu2e7S8atp6tG2galK9hgg', MINECRAFT_DIR),
    Channel('Zombie Cleo', 'UCjI5qxhtyv3srhWr60HemRw', MINECRAFT_DIR,
            includes=[r'Hermitcraft']),
    Channel('Docm', 'UC4O9HKe9Jt5yAhKuNv3LXpQ', MINECRAFT_DIR),
    Channel('Ilmango', 'UCHSI8erNrN6hs3sUK6oONLA', MINECRAFT_DIR),
    Channel('Gnembon', 'UCRtyLX-ej-H1PSiaw8g9aIA', MINECRAFT_DIR),
    Channel('Rendog', 'UCDpdtiUfcdUCzokpRWORRqA', MINECRAFT_DIR),
    Channel('Stressmonster', 'UC24lkOxZYna9nlXYBcJ9B8Q', MINECRAFT_DIR),
    Channel('Zedaph', 'UCPK5G4jeoVEbUp5crKJl6CQ', MINECRAFT_DIR),

    # ------------------------------
    # --- Other YouTube Channels ---
    # ------------------------------
    Channel('Xterminator', 'UC5StrkKVnU2xkjV0mVJ9yTw', YOUTUBE_DIR,
            includes=[r'Spotlight', r'ALT-F4']),
]

db = Model()
total_downloaded = 0

for channel in channels:
    videos = channel.get_videos()
    log_message('')

    for video in videos:
        downloader = Downloader(db, video, channel.collection_dir)

        if not downloader.has_downloaded():
            downloader.download()
            total_downloaded += 1
        else:
            log_message('------ Skipping, no new videos to download ------')

log_message('\n\n\nDownloaded {} episodes'.format(total_downloaded))
