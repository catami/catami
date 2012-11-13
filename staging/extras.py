"""Contains extra functions that do not quite fit in other categories.
"""
from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache


def update_progress(key, percent):
    """Updates the percent for key."""
    cache.set(key, percent, 300)  # timeout in 30 seconds


class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        self.current_length = 0
        uuid = self.request.REQUEST.get('uuid')

        self.file_key = uuid + "_file_key"

        update_progress(self.file_key, 0)

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        if self.file_key:
            # tally up total downloaded
            self.current_length += self.chunk_size
            percent = int(float(100.0 * self.current_length) / float(self.content_length))
            update_progress(self.file_key, percent)
        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.cache_key:
            cache.delete(self.file_key)
