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

Renames MP3 files based on track order from a playlist URL. The script fetches the playlist track list using `yt-dlp` and renames MP3 files accordingly.

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

## fill_mp3_va_tags.py

Fills MP3 tags for Various Artists styles compilations. The script sets the following tags:

- **Artist**: "Various Artists"
- **Album**: style subdirectory name (or directory name if processing directly)
- **Title**: "Artist - Song Name" (parsed from filename)
- **Album Art**: embeds the first image found in the directory as cover art

The script can process either:
- A directory containing MP3 files directly
- A parent directory with multiple subdirectories (each subdirectory is treated as a style)

### Usage

```bash
# Process a single genre directory
python fill_mp3_va_tags.py -d "C:\Music\Various Artists\Rock"

# Process parent directory with multiple genres subdirectories
python fill_mp3_va_tags.py -d "C:\Music\Various Artists"
```

### Filename Format

MP3 files must follow the format: `Artist - Song Name.mp3`

## tag_misc_audio.py

Tags and renames audio files from artist directories. The script processes audio files in the format: `<Artist>/<Artist> - <Song>.mp3` and:

- Renames files to: `<Song>.mp3`
- Sets tags: Artist tag, Title tag
- For collaborations (e.g., `Artist1, Artist2 & Artist3 - Song.mp3` or `Artist1 ft. Artist2 - Song.mp3`):
  - Artist tag: All artists from filename (e.g., `Artist1, Artist2 & Artist3`)
  - Album Artist tag: First artist from filename (e.g., `Artist1`)
- Supports MP3, OGG, OPUS, AAC, and M4A formats

### Usage

```bash
python tag_misc_audio.py <source_directory>
```

The script processes all artist subdirectories in the source directory, renaming and tagging files in place.

### Prerequisites (all scripts)

```bash
pip install mutagen
pip install yt-dlp
```

### Parameters (all scripts)

- `-d`, `--dir <dir>`: root directory containing the `Artist/Album (Year)/` structure
- `-h`, `--help`: display help
- `-p`, `--playlist <url>`: playlist URL (for `rename_mp3s_by_url_playlist.py` only)
