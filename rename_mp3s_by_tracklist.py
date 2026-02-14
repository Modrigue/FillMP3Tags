#!/usr/bin/env python3
# -*-coding:utf-8 -*-

# Rename MP3 files based on tracklist from YouTube playlist.
# Format: "<track_number_with_2_digits>. <track_name>.mp3"

import os
import sys
import getopt
import glob
import platform

# Files directory
ROOT_DIR = ""

# Detect operating system
IS_WINDOWS = platform.system() == 'Windows'


def main(argv):
    global ROOT_DIR

    try:
        opts, args = getopt.getopt(argv, "hd:", ["help", "dir="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit()
        elif opt in ("-d", "--dir"):
            ROOT_DIR = arg

    if not ROOT_DIR:
        print('Error: directory is missing')
        printHelp()
        return

    renameMP3s(ROOT_DIR)


def renameMP3s(directory):
    # Check directory
    if not os.path.isdir(directory):
        print("ERROR: Directory", directory, "does not exist")
        return

    print("Renaming MP3 files in", directory, "...")
    print()

    for artist in os.listdir(directory):
        artist_path = os.path.join(directory, artist)
        if not os.path.isdir(artist_path):
            continue

        for album_folder in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album_folder)
            if not os.path.isdir(album_path):
                continue

            tracklist_path = os.path.join(album_path, "tracklist_from_youtube_playlist.txt")

            if not os.path.exists(tracklist_path):
                continue

            print(f"Processing album: {artist}/{album_folder} ...")
            rename_album_mp3s(album_path, tracklist_path)
            print()


def parse_tracklist(tracklist_path):
    """Parse tracklist file and return dict of {track_name: track_number}

    Track number is on line 1, track name is on line 5 of each entry.
    """
    tracks = {}

    with open(tracklist_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line is a track number
        if line.isdigit() and i + 4 < len(lines):
            track_num = int(line)
            track_name = lines[i + 4]

            # Validate: track name should not be metadata (empty, view counts, etc.)
            if track_name and not any(pattern in track_name.lower() for pattern in ["vues", "views", "il y a"]):
                tracks[track_name] = track_num
                i += 9  # Skip to next entry (9 lines per entry including blank line)
                continue

        i += 1

    return tracks


def find_matching_mp3(track_name, mp3_files):
    """Find MP3 file that matches the track name (case-insensitive, ignoring special chars)"""
    def normalize(s):
        return s.lower().replace("'", "").replace(" ", "").replace(".", "").replace(",", "")

    normalized_track = normalize(track_name)

    for mp3_file in mp3_files:
        filename = os.path.splitext(os.path.basename(mp3_file))[0]
        normalized_file = normalize(filename)

        if normalized_file == normalized_track:
            return mp3_file

    return None


def rename_album_mp3s(album_path, tracklist_path):
    """Rename MP3 files in a single album folder"""
    import re
    
    all_mp3_files = glob.glob(os.path.join(album_path, "*.mp3"))
    
    # Filter out files already renamed with track number prefix (e.g., "01. ", "02. ")
    mp3_files = [f for f in all_mp3_files if not re.match(r'^\d{2}\. ', os.path.basename(f))]
    
    skipped_count = len(all_mp3_files) - len(mp3_files)
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} already-renamed file(s)")

    tracks = parse_tracklist(tracklist_path)
    print(f"  Found {len(tracks)} tracks in tracklist")

    renamed_count = 0
    for track_name, track_num in tracks.items():
        matching_file = find_matching_mp3(track_name, mp3_files)

        if matching_file:
            new_name = f"{track_num:02d}. {track_name}.mp3"
            new_path = os.path.join(album_path, new_name)

            if os.path.exists(new_path) and new_path != matching_file:
                print(f"  Warning: {new_name} already exists, skipping")
                continue

            try:
                os.rename(matching_file, new_path)
                print(f"  Renamed: {os.path.basename(matching_file)} -> {new_name}")
                renamed_count += 1
            except OSError as e:
                print(f"  Error renaming {os.path.basename(matching_file)}: {e}")
        else:
            print(f"  Warning: No matching MP3 file found for '{track_name}'")

    print(f"  Done! Renamed {renamed_count} files.")


def printHelp():
    print()
    print('Usage: python rename_mp3s_by_tracklist.py -d <directory>')
    print()
    print("Options:")
    print("  -d, --dir <dir>:  root directory containing Artist/Album (Year)/Track structure")
    print("  -h, --help:       display help")
    print()


if __name__ == "__main__":
    main(sys.argv[1:])

    # Wait for user input to close program
    if IS_WINDOWS:
        os.system("pause")
    else:
        input("Press Enter to exit...")
