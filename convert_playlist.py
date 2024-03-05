# coding: utf-8

import os
import unicodedata

##########################
# EDIT THE 2 LINES BELOW #
##########################
iTunes_lib_path = 'file:///Volumes/MasterDD/Audios/Gros iTunes/'
path_to_playlists = '/Projects/itunes-lib-tlk/playlists/'
##########################
#                        #
##########################

walkman_lib_path = '/Volumes/MasterAudio/Audio/Gros iTunes/'

#the possible norms ar ‘NFC’, ‘NFKC’, ‘NFD’, and ‘NFKD’.
norm = 'NFC'

def convert_playlists(path_to_playlists,
                      destination_folder = 'Playlists_WM',
                      walkman_lib_path = '/Volumes/MasterAudio/Audio/Gros iTunes/'):

    if destination_folder not in os.listdir(path_to_playlists):
        os.mkdir(os.path.join(path_to_playlists,destination_folder))

    destination_path = os.path.join(path_to_playlists,destination_folder)

    files_list = [f for f in os.listdir(path_to_playlists) if (f.endswith('.m3u8')
                                             and not f.startswith('._'))]

    for file_name in files_list:
        print(file_name)

        playlist_file = open(os.path.join(path_to_playlists,file_name))
        lines = playlist_file.readlines()
        playlist_file.close()

        target_file_name = file_name
        f = open(os.path.join(destination_path,target_file_name), "w")

        for line in lines:
            line = line.replace(iTunes_lib_path, walkman_lib_path)
            f.write((unicodedata.normalize(norm, line).encode("utf-8")).decode("utf-8"))

        f.close()
