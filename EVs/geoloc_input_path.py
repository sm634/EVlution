import os
from sys import path


def add_data_path():
    """
    Description
    -----------
    function to enable importing from the preprocess_data subdirectory.

    Returns
    -------
    The path to the preprocess_data subdirectory
    """
    work_dir = os.getcwd()
    path_preprocess = os.path.join(work_dir, '..\\preprocess_data\\')
    parent_dir = os.path.join(work_dir, '..\\')
    path.extend(
        [
            path_preprocess,
            parent_dir
        ]
    )
    return path
