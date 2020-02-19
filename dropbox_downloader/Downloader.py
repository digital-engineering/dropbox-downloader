import os

from dropbox.files import FolderMetadata, FileMetadata
from pathlib import Path


class Downloader:
    """Recursively downloads folders and files from Dropbox"""

    def __init__(self, base_path, dbx, dl_dir, to_dl):
        self._base_path = base_path
        self._dbx = dbx
        self._dl_dir = dl_dir
        self._to_dl = to_dl

    def download_file(self, file: FileMetadata):
        """Download file, create parent folder if necessary, and write to `dl_dir`"""
        # check if file exists
        path_lower = file.path_lower
        local_path = '{}{}'.format(self._dl_dir, path_lower)
        if os.path.exists(local_path):
            # check size
            local_size = os.path.getsize(local_path)
            if local_size == file.size:
                print('File already exists: {}'.format(path_lower))
                return

        # dl file
        md, res = self._dbx.files_download(path_lower)
        data = res.content

        # make sure dir exists
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            print('Creating folder {}'.format(local_dir))
            Path(local_dir).mkdir(parents=True)

        # write file
        if not os.path.exists(local_path):
            print('Creating file {}'.format(local_path))
            with open(local_path, 'wb') as f:
                f.write(data)

    def download_recursive(self, path: str = ''):
        """Download all folders for path recursively

          - Get list of folder contents for `path`.
          - If it is a `FolderMetadata` (and optionally in `to_dl` list),
            recursively run `self.download_recursive(path)` with that path.
          - If it is a `FileMetadata`, download it

        :param path:str
        :return: void
        """
        files_and_folders = self.list_files_and_folders(path)
        for f in files_and_folders.entries:
            if path == '' and self._to_dl and f.name not in self._to_dl:
                return  # only download f.name in self._to_dl
            if isinstance(f, FolderMetadata):
                self.download_recursive(f.path_lower)
            elif isinstance(f, FileMetadata):
                self.download_file(f)
            else:
                raise RuntimeError(
                    'Unexpected folder entry: {}\nExpected types: FolderMetadata, FileMetadata'.format(f))

    def list_files_and_folders(self, path):
        """Wrapper around dbx.files_list_folder"""
        return self._dbx.files_list_folder(path)
