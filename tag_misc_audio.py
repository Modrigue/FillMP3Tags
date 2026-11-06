#!/usr/bin/env python3
"""
Tag Misc Audio Files - Tag audio files from artists directory.

Parses audio files in the format: <Artist>/<Artist> - <Song>.mp3
Renames to: <Song>.mp3
Tags with: Artist: <Artist>, Title: <Song>
For collaborations (Artist1 & Artist2 - Song.mp3):
  - Artist tag: Artist1 & Artist2
  - Album Artist tag: Artist1 (from subdirectory name)
Supports MP3, OGG, OPUS, AAC, and M4A formats.
"""

import os
import re
import sys
import shutil
from pathlib import Path

try:
    from mutagen import File
    from mutagen.id3 import ID3, TPE1, TIT2, TPE2, ID3NoHeaderError
    from mutagen.easyid3 import EasyID3
except ImportError:
    print("Error: mutagen library is required. Install it with: pip install mutagen")
    exit(1)

try:
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    OggVorbis = None

try:
    from mutagen.oggopus import OggOpus
except ImportError:
    OggOpus = None

try:
    from mutagen.aac import AAC
except ImportError:
    AAC = None

try:
    from mutagen.mp4 import MP4
except ImportError:
    MP4 = None


def set_tags(file_path, artist, title, album_artist=None):
    """
    Set metadata tags for an audio file.

    Args:
        file_path: Path to the audio file
        artist: Artist name (can be multiple artists with &)
        title: Song title
        album_artist: Album artist (optional, used for collaborations)
    """
    try:
        # Try easy mode first
        audio = File(file_path, easy=True)

        if audio is None:
            # If easy mode fails, try format-specific handling
            ext = file_path.suffix.lower()

            if ext == '.mp3':
                # For MP3, try using ID3 directly
                try:
                    audio = EasyID3(file_path)
                except:
                    # If file has no ID3 tags, create them
                    try:
                        audio = ID3(file_path)
                    except ID3NoHeaderError:
                        audio = ID3()
                        audio.save(file_path)
                        audio = EasyID3(file_path)
            elif ext == '.ogg' and OggVorbis:
                audio = OggVorbis(file_path)
            elif ext == '.opus' and OggOpus:
                audio = OggOpus(file_path)
            elif ext == '.aac' and AAC:
                audio = AAC(file_path)
            elif ext == '.m4a' and MP4:
                audio = MP4(file_path)
            else:
                print(f"  Error: Unsupported format or could not open file")
                return False

        if audio is None:
            print(f"  Error: Could not open file for tagging")
            return False

        # Set Artist and Title tags
        audio['artist'] = artist
        audio['title'] = title

        # Set Album Artist if provided (for collaborations)
        if album_artist:
            audio['albumartist'] = album_artist

        audio.save()
        return True

    except Exception as e:
        print(f"  Error setting tags: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_artist_and_song(filename):
    """
    Extract artist and song name from filename.
    Expected format: <Artist> - <Song>.mp3
    Returns: (artist, song) or (None, None) if pattern doesn't match
    """
    # Remove extension
    name_without_ext = re.sub(r'\.(mp3|ogg|opus|aac|m4a)$', '', filename, flags=re.IGNORECASE)
    
    # Match pattern: "Artist - Song"
    match = re.match(r'^(.+?)\s*-\s*(.+)$', name_without_ext)
    if match:
        artist = match.group(1).strip()
        song = match.group(2).strip()
        return artist, song
    
    return None, None


def process_artist_directory(source_dir):
    """
    Process a single artist directory - rename and tag files in place.

    Args:
        source_dir: Path to the artist directory
    """
    source_path = Path(source_dir)
    artist_name = source_path.name

    print(f"\nProcessing artist: {artist_name}")
    print("=" * 60)

    # Find all audio files
    audio_extensions = ['*.mp3', '*.ogg', '*.opus', '*.aac', '*.m4a']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(source_path.glob(ext))

    if not audio_files:
        print(f"  No audio files found in {source_dir}")
        return

    print(f"  Found {len(audio_files)} audio files")

    processed_count = 0
    skipped_count = 0
    error_count = 0

    for audio_file in audio_files:
        print(f"\n  File: {audio_file.name}")

        # Extract artist and song from filename
        file_artist, song_name = extract_artist_and_song(audio_file.name)

        if not file_artist or not song_name:
            print(f"    Skipped: Filename doesn't match expected format '<Artist> - <Song>.mp3'")
            skipped_count += 1
            continue

        # Determine if this is a collaboration (contains & in artist from filename)
        if '&' in file_artist:
            # File has "Artist1 & Artist2 - Song"
            # Artist tag: Artist1 & Artist2
            # Album Artist tag: artist_name (from subdirectory)
            tag_artist = file_artist
            album_artist = artist_name
            print(f"    Collaboration detected")
            print(f"    Artist tag: {tag_artist}")
            print(f"    Album Artist tag: {album_artist}")
        else:
            # Simple case: artist matches directory name
            tag_artist = artist_name
            album_artist = None
            print(f"    Artist tag: {tag_artist}")

        print(f"    Title tag: {song_name}")

        # New filename: <Song>.mp3
        new_filename = song_name + audio_file.suffix
        new_file_path = source_path / new_filename

        print(f"    New filename: {new_filename}")

        # Handle duplicate filenames
        counter = 1
        while new_file_path.exists():
            base_name = song_name
            new_filename = f"{base_name}_{counter}{audio_file.suffix}"
            new_file_path = source_path / new_filename
            counter += 1
            print(f"    Duplicate detected, trying: {new_filename}")

        # Rename file in place
        try:
            audio_file.rename(new_file_path)
            print(f"    Renamed to: {new_filename}")
        except Exception as e:
            print(f"    Error renaming file: {e}")
            error_count += 1
            continue

        # Set tags on the renamed file
        if set_tags(new_file_path, tag_artist, song_name, album_artist):
            print(f"    Tags set successfully")
            processed_count += 1
        else:
            print(f"    Error setting tags")
            error_count += 1

    print(f"\n  Summary for {artist_name}:")
    print(f"    Processed: {processed_count}")
    print(f"    Skipped: {skipped_count}")
    print(f"    Errors: {error_count}")


def process_audio_directory(source_dir):
    """
    Process all artist subdirectories in the source directory.

    Args:
        source_dir: Path to the artist directory
    """
    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist")
        return

    if not source_path.is_dir():
        print(f"Error: '{source_dir}' is not a directory")
        return

    # Find all subdirectories (artist directories)
    artist_dirs = [d for d in source_path.iterdir() if d.is_dir()]

    if not artist_dirs:
        print(f"No subdirectories found in '{source_dir}'")
        return

    print(f"Found {len(artist_dirs)} artist directories in {source_dir}")
    print("=" * 60)

    total_processed = 0
    total_skipped = 0
    total_errors = 0

    for artist_dir in sorted(artist_dirs):
        # Process each artist directory
        # We need to track counts per directory, so we'll collect them
        old_stdout = sys.stdout
        import io
        captured_output = io.StringIO()
        sys.stdout = captured_output

        process_artist_directory(artist_dir)

        sys.stdout = old_stdout
        output = captured_output.getvalue()
        print(output)

        # Parse summary from output
        if "Summary for" in output:
            lines = output.split('\n')
            for line in lines:
                if "Processed:" in line:
                    total_processed += int(line.split(':')[1].strip())
                elif "Skipped:" in line:
                    total_skipped += int(line.split(':')[1].strip())
                elif "Errors:" in line:
                    total_errors += int(line.split(':')[1].strip())

    print("\n" + "=" * 60)
    print("Overall Summary:")
    print(f"  Total processed: {total_processed}")
    print(f"  Total skipped: {total_skipped}")
    print(f"  Total errors: {total_errors}")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tag_misc_audio.py <source_directory>")
        print("\nArguments:")
        print("  source_directory  Path to the artists directory")
        print("\nExample:")
        print('  python tag_misc_audio.py "D:/PATH/TO/ARTISTS"')
        sys.exit(1)

    source_dir = sys.argv[1]

    print("Misc audio File Tagger")
    print("=" * 60)
    print(f"Source directory: {source_dir}")
    print("Files will be renamed and tagged in place")
    print("=" * 60)

    process_audio_directory(source_dir)


if __name__ == "__main__":
    main()
