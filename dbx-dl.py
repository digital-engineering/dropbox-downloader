#!/usr/bin/env python3
"""Dropbox Downloader

Usage:
  dbx-dl.py download-recursive
  dbx-dl.py du [<path>]
  dbx-dl.py ls [<path>]
  dbx-dl.py (-h | --help)
  dbx-dl.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
import dropbox
import dropbox.exceptions
import os.path

from docopt import docopt
from dropbox.files import FolderMetadata, FileMetadata
from configparser import ConfigParser
from queue import Queue

from dropbox_downloader.DiskUsage import DiskUsage
from dropbox_downloader.Downloader import Downloader
from dropbox_downloader.DownloadWorker import DownloadWorker


class DropboxDownloader:
    """Controlling class for console command."""

    def __init__(self):
        self._base_path = os.path.dirname(os.path.realpath(__file__))
        ini_settings = self._load_config()
        self._dbx = dropbox.Dropbox(ini_settings.get('main', 'api_key'))
        self._dl_dir = ini_settings.get('main', 'dl_dir')
        self._to_dl = str(ini_settings.get('main', 'to_dl')).split(',') or None

    def dl(self, path: str = ''):
        d = Downloader(self._base_path, self._dbx, self._dl_dir, self._to_dl)
        queue = Queue()

        # Create 8 ListWorker threads
        for x in range(8):
            worker = DownloadWorker(d, queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        files_and_folders = d.list_files_and_folders(path)
        for f in files_and_folders.entries:
            if isinstance(f, FolderMetadata):
                queue.put(f.path_lower)
            elif isinstance(f, FileMetadata):
                d.download_file(f.path_lower)
            else:
                raise RuntimeError(
                    'Unexpected folder entry: {}\nExpected types: FolderMetadata, FileMetadata'.format(f))

        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()

    def du(self, path: str):
        """Get disk usage (size) for path"""
        du = DiskUsage(self._dbx)
        du.du(path)

    def ls(self, path: str):
        """Print contents of a given folder path in text columns"""
        files_and_folders = self._dbx.files_list_folder(path)
        print('Listing path "{}"...'.format(path))
        file_list = [{
            'id':         f.id,
            'name':       f.name,
            'path_lower': f.path_lower
        } for f in files_and_folders.entries]

        # get column sizes for formatting
        max_len_id = max(len(f['id']) for f in file_list)
        max_len_name = max(len(f['name']) for f in file_list)
        max_len_path_lower = max(len(f['path_lower']) for f in file_list)
        for f in file_list:
            print('{:>{}} {:>{}} {:>{}}'.format(
                f['id'], max_len_id, f['name'], max_len_name, f['path_lower'], max_len_path_lower))

    def _load_config(self) -> ConfigParser:
        """Load `dbx-dl.ini` config file

        :return: ConfigParser
        """
        # By using `allow_no_value=True` we are allowed to
        # write `--force` instead of `--force=true` below.
        config = ConfigParser(allow_no_value=True)
        with open('{}/dbx-dl.ini'.format(self._base_path)) as f:
            config.read_file(f)

        return config


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dropbox Downloader')
    dd = DropboxDownloader()
    if arguments['download-recursive']:
        dd.dl()
    elif arguments.get('du'):
        dd.du(arguments['<path>'])
    elif arguments.get('ls'):
        dd.ls(arguments['<path>'])
