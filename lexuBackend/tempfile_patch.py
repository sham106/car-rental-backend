import os
import tempfile

"""
Patch for Django TemporaryFile on Windows.
This prevents PermissionError: [WinError 32] when handling file uploads.
"""

def _patch_tempfile():
    if os.name != 'nt':
        return

    # Only patch if we haven't already
    if hasattr(tempfile, 'NamedTemporaryFile_original'):
        return

    tempfile.NamedTemporaryFile_original = tempfile.NamedTemporaryFile

    def NamedTemporaryFile(*args, **kwargs):
        # On Windows, the default delete=True causes permission errors
        # when the file is opened multiple times (which Django does).
        # We force delete=False to avoid this lock.
        if 'delete' in kwargs:
            kwargs['delete'] = False
        return tempfile.NamedTemporaryFile_original(*args, **kwargs)

    tempfile.NamedTemporaryFile = NamedTemporaryFile
