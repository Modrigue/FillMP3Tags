# Fill & Rename MP3 Tags

This repository contains scripts to manage MP3 files in a directory tree.

## fill_mp3_tags.py

Automatically fills the tags of MP3 files with the artist, track number, album name, year and cover image.

### Usage

MP3 directories must be formatted as follows:

_Artist/Album (Year)/Track number. Track name.mp3_

The album cover image must be a jpg or png file and be located in the album directory.

```bash
python fill_mp3_tags.py -d <directory>
```

## rename_mp3s_by_tracklist.py

Renames MP3 files based on a tracklist from a YouTube playlist. The tracklist file (`tracklist_from_youtube_playlist.txt`) must be present in each album folder.

The tracklist format expects:

- Track number on the first line of each entry
- Track name on the 5th line of each entry

Files are renamed to the format: `01. Track Name.mp3`

Already renamed files (matching the `XX.` pattern) are skipped.

### Usage

```bash
python rename_mp3s_by_tracklist.py -d <directory>
```

The script recursively processes all subdirectories matching the `Artist/Album (Year)/` structure.

### Prerequisites

```bash
pip install mutagen
```

### Parameters (both scripts)

- `-d`, `--dir <dir>`: root directory containing the `Artist/Album (Year)/` structure
- `-h`, `--help`: display help
