# music-lib-tlk
To contain python scripts to convert music library meta-data from iTunes to Walkman.

This project currently contains 2 scripts:

## I. convert_playlist.py

### 1 - What this script is doing: 
Convert m3u8 playlists exported by iTunes to a format that can be read by a Sony Walkman

### 2 -  How to run the script:

i: Download the code from GitHub
ii: In iTunes export your playlists using the format "m3u8".
iii: Edit lines 10 and 11 inside 'convert_playlist.py' using a text editor. 

* Line 10 is the path to the iTunes library used to create "m3u8" files.
* Line 11 is the path to tge directory containint the  "m3u8" files.

iv: open a terminal window and navigate to your 'music-lib-tlk' directrory.
v: run the script using the command: 'python3 convert_playlist.py'
vi: your formated playlists are now containted in a 'Playlists_WM' directory located inside your playlist directory


## II. convert_cover.py

### 1 - What this script is doing: 

Finding all the music files contain in a folder and extract/convert the cover art image contained in the metadata of the music files.

### 2 -  Warning:
* This scripts assume that the music is organised by artist_album/album
* This script is modifying all the cover art of the music files contained in the given directory. Please don't blame me if all cover arts are messed up afterwards... I suggest to try to run it first inside a directory containing a sample of test files.

### 3 -  How to run the script:

i: Download the code from GitHub
ii: Edit lines 14 to 18 inside inside 'convert_cover.py' using a text editor. 

* Line 14 is the path to the music library you want to exctract/convert cover art. This can we the path to the music folder of a Walkman.
* Line 15 if 'create_cover_jpg = True', a 'cover.jpg' file is created inisde each album directory if a cover is present in the metadat of 1 of the songs of the album.
* Line 16 if 'create_album_jpg = True', a 'album.jpg' file is created inisde each album directory if a cover is present in the metadat of 1 of the songs of the album.
* Line 17 if complete_missing_cover_art = True, the first cover art found inside the metadata of an album is assigned to all the songs without cover in there metadata.
* Line 18 if convert_to_non_prog = True all the cover art are converted to non-progressive jpg.

iv: open a terminal window and navigate to your 'music-lib-tlk' directrory.
v: run the script using the command: 'python3 convert_cover.py'. 
vi: The code is relatively long to run so be patient! Count ~0.5 second per track for a modern computer.
vii: The terminal will show the list of album path for which no cover art has been found.
