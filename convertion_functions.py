import pandas as pd
import os
import xml.etree.ElementTree as ET ## XML parsing
from collections import defaultdict
import numpy as np
from itunesLibrary import library

from urllib.parse import unquote
from convert_cover import loop_over_a_music_path
from convert_playlist import convert_playlists

import datetime

import pickle 

import parameters as param


def m3u8_to_csv(path_to_playlist,playlist_name):
    """_summary_

    Args:
        path_to_playlist (_type_): _description_
        playlist_name (_type_): _description_

    Returns:
        _type_: _description_
    """

    file1 = open(os.parth.join(path_to_playlist,playlist_name), 'r')
    count = 0
    
    # Using for loop
    print("Using for loop")
    duration_list = []
    title_list = []
    artist_list = []
    location_list = []  

    for line in file1:
    
        line_strip = line.strip()
        if line_strip.startswith('#EXTINF:'):

            line_strip = line_strip.replace('#EXTINF:','')       
            duration = line_strip.split(',')[0]
            line_strip = line_strip.replace(f'{duration},','')
            title = line_strip.split(' - ')[0] 
            artist = line_strip.split(' - ')[1] 

            count += 1
            print(duration,title,artist)
            duration_list.append(duration)
            title_list.append(title)
            artist_list.append(artist)
        elif not line_strip.startswith('#EXT'):
            location = line.strip()
            print(location.replace(' ','%20'))
            location_list.append(location)

    
    # Closing files
    file1.close()

    df = pd.DataFrame({'Artist' : artist_list, 
                       'Title' : title_list,
                       'Duration' : duration_list,
                       'Location' : location_list,
                       })
    
    df.loc[:,'Location'] = df.loc[:,'Location'].apply(lambda x : unquote(x)) 
    df.to_csv(os.parth.join(path_to_playlist,playlist_name.replace('m3u8','csv')))

    return df


def df_to_m3u8(df,file_name, path_to_m3u8_folder):
    """_summary_

    Args:
        df (_type_): _description_
        file_name (_type_): _description_
        path_to_m3u8_folder (_type_): _description_
    """

    if not file_name.endswith('.m3u8'):
        file_name+='.m3u8'
        
    f= open(os.path.join(path_to_m3u8_folder,file_name),"w+")
    f.write(f"#EXTM3U\r\n" )

    for i,row in df.iterrows():

        #try:
        total_time = row['Total Time']
        name = row['Name']
        artist = row['Artist']
        location = row['Location']

        f.write(f"#EXTINF:{round(int(total_time)/1000)} ,{name} - {artist}\r\n" )
        f.write(f"{location}\r\n".replace('%20', ' ') )
        #except:
        #    print(row)
    f.close()


            


def PL_to_m3u8(path_to_playlists_folder,
               playlist,):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        playlist (_type_): _description_

    Returns:
        _type_: _description_
    """
    file_name = f"{playlist.itunesAttributes['Name']}.m3u8"
    if file_name in os.listdir():
        file_name = f"{playlist.itunesAttributes['Name']} -  {playlist.itunesAttributes['Playlist ID']}.m3u"

    f= open(os.path.join(path_to_playlists_folder,file_name),"w+")
    f.write(f"#EXTM3U\r\n" )

    total_time_list = []
    name_list =[]
    artist_list = []
    location_list =[]

    for item in playlist.items:
        #try:
        try:
            total_time = item.itunesAttributes['Total Time']
        except:
            total_time = 0

        name = item.itunesAttributes['Name']
        try:
            artist = item.itunesAttributes['Artist']
        except:
            artist = None
        location = item.itunesAttributes['Location']

        total_time_list.append(total_time)
        name_list.append(name)
        artist_list.append(artist)
        location_list.append(location)

        f.write(f"#EXTINF:{round(int(total_time)/1000)} ,{name} - {artist}\r\n" )
        f.write(f"{location}\r\n".replace('%20', ' ') )
        #except:
        #    print(item)

    f.close()

    df = pd.DataFrame({'Artist' : artist_list, 
                       'Name' : name_list,
                       'Total Time' : total_time_list,
                       'Location' : location_list,
                       })
    df.loc[:,'Location'] = df.loc[:,'Location'].apply(lambda x : unquote(x)) 
    #df.to_csv(os.parth.join(path_to_playlist,playlist_name.replace('m3u8','csv')))
    return df