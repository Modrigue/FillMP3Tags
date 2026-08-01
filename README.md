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

Renames MP3 files based on a tracklist from a text file. The first `.txt` file found in each album folder is used as the tracklist.

The tracklist format expects:

- Duration on a line (e.g., "5:07" or "8:26")
- Track name on the next line
- Variable blank lines between entries are supported

Track numbers are assigned sequentially based on the order in the file.

Files are renamed to the format: `01. Track Name.mp3`

Already renamed files (matching the `XX.` pattern) are skipped.

### Usage

```bash
python rename_mp3s_by_tracklist.py -d <directory>
```

The script recursively processes all subdirectories matching the `Artist/Album (Year)/` structure.

## rename_mp3s_by_url_playlist.py

Renames MP3 files based on track order from an URL playlist. The script fetches the playlist track list and renames MP3 files accordingly.

The playlist URL can be provided in two ways:

1. **Command-line argument**: `-p <playlist_url>` (applies to all albums)
2. **Text file in album folder**: If no URL is provided, the script searches for a playlist URL in the first `.txt` file found in each album folder

Files are renamed to the format: `01. Track Name.mp3`

Already renamed files (matching the `XX.` pattern) are skipped.

### Usage

```bash
# With explicit playlist URL (applies to all albums)
python rename_mp3s_by_url_playlist.py -d <directory> -p <playlist_url>

# Without playlist URL (reads from album's .txt file)
python rename_mp3s_by_url_playlist.py -d <directory>
```

The script recursively processes all subdirectories matching the `Artist/Album (Year)/` structure.

### Prerequisites

```bash
pip install yt-dlp
```

### Parameters (all scripts)

- `-d`, `--dir <dir>`: root directory containing the `Artist/Album (Year)/` structure
- `-h`, `--help`: display help
- `-p`, `--playlist <url>`: URL of the playlist (for `rename_mp3s_by_url_playlist.py` only)
