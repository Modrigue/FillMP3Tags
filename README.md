# Fill MP3 Tags

This script automatically fills the tags of MP3 files in a directory tree with the artist, track number, album name, year and cover image.

## Usage

MP3 directories must be formatted as follows:

_Artist/Album [Year]/Track number. Track name.mp3_

The album cover image must be a jpg or png file and be located in the album directory.

```bash
python fill_mp3_tags.py -d <directory>
```

## Prerequisites

```bash
pip install mutagen
```

## Parameters

- `-d`, `--dir <dir>`: root directory containing the `Artist/Album [Year]/Track.mp3` structure
- `-h`, `--help`: display help
