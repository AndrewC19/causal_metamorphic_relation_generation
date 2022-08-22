"""A library of helper functions."""
import os


def safe_open_w(path):
    """Open path for writing and create directories if they do not exist.

    Original implementation: https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist
    Author: Jonathon Reinhart

    :param path: A path to the target directory. This may not exist yet.
    :return: An open path to be written to.
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")
