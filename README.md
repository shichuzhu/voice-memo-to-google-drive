# Export iPhone voice memo to Google Drive

## Requirements

1. A Windows PC. Optionally run in WSL.
2. Python >= 3.9 (for `pytz` to support named_tuple)
3. Install and setup iCloud on PC.
4. Install and setup Google Drive on PC.

## Steps

1. Export voice memos on the iPhone to iCloud. (Sliding selection to easily select all)
2. Run this python script `rename.py` to copy from iCloud to Google Drive.
3. Delete iCloud copies.
4. Delete voice memo copies on the iPhone.
