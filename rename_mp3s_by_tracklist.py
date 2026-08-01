#!/usr/bin/env python3
# -*-coding:utf-8 -*-

# Rename MP3 files based on tracklist from YouTube playlist.
# Format: "<track_number_with_2_digits>. <track_name>.mp3"

import os
import sys
import getopt
import glob
import platform
import math

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

    # Process each artist folder
    for artist in os.listdir(directory):
        artist_path = os.path.join(directory, artist)
        if not os.path.isdir(artist_path):
            continue

        # Process each album folder
        for album_folder in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album_folder)
            if not os.path.isdir(album_path):
                continue

            # get tracklist from the first .txt file found in the album folder
            tracklist_path = None
            for file in os.listdir(album_path):
                if file.lower().endswith('.txt'):
                    tracklist_path = os.path.join(album_path, file)
                    break

            if not tracklist_path:
                continue

            print(f"Processing album: {artist}/{album_folder} ...")
            rename_album_mp3s(album_path, tracklist_path)
            print()


def parse_tracklist(tracklist_path):
    """Parse tracklist file and return dict of {track_name: track_number}

    New format: duration on line (e.g., "5:07"), track name on next line.
    Track numbers are assigned sequentially based on order in file.
    Handles variable blank lines between entries.
    """
    tracks = {}
    track_num = 1

    with open(tracklist_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    # Process each entry in the tracklist
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line is a duration (format "X:XX" or "XX:XX")
        if ':' in line and i + 1 < len(lines):
            # Track name is on the next line
            track_name = lines[i + 1]

            # Validate: track name should not be metadata (empty, view counts, etc.)
            if track_name and not any(pattern in track_name.lower() for pattern in ["vues", "views", "il y a"]):
                tracks[track_name] = track_num
                track_num += 1
                # Move to next line and let the loop find the next duration
                i += 1
                continue

        i += 1

    return tracks


def find_matching_mp3(track_name, mp3_files):
    """Find MP3 file that matches the track name (case-insensitive, ignoring special chars)"""
    def normalize(s):
        return s.lower().replace("'", "").replace(" ", "").replace(".", "").replace(",", "")

    # Normalize track name
    normalized_track = normalize(track_name)

    # Find matching MP3 file
    for mp3_file in mp3_files:
        filename = os.path.splitext(os.path.basename(mp3_file))[0]
        normalized_file = normalize(filename)

        if normalized_file == normalized_track:
            return mp3_file

    return None


def sanitize_track_name(track_name):
    """Sanitize track name by removing forbidden filename characters.
    Slashes and backslashes are replaced with '-', other forbidden chars are removed.
    """
    # Replace slashes and backslashes with '-'
    sanitized = track_name.replace('/', '-').replace('\\', '-')
    
    # Remove other Windows forbidden characters: < > : " | ? *
    forbidden_chars = '<>:"|?*'
    for char in forbidden_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


def rename_album_mp3s(album_path, tracklist_path):
    """Rename MP3 files in a single album folder"""
    import re
    
    all_mp3_files = glob.glob(os.path.join(album_path, "*.mp3"))
    
    # Filter out files already renamed with track number prefix (e.g., "1. ", "01. ", "001. ")
    mp3_files = [f for f in all_mp3_files if not re.match(r'^\d+\. ', os.path.basename(f))]
    
    # Count skipped files
    skipped_count = len(all_mp3_files) - len(mp3_files)
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} already-renamed file(s)")

    # Parse tracklist
    tracks = parse_tracklist(tracklist_path)
    track_count = len(tracks)
    print(f"  Found {track_count} tracks in tracklist")

    # Calculate number of digits needed based on track count
    num_digits = int(math.log10(track_count)) + 1 if track_count > 0 else 1

    # Rename MP3 files
    renamed_count = 0
    for track_name, track_num in tracks.items():
        matching_file = find_matching_mp3(track_name, mp3_files)

        if matching_file:
            # Sanitize track name for valid filename
            safe_track_name = sanitize_track_name(track_name)
            # Format track number with dynamic digit count
            new_name = f"{track_num:0{num_digits}d}. {safe_track_name}.mp3"
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
