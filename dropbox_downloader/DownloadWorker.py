from threading import Thread
from queue import Queue

from dropbox_downloader.Downloader import Downloader


class DownloadWorker(Thread):
    """Threaded worker to download files and folders using Downloader"""

    def __init__(self, downloader: Downloader, queue: Queue):
        Thread.__init__(self)
        self.downloader = downloader
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            path = self.queue.get()
            try:
                self.downloader.download_recursive(path)
            finally:
                self.queue.task_done()
