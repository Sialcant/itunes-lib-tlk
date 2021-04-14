# coding: utf-8

import os
import unicodedata
import sys

##########################
# EDIT THE 2 LINES BELOW #
##########################
iTunes_lib_path = '/Users/BenGast/Music/iTunes/iTunes Media/Music'
path_to_playlists = '/Users/BenGast/Desktop/Playlists'
##########################
#                        #
##########################

walkman_lib_path = ''

#the possible norms ar ‘NFC’, ‘NFKC’, ‘NFD’, and ‘NFKD’.
norm = 'NFC'

destination_path = path_to_playlists+'/Playlists_WM'
if 'Playlists_WM' not in os.listdir(path_to_playlists):
    os.mkdir(destination_path)



files_list = [f for f in os.listdir(path_to_playlists) if (f.endswith('.m3u8')
                                             and not f.startswith('._'))]

for file_name in files_list:

    playlist_file = open(path_to_playlists+'/'+file_name)
    lines = playlist_file.readlines()
    playlist_file.close()
    #print('*********** ', file_name)
    target_file_name = 'test_'+file_name#.split('.')[0]+walkman_suffix+norm+'.m3u8'
    f = open(destination_path+'/'+target_file_name, "w")

    for line in lines:
        line = line.replace(iTunes_lib_path, walkman_lib_path)
        #print(line.encode("utf-8"))
        #print(line.decode("utf-8", "strict"))
        #print(unicodedata.normalize(norm, line).encode("utf-8"))
        f.write((unicodedata.normalize(norm, line).encode("utf-8")).decode("utf-8"))

    f.close()
