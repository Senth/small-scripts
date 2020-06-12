#!/usr/bin/python3

import requests
import re
from pathlib import Path
from subprocess import run
from os import path, makedirs, remove
from datetime import datetime, timedelta


MINECRAFT_DIR = '/mnt/lvm/series/Minecraft'
MAX_DAYS_BACK = 1


class Channel:
    RSS_PREFIX = "https://www.youtube.com/feeds/videos.xml?channel_id="
    REGEX = re.compile(
        "<entry>.*?<yt:videoId>(.*?)<\/yt:videoId>.*?<title>(.*?)<\/title>.*?<published>(.*?)<\/published>.*?<\/entry>", re.DOTALL)

    def __init__(self, name, channel_id, filters=[]):
        self.name = name
        self.channel_id = channel_id
        self.filters = filters

    def get_video_ids(self):
        url = Channel.RSS_PREFIX + self.channel_id
        xml = requests.get(url).text

        matches = Channel.REGEX.findall(xml)

        video_ids = []

        for groups in matches:
            id = groups[0]
            title = groups[1]
            date = groups[2]

            if not self._matches_filter(title) and self._is_new(date):
                video_ids.append(id)

        return video_ids

    def _is_new(self, dateString):
        date = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')
        diff_time = datetime.now() - date.replace(tzinfo=None)

        if diff_time.days <= MAX_DAYS_BACK:
            return True
        else:
            return False

    def _matches_filter(self, title):
        for filter in self.filters:
            if re.match(filter, title):
                return True
        return False


class Downloader:
    TMP_DOWNLOAD = '/tmp/%(upload_date)s - %(id)s.%(ext)s'

    def __init__(self, channel_name, video_id):
        self.channel_name = channel_name
        self.video_id = video_id

    def has_downloaded(self):
        if any(Path(MINECRAFT_DIR).rglob('*' + self.video_id + '*')):
            return True
        return False

    def download(self):
        run(['youtube-dl', '-o', Downloader.TMP_DOWNLOAD, '-f', 'bestvideo[height>=1080,fps=60]+bestaudio',
             '--merge-output-format', 'mkv', '--restrict-filenames', self.video_id])

        self._convert()

        print(str(self._get_in_and_out_filepath()))

    def _convert(self):
        self._create_out_dir()
        in_filepath, out_filepath = self._get_in_and_out_filepath()

        run(['ffmpeg', '-i', in_filepath, '-threads', '2', '-filter_complex',
             '[0:v]setpts=(2/3)*PTS[v];[0:a]atempo=1.5[a]', '-map', '[v]', '-map', '[a]', out_filepath])

        # Delete tmp file
        remove(in_filepath)

    def _get_out_dir(self):
        return path.join(MINECRAFT_DIR, self.channel_name, 'Season 01')

    def _create_out_dir(self):
        makedirs(self._get_out_dir(), exist_ok=True)

    def _get_in_and_out_filepath(self):
        in_filename = ''
        for file in Path('/tmp').rglob('*' + self.video_id + '*'):
            in_filename = file.name
        in_filepath = path.join('/tmp', in_filename)

        out_filename = self.channel_name + ' - ' + re.sub(
            '(\d{4})(\d{2})(\d{2}) ', '\g<1>-\g<2>-\g<3> ', in_filename)
        out_filepath = path.join(self._get_out_dir(), out_filename)

        return in_filepath, out_filepath


channels = [
    Channel('Cubfan', 'UC9lJXqw4QZw-HWaZH6sN-xw'),
    Channel('Xisuma', 'UCU9pX8hKcrx06XfOB-VQLdw', ['Live Now', 'LIVE NOW']),
    Channel('Keralis', 'UCcJgOennb0II4a_qi9OMkRA'),
    Channel('Etho', 'UCFKDEp9si4RmHFWJW1vYsMA'),
    Channel('Iskall', 'UCZ9x-z3iOnIbJxVpm1rsu2A'),
    Channel('Logical Geek Boy', 'UCJx74HaacAjDZk8LPdOfUFQ'),
    Channel('Grian', 'UCR9Gcq0CMm6YgTzsDxAxjOQ'),
    Channel('False Symmetry', 'UCuQYHhF6on6EXXO-_i_ClHQ'),
    Channel('ImpulseSV', 'UCuMJPFqazQI4SofSFEd-5zA'),
    Channel('Hypnotizd', 'UChi5MyXJLQuPni3dM19Ar3g', ['Modded']),
    Channel('Tango Tek', 'UC4YUKOBld2PoOLzk0YZ80lw'),
    Channel('Good Times With Scar', 'UCodkNmk9oWRTIYZdr_HuSlg'),
    Channel('Mumbo Jumbo', 'UChFur_NwVSbUozOcF_F2kMg'),
    Channel('BDoubleO', 'UClu2e7S8atp6tG2galK9hgg'),
    Channel('Zombie Cleo', 'UCjI5qxhtyv3srhWr60HemRw'),
    Channel('Docm', 'UC4O9HKe9Jt5yAhKuNv3LXpQ'),
    Channel('Ilmango', 'UCHSI8erNrN6hs3sUK6oONLA'),
    Channel('Gnembon', 'UCRtyLX-ej-H1PSiaw8g9aIA'),
]


for channel in channels:
    video_ids = channel.get_video_ids()

    for video_id in video_ids:
        print('Video id: ' + video_id)
        downloader = Downloader(channel.name, video_id)

        if not downloader.has_downloaded():
            downloader.download()
        else:
            print('Skipping, already downloaded video')
