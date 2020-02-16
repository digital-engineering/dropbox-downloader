from dropbox.files import FileMetadata, FolderMetadata


class DiskUsage:
    def __init__(self, dbx):
        self._dbx = dbx
        self.size = 0

    def du(self, path=''):
        """Get total size of given path by recursing through all subfolders, similar to linux `du` command."""
        self._du_sum_recursive(path)
        print(f'{path}: {self.size} bytes ({self.size / 10 ** 9:0.2f} GB)')

    def _du_sum_recursive(self, path):
        files_and_folders = self._dbx.files_list_folder(path)
        for f in files_and_folders.entries:
            if isinstance(f, FolderMetadata):
                self._du_sum_recursive(f.path_lower)
            elif isinstance(f, FileMetadata):
                self.size += f.size
            else:
                raise RuntimeError(f'Unexpected folder entry: {f}\nExpected types: FolderMetadata, FileMetadata')
