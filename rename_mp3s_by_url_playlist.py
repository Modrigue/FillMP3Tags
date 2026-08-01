#!/usr/bin/env python3
# -*-coding:utf-8 -*-

# Rename MP3 files based on track order from YouTube playlist.
# Format: "<track_number_with_2_digits>. <track_name>.mp3"
# Requires yt-dlp: pip install yt-dlp

import os
import sys
import getopt
import glob
import platform
import math
import subprocess
import json

# Files directory
ROOT_DIR = ""

# Detect operating system
IS_WINDOWS = platform.system() == 'Windows'


def main(argv):
    global ROOT_DIR

    try:
        opts, args = getopt.getopt(argv, "hd:p:", ["help", "dir=", "playlist="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    playlist_url = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit()
        elif opt in ("-d", "--dir"):
            ROOT_DIR = arg
        elif opt in ("-p", "--playlist"):
            playlist_url = arg

    if not ROOT_DIR:
        print('Error: directory is missing')
        printHelp()
        return

    renameMP3s(ROOT_DIR, playlist_url)


def renameMP3s(directory, playlist_url):
    # Check directory
    if not os.path.isdir(directory):
        print("ERROR: Directory", directory, "does not exist")
        return

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

            # Determine playlist URL for this album
            album_playlist_url = playlist_url
            if not album_playlist_url:
                # Look for playlist URL in first text file
                album_playlist_url = find_playlist_url_in_album(album_path)
                if not album_playlist_url:
                    print(f"Skipping {artist}/{album_folder}: no playlist URL found")
                    print()
                    continue

            print(f"Processing album: {artist}/{album_folder} ...")
            print(f"  Using playlist: {album_playlist_url}")
            
            # Get track order from YouTube playlist
            tracks = get_playlist_tracks(album_playlist_url)
            
            if not tracks:
                print(f"  ERROR: Could not fetch playlist or playlist is empty")
                print()
                continue

            rename_album_mp3s(album_path, tracks)
            print()


def find_playlist_url_in_album(album_path):
    """Look for YouTube playlist URL in the first text file in album folder"""
    for file in os.listdir(album_path):
        if file.lower().endswith('.txt'):
            txt_path = os.path.join(album_path, file)
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for YouTube playlist URL pattern
                    import re
                    url_pattern = r'https?://(?:www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+'
                    match = re.search(url_pattern, content)
                    if match:
                        return match.group(0)
            except Exception as e:
                print(f"  Warning: Could not read {file}: {e}")
    return None


def get_playlist_tracks(playlist_url):
    """Fetch track names from YouTube playlist using yt-dlp"""
    try:
        # Use yt-dlp to get playlist info as JSON
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--flat-playlist',
            playlist_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"Error running yt-dlp: {result.stderr}")
            return None
        
        # Parse JSON output (each line is a separate video entry)
        tracks = {}
        track_num = 1
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            try:
                video_data = json.loads(line)
                track_name = video_data.get('title', '')
                
                if track_name:
                    tracks[track_name] = track_num
                    track_num += 1
            except json.JSONDecodeError:
                continue
        
        return tracks
    
    except FileNotFoundError:
        print("ERROR: yt-dlp not found. Please install it with: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


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


def rename_album_mp3s(album_path, tracks):
    """Rename MP3 files in a single album folder"""
    import re
    
    all_mp3_files = glob.glob(os.path.join(album_path, "*.mp3"))
    
    # Filter out files already renamed with track number prefix (e.g., "1. ", "01. ", "001. ")
    mp3_files = [f for f in all_mp3_files if not re.match(r'^\d+\. ', os.path.basename(f))]
    
    # Count skipped files
    skipped_count = len(all_mp3_files) - len(mp3_files)
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} already-renamed file(s)")

    track_count = len(tracks)
    print(f"  Found {track_count} tracks in playlist")

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
    print('Usage: python rename_mp3s_by_youtube_playlist.py -d <directory> [-p <playlist_url>]')
    print()
    print("Options:")
    print("  -d, --dir <dir>:       root directory containing Artist/Album (Year)/Track structure")
    print("  -p, --playlist <url>:  YouTube playlist URL (optional)")
    print("                         If not provided, script will look for URL in album's .txt file")
    print("  -h, --help:            display help")
    print()
    print("Requirements:")
    print("  yt-dlp (install with: pip install yt-dlp)")
    print()


if __name__ == "__main__":
    main(sys.argv[1:])

    # Wait for user input to close program
    if IS_WINDOWS:
        os.system("pause")
    else:
        input("Press Enter to exit...")
