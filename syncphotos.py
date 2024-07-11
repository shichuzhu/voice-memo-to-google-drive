import os
from pathlib import Path
from typing import Tuple

ROOT_DRIVE = "c"
ROOT_RELPATH = "Users/shich/Desktop/tmp"

# TODO: This may not be true if iTools imports without specifying 'monthly'??????????????????????????????????
# Filename looks like 20240704_IMG_2250.MOV, whose prefix is added by iTools.
ITOOLSEXPORTEDPATH = (
    "itools/2024_07"  # <------ DOUBLE CHECK this path!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
)
ICLOUDCOPIEDPATH = "iphone"

# C:\Users\shich\Desktop\tmp\itools\2024_07 -- itool exported
# C:\Users\shich\Desktop\tmp\iphone -- icloud copied


def root_path() -> Path:
    if os.name == "nt":  # windows
        root_disk = Path(f"{ROOT_DRIVE}:")
    else:  # posix
        root_disk = Path(f"/mnt/{ROOT_DRIVE}")
    rel_path = ROOT_RELPATH.split("/")
    return Path(root_disk, *rel_path)


def itools_exported_path() -> Path:
    sections = ITOOLSEXPORTEDPATH.split("/")
    return Path(root_path(), *sections)


def icloud_copied_path() -> Path:
    sections = ICLOUDCOPIEDPATH.split("/")
    return Path(root_path(), *sections)


def get_all_files(directory):
    try:
        # Get all files in the directory
        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        return files
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_all_icloud_names_of_pic_and_movie(directory) -> Tuple[set, set]:
    files = get_all_files(directory)
    pic_names = set()
    mov_names = set()
    want_pic_exts = set([".heic", ".jpg", ".png"])
    for file in files:
        name, extension = os.path.splitext(file)
        if extension.lower() in want_pic_exts:
            pic_names.add(name)
        if extension.lower() == ".mov":
            mov_names.add(name)
    return pic_names, mov_names


def sync():
    files = get_all_files(itools_exported_path())
    pic_names, mov_names = get_all_icloud_names_of_pic_and_movie(icloud_copied_path())
    # PNG files are screenshots.
    check_exts = set([".mov", ".jpg", ".png"])
    for filename in files:
        name, extension = os.path.splitext(filename)
        ext = extension.lower()
        if ext not in check_exts:
            continue
        # TODO: This may not be true if iTools imports without specifying 'monthly'??????????????????????????????????
        # Filename looks like 20240704_IMG_2250.MOV, whose prefix is added by iTools.
        stripped_name = "_".join(name.split("_")[1:])
        path_to_remove = Path(root_path(), itools_exported_path(), filename)
        if ext == ".mov" and stripped_name in mov_names:
            print(f"[MOVIE] removing duplicate file {path_to_remove}")
            os.remove(path_to_remove)
        if (ext == ".jpg" or ext == ".png") and stripped_name in pic_names:
            print(f"[PIC  ] removing duplicate file {path_to_remove}")
            os.remove(path_to_remove)


def get_filenames_without_extensions(directory):
    filenames = []
    try:
        # List all files in the directory
        for filename in os.listdir(directory):
            # Get the file name without the extension
            name, _ = os.path.splitext(filename)
            filenames.append(name)
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return filenames


if __name__ == "__main__":
    """Consolidate photo files from iCloud and those imported via itools.

    If there's a XXX.jpg from itools exported, and there's a corresponding XXX.HEIC or XXX.jpg in iCloud,
    then the XXX.jpg should be deleted.

    If there's a XXX.mov from itools exported, and there's a corresponding XXX.mov in iCloud,
    then the XXX.mov should be deleted.

    Tested running on WSL.

    Workflow:
    1. From iCloud Photos, remove the files that we don't want to keep.
    2. Copy iCloud Photos to local directory A.
    3. Make sure the removal is sync'ed to iPhone.
    4. Import iPhone photos on to local directory B via iTools.
    5. Run this script to remove duplicate items in directory B.
    6. Copy contents in A to B.
    7. Copy merged contents in B to android phone to upload.
    """
    # Example usage
    sync()
