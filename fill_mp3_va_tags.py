#!/usr/bin/env python3
# -*-coding:utf-8 -*-

# Fill MP3 tags for Various Artists compilations.
# Sets Artist to "Various Artists", Album to subdirectory name,
# and Title to "Artist - Song Name" (parsed from filename).
# Also embeds the first image found in the subdirectory as album art.

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

    fillVariousArtistsTags(ROOT_DIR)


def fillVariousArtistsTags(directory):
    # Check directory
    if not os.path.isdir(directory):
        print("ERROR: Directory", directory, "does not exist")
        return

    print("Processing Various Artists compilations in", directory, "...")
    print()

    # Check if directory contains MP3 files directly
    mp3_files = glob.glob(os.path.join(directory, "*.mp3"))
    
    if mp3_files:
        # Process this directory directly
        album_name = os.path.basename(directory)
        print(f"Processing album: {album_name} ...")
        process_album(directory, album_name)
        print()
    else:
        # Process each subdirectory (album)
        for album_folder in os.listdir(directory):
            album_path = os.path.join(directory, album_folder)
            if not os.path.isdir(album_path):
                continue

            print(f"Processing album: {album_folder} ...")
            process_album(album_path, album_folder)
            print()


def process_album(album_path, album_name):
    """Process a single album folder"""
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TPE1, TALB, TIT2, APIC
    import mimetypes

    # Find first image file in the album folder
    image_path = find_first_image(album_path)
    if image_path:
        print(f"  Found album art: {os.path.basename(image_path)}")
    else:
        print(f"  No album art found")

    # Get all MP3 files
    mp3_files = glob.glob(os.path.join(album_path, "*.mp3"))
    
    if not mp3_files:
        print(f"  No MP3 files found")
        return

    print(f"  Found {len(mp3_files)} MP3 files")

    # Process each MP3 file
    updated_count = 0
    for mp3_file in mp3_files:
        try:
            # Parse filename to get artist and title
            filename = os.path.basename(mp3_file)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Expected format: "Artist - Title.mp3"
            if " - " not in name_without_ext:
                print(f"  Warning: Skipping {filename} (does not match 'Artist - Title' format)")
                continue
            
            parts = name_without_ext.split(" - ", 1)
            artist = parts[0].strip()
            title = name_without_ext  # Keep full "Artist - Title" as title
            
            # Load MP3 file
            audio = MP3(mp3_file, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Set Artist to "Various Artists"
            audio.tags['TPE1'] = TPE1(encoding=3, text="Various Artists")
            
            # Set Album to folder name
            audio.tags['TALB'] = TALB(encoding=3, text=album_name)
            
            # Set Title to "Artist - Song Name"
            audio.tags['TIT2'] = TIT2(encoding=3, text=title)
            
            # Add album art if image found
            if image_path:
                # Remove existing APIC frames
                audio.tags.delall('APIC')
                
                # Determine MIME type
                mime_type = mimetypes.guess_type(image_path)[0]
                if mime_type is None:
                    # Default to jpeg if unknown
                    mime_type = 'image/jpeg'
                
                # Read image data
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                # Add APIC frame
                audio.tags['APIC'] = APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,  # Cover front
                    desc='Cover',
                    data=img_data
                )
            
            # Save changes
            audio.save()
            print(f"  Updated: {filename}")
            updated_count += 1
            
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"  Done! Updated {updated_count} files.")


def find_first_image(directory):
    """Find the first image file in the directory"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                return file_path
    
    return None


def printHelp():
    print()
    print('Usage: python fill_various_artists_tags.py -d <directory>')
    print()
    print("Options:")
    print("  -d, --dir <dir>:  root directory containing Various Artists subdirectories")
    print("  -h, --help:       display help")
    print()
    print("Description:")
    print("  This script processes MP3 files in Various Artists compilations.")
    print("  For each MP3 file, it sets:")
    print("    - Artist: 'Various Artists'")
    print("    - Album: subdirectory name")
    print("    - Title: 'Artist - Song Name' (parsed from filename)")
    print("  It also embeds the first image found in the subdirectory as album art.")
    print()
    print("Requirements:")
    print("  mutagen (install with: pip install mutagen)")
    print()


if __name__ == "__main__":
    main(sys.argv[1:])

    # Wait for user input to close program
    if IS_WINDOWS:
        os.system("pause")
    else:
        input("Press Enter to exit...")
