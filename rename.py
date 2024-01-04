import os
import shutil

import pytz
from pathlib import Path
from ffprobe import FFProbe


# from path: D:\data\icloud\iCloudDrive\VoiceMemoBackup
ICLOUD_DRIVE = "d"
ICLOUD_RELPATH = "data/icloud/iCloudDrive/VoiceMemoBackup"

# to path root: G:\My Drive\Recordings
GOOGLE_DRIVE = "g"
GDRIVE_RELPATH = "My Drive/Recordings"


def from_path() -> Path:
    if os.name == "nt":  # windows
        root_disk = Path(f"{ICLOUD_DRIVE}:")
    else:  # posix
        root_disk = Path(f"/mnt/{ICLOUD_DRIVE}")
    rel_path = ICLOUD_RELPATH.split("/")
    return Path(root_disk, *rel_path)


def to_path_root() -> Path:
    if os.name == "nt":  # windows
        root_disk = Path(f"{GOOGLE_DRIVE}:")
    else:  # posix
        root_disk = Path(f"/mnt/{GOOGLE_DRIVE}")
    rel_path = GDRIVE_RELPATH.split("/")
    return Path(root_disk, *rel_path)


def to_path(year, week):
    return Path(to_path_root(), f"{year}", f"W{week}")


def move_files(dir_path: Path):
    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        rename_via_metadata(f)


def rename_via_metadata(src_path: Path):
    metadata = FFProbe(str(src_path))
    iso_time = metadata.metadata["creation_time"]
    read_fmt = "%Y-%m-%dT%H:%M:%S.%f%z"
    utc_time = pytz.datetime.datetime.strptime(iso_time, read_fmt)
    east_tz = pytz.timezone("America/New_York")
    east_time = utc_time.astimezone(east_tz)
    new_fmt = "%Y-%m-%d_D%wT_%H-%M-%S"
    new_filename = east_time.strftime(new_fmt)
    year = east_time.isocalendar().year
    week_number = east_time.isocalendar().week
    dst_path = Path(to_path(year, week_number), f"{new_filename} {src_path.name}")
    assert src_path.is_file()
    assert not dst_path.is_file()  # Expect the file is not already there.
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"     moving {src_path} -> {dst_path}")
    shutil.copy(src_path, dst_path)
    src_path.unlink()  # Delete the iCloud copy.
    print(f"DONE moving {src_path} -> {dst_path}")


if __name__ == "__main__":
    """Rename files from iCloud backup to Google Drive.

    The files will be named as "${year}/${week}/${media creation EST time} $(original name)"

    Steps:
    1. Export voice memos on the iPhone to iCloud. (Sliding selection to easily select all)
    2. Run this script to copy from iCloud to Google Drive.
    3. Delete iCloud copies.
    4. Delete voice memo copies on the iPhone.

    Tested running on WSL.
    """
    move_files(from_path())
