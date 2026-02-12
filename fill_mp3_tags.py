#!/usr/bin/env python3
# -*-coding:utf-8 -*-

# Fills MP3 tags from directory structure and filenames

import os
import platform
import re
import sys, getopt
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, TRCK, APIC, error

# Files directory (replace '\' with '/')
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

    fillMP3Tags(ROOT_DIR)


def fillMP3Tags(directory):

    # Check directory
    if not os.path.isdir(directory):
        print("ERROR: Directory", directory, "does not exist")
        return

    print("Filling MP3 tags in", directory, "...")
    print()

    for artist in os.listdir(directory):
        artist_path = os.path.join(directory, artist)
        if not os.path.isdir(artist_path): continue

        for album_folder in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album_folder)
            if not os.path.isdir(album_path): continue

            # --- Year Extraction Logic ---
            # Searches for any 4-digit number (19xx or 20xx) in the folder name
            year_match = re.search(r'(19|20)\d{2}', album_folder)
            year = year_match.group(0) if year_match else None

            # Clean Album Name (optional: removes the year from the tag if you want)
            # e.g., "Greatest Hits (2024)" becomes just "Greatest Hits"
            album_name = re.sub(r'[\(\[\s]*(19|20)\d{2}[\)\]\s]*', '', album_folder).strip()

            print(f"Processing album: {artist}/{album_name} [{year or 'No Year'}]...")

            # --- Image Handling ---
            cover_data = None
            mime_type = None
            for file in os.listdir(album_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"Found cover: {artist}/{album_name} [{year or 'No Year'}]/{file}")
                    with open(os.path.join(album_path, file), 'rb') as f:
                        cover_data = f.read()
                    mime_type = 'image/png' if file.lower().endswith('.png') else 'image/jpeg'
                    break

            # --- File Tagging ---
            for filename in os.listdir(album_path):
                if filename.lower().endswith('.mp3'):
                    file_path = os.path.join(album_path, filename)

                    try:
                        # Splits "01. Song Name" into ["01", "Song Name"]
                        track_part, title_part = filename.replace('.mp3', '').split('. ', 1)
                    except ValueError:
                        continue

                    audio = MP3(file_path, ID3=ID3)
                    try:
                        audio.add_tags()
                    except error:
                        pass

                    # Apply Tags
                    audio.tags.add(TPE1(encoding=3, text=artist))
                    audio.tags.add(TALB(encoding=3, text=album_name))
                    audio.tags.add(TRCK(encoding=3, text=track_part))
                    audio.tags.add(TIT2(encoding=3, text=title_part))

                    if year:
                        audio.tags.add(TYER(encoding=3, text=year))

                    if cover_data:
                        audio.tags.add(APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=cover_data))

                    # Save with ID3 v2.3
                    audio.save(v2_version=3)
                    print(f"Processed: {artist}/{album_name} [{year or 'No Year'}]/{title_part}.mp3")


def printHelp():
    print()
    print('Usage: python fill_mp3_tags.py -d <directory>')
    print()
    print("Options:")
    print("  -d, --dir <dir>:  root directory containing Artist/Album/Track structure")
    print("  -h, --help:       display help")
    print()


if __name__ == "__main__":
    main(sys.argv[1:])

    # Wait for user input to close program
    if IS_WINDOWS:
        os.system("pause")
    else:
        input("Press Enter to exit...")