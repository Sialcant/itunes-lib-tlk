import pandas as pd
import os
import xml.etree.ElementTree as ET ## XML parsing
from collections import defaultdict
import numpy as np
from itunesLibrary import library

import pickle 


important_cols = ['Track ID', 'Name', 'Artist', 'Album Artist',
       'Album', 'Genre', 'Kind', 'Size', 'Total Time', 'Disc Number',
       'Disc Count', 'Track Number', 'Track Count', 
        'File Type', 
        'Location','Scoring']


def PL_to_m3u8(path_to_lib,playlist):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        playlist (_type_): _description_

    Returns:
        _type_: _description_
    """
    file_name = f"{playlist.itunesAttributes['Name']}.m3u8"
    if file_name in os.listdir():
        file_name = f"{playlist.itunesAttributes['Name']} -  {playlist.itunesAttributes['Playlist ID']}.m3u"

    path_to_pl = os.path.join(path_to_lib,'Playlists')

    if 'Playlists' not in os.listdir(path_to_lib):
        os.mkdir(path_to_pl)
        

    f= open(os.path.join(path_to_pl,file_name),"w+")
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
    #df.to_csv(os.parth.join(path_to_playlist,playlist_name.replace('m3u8','csv')))
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
    df.to_csv(os.parth.join(path_to_playlist,playlist_name.replace('m3u8','csv')))
    return df


def convert_lib_to_csv(path_to_lib_folder,lib_name):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        lib_name (_type_): _description_

    Returns:
        _type_: _description_
    """

    tree = ET.parse(os.path.join(path_to_lib_folder,lib_name))
    root = tree.getroot()

    columns = sorted(list(set([root[0][17][i][j].text for i, _ in enumerate(root[0][17]) 
                           for j, _ in enumerate(root[0][17][i]) if root[0][17][i][j].tag == 'key'])))

    data = defaultdict(list)
    bool_columns = ['Album Loved', 'Apple Music',
                    'Clean', 'Compilation',
                    'Explicit', 'HD',
                    'Has Video', 'Loved',
                    'Matched', 'Music Video', 
                    'Part Of Gapless Album', 
                    'Playlist Only']

    for i, _ in enumerate(root[0][17]):
        temp_columns = list.copy(columns)
        if i % 2 == 1:
            for j, _ in enumerate(root[0][17][i]):
                if root[0][17][i][j].tag == 'key':
                    if root[0][17][i][j].text in bool_columns:
                        data[root[0][17][i][j].text].append(root[0][17][i][j+1].tag)
                        temp_columns.remove(root[0][17][i][j].text)
                    else:
                        data[root[0][17][i][j].text].append(root[0][17][i][j+1].text)
                        temp_columns.remove(root[0][17][i][j].text)
            for column in temp_columns:
                data[column].append(np.nan)
    df = pd.DataFrame(data)

    numeric_columns = ['Artwork Count', 'Bit Rate', 'Disc Count', 'Disc Number', 
                       'Movement Count', 'Movement Number', 'Play Count', 'Play Date', 
                       'Sample Rate', 'Size', 'Skip Count', 'Track Count', 'Track ID', 'Track Number', 'Year']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

    date_columns = ['Date Added', 'Date Modified', 'Play Date UTC', 'Release Date', 'Skip Date']

    df[date_columns] = df[date_columns].apply(pd.to_datetime)

    df['Play Date'] = pd.to_datetime(df['Play Date'] - 2082826800, unit='s')


    df.loc[:,'Total Time'] = df['Total Time'].apply(pd.to_numeric)
    #df.loc[:,'Total Time'] = pd.to_timedelta(df['Total Time'], unit='ms')

    usefull_cols = ['Track ID', 'Name', 'Artist', 'Album Artist', 'Composer', 'Album',
       'Genre', 'Kind', 'Size', 'Total Time', 'Disc Number', 'Disc Count',
       'Track Number', 'Track Count', 'Year', 'Date Modified', 'Date Added',
       'Bit Rate', 'Sample Rate',  'Normalization',
       'Compilation',  
       'Album Rating',
        'Artwork Count',
         'File Type', 'Play Count',
       'Play Date', 'Play Date UTC', 'Rating',
       'Sort Album',
       'Sort Album Artist', 'Sort Composer','Sort Artist', 'Sort Name','Persistent ID', 'Track Type', 'Location',
       'File Folder Count', 'Library Folder Count', 'Podcast',]
    all_cols = ([col for col in df.columns if col in usefull_cols] 
                + [col for col in df.columns if col not in usefull_cols])

    df[all_cols].to_csv(os.path.join(path_to_lib_folder,f"{lib_name.split('.')[0]}.csv"))

    return df[all_cols]



def get_lib_as_lib(path_to_lib_folder,lib_version):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        lib_version (_type_): _description_

    Returns:
        _type_: _description_
    """

    lib_name = f'{lib_version}.xml'
    pkl_name = f'{lib_version}.pickle'
    
    if pkl_name in os.listdir(path_to_lib_folder):

        with open(os.path.join(path_to_lib_folder,pkl_name), 'rb') as handle:
            lib = pickle.load(handle)
    else:
        # must first parse...
        print('! Be Patient this will take a long time !')
        lib = library.parse(os.path.join(path_to_lib_folder,lib_name))

        with open(os.path.join(path_to_lib_folder,pkl_name), 'wb') as handle:
            pickle.dump(lib, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    return lib



def get_lib_as_csv(path_to_lib_folder,lib_version):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        lib_version (_type_): _description_

    Returns:
        _type_: _description_
    """
    lib_name = f'{lib_version}.xml'
    csv_name = f'{lib_version}.csv'
    if csv_name in os.listdir(path_to_lib_folder):

        df_lib = pd.read_csv(os.path.join(path_to_lib_folder,csv_name))
    else:
        # must first parse...
        print('! Be Patient this will take a long time !')
        df_lib =  convert_lib_to_csv(path_to_lib_folder,
                                        lib_name)
    
    return df_lib



def get_all_playlists_from_a_lib(path_to_lib, lib_version):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        lib_version (_type_): _description_
    """

    lib_lib = get_lib_as_lib(path_to_lib, lib_version)

    for playlist in lib_lib.playlists:
    #if '*' in  playlist.itunesAttributes['Name']:
        print("PL ", playlist.itunesAttributes['Name'])
        PL_to_m3u8(path_to_lib,playlist) 


def assign_score_to_df(path_to_lib,
                        lib_version,
                       pl_list =['*', '**', '***', '****', '*****']
                       ):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        lib_version (_type_): _description_
        pl_list (list, optional): _description_. Defaults to ['*', '**', '***', '****', '*****'].

    Returns:
        _type_: _description_
    """

    lib_lib = get_lib_as_lib(path_to_lib, lib_version)

    df_lib = get_lib_as_csv(path_to_lib, lib_version)

    pl_dict = {}
    df_list = []

    for i in range(len(pl_list)):

        pl_dict[i+1] = lib_lib.getPlaylist(pl_list[i])
        df = PL_to_m3u8(path_to_lib,pl_dict[i+1])
        df.loc[:,'Scoring'] = i+1
        df_list.append(df)


    df_score = pd.concat(df_list)

    full_df = df_lib.merge(df_score[['Location','Scoring']], on='Location')


    return full_df  

def group_by_cd(x):
    """_summary_

    Args:
        x (_type_): _description_
    """
    try:
        total_duration =  np.sum(x['Total Time'])
    except:
        total_duration = -1
    try:
        size =  sum(x['Size'].astype(int))
    except:   
        size = -1
    try:
        scoring = np.mean(x['Scoring'])
        int_scoring = np.mean(x['Scoring'].astype(int))

    except:     
        scoring=-1
        int_scoring =-1
    

    mean_bit_rate = np.mean(x['Bit Rate'].astype(int))
    num_track=len(x)
    min_track = np.min(x[ 'Track Number'])
    max_track = np.max(x[ 'Track Number'])
    track_num_delta = max_track+1 - min_track
    all_track_present = (track_num_delta == num_track)

    return pd.Series({'Album Total Time': total_duration,
                       'Album Size' : size,
                       'Album Scoring' :scoring ,
                       'Album Scoring Int' :int_scoring ,
                       'Album Bit Rate' :mean_bit_rate,
                       'Num Tracks' : num_track,
                       'Min Track Number' :min_track,
                       'Max Track Number' :max_track,
                       'Track Number Delta' :track_num_delta,
                       'All Track Present' : all_track_present,
                       })




def assign_album_features_to_df(path_to_lib,
                        lib_version,
                       pl_list =['*', '**', '*** 1', '**** 1', '***** 1']
                       ):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        lib_version (_type_): _description_
        pl_list (list, optional): _description_. Defaults to ['*', '**', '*** 1', '**** 1', '***** 1'].

    Returns:
        _type_: _description_
    """
    
    df_lib = assign_score_to_df(path_to_lib,
                        lib_version,
                       pl_list =pl_list
                       )
    
    df_lib.loc[:,'Album'] =  df_lib['Album'].apply(lambda x: x[:-1] if x.endswith(' ') else x)
    df_lib.loc[:,'Album Artist'] =  df_lib['Album Artist'].apply(lambda x: str(x)[:-1] if str(x).endswith(' ') else str(x))
    
    
    group_features = ['Album', 
                        'Album Artist', 
                        'Disc Number',
                        'Genre',  
                        'Disc Count']

    grouped_df = df_lib.groupby(by=group_features).apply(group_by_cd).reset_index()

    #grouped_df.loc[:,'cumsum_time'] = np.cumsum((grouped_df.loc[:,'Total Time']/1000)/(4*60*60))

    df_lib = df_lib.merge(grouped_df, on=group_features)

    return df_lib,grouped_df


def split_lib(lib_version,
                path_to_lib,
            split_type = ['Genre','Album Scoring',],
              maximum_size_feature = 'Album Size' ,
              maximum_bin_size_in_hours = 4,
              maximum_bin_size_in_gb = 1):
    """_summary_

    Args:
        lib_version (_type_): _description_
        path_to_lib (_type_): _description_
        split_type (list, optional): _description_. Defaults to ['Genre','Album Scoring',].
        maximum_size_feature (str, optional): _description_. Defaults to 'Album Size'.
        maximum_bin_size_in_hours (int, optional): _description_. Defaults to 4.
        maximum_bin_size_in_gb (int, optional): _description_. Defaults to 1.
    """
    
    df_lib,cd_df = assign_album_features_to_df(path_to_lib,
                                    lib_version)


    cd_df.to_csv(os.path.join(path_to_lib,f'{lib_version}_CDs.csv'))

    if split_type == 'random':

        sorted_df = cd_df.sample(frac = 1)
        split_name = 'random'
    elif type(split_type) == list:
        sorted_df = cd_df.sample(frac = 1)
        sorted_df = sorted_df.sort_values(by = split_type)

        split_name = split_type[0]

        if len(split_type)>1:
            for st in split_type[1:]:
                split_name+='_'+st
        split_name+='_'

    if maximum_size_feature == 'Album Total Time':
        maximum_bin_size = maximum_bin_size_in_hours * 60 *60 * 1000

    else:

        maximum_bin_size =  maximum_bin_size_in_gb * (1000*1000*1000)

    sorted_df.loc[:,'PL Id'] = np.cumsum((sorted_df.loc[:,maximum_size_feature])/(maximum_bin_size)).astype(int).astype(str)
    
    def group_by_pl(x):
        """_summary_

        Args:
            x (_type_): _description_

        Returns:
            _type_: _description_
        """

        mean_score = round(np.mean(x['Album Scoring']),1)
        med_genre = x.Genre.mode()[0].replace('/','-')
        return pd.Series({'PL Scoring' : mean_score,
                        'PL Genre' : med_genre,
                        'PL Name' : f'{med_genre}_{mean_score}_'
                        })

    pl_df = sorted_df.groupby(by = 'PL Id').apply(group_by_pl)

    sorted_df = sorted_df.merge(pl_df,on = 'PL Id')

    sorted_df.loc[:,'PL Name'] = sorted_df.loc[:,'PL Name'] +sorted_df.loc[:,'PL Id']

    PL_folder_name = f'split_{maximum_size_feature}_{split_type}'

    path_to_pl = os.path.join(path_to_lib,PL_folder_name)

    if PL_folder_name not in os.listdir(path_to_lib):
        os.mkdir(path_to_pl)
        
        
    group_features = ['Album', 
                        'Album Artist', 
                        'Disc Number',
                        'Genre',  
                        'Disc Count']

    #grouped_df = df_lib.groupby(by=group_features).apply(group_by_cd).reset_index()

    #grouped_df.loc[:,'cumsum_time'] = np.cumsum((grouped_df.loc[:,'Total Time']/1000)/(4*60*60))

    df_lib = df_lib.merge(sorted_df[group_features+['PL Name']], on=group_features)

    for pl_name in sorted_df.loc[:,'PL Name'].unique():

        df_lib[df_lib.loc[:,'PL Name']== pl_name].to_csv(os.path.join(path_to_pl, f'{pl_name}.csv'))
                                                         
        df_to_m3u8(df_lib[df_lib.loc[:,'PL Name']== pl_name],
                    pl_name, 
                    path_to_pl)



##########################
# EDIT THE 5 LINES BELOW #
##########################
lib_version = 'iTunesLibrary-2024-02-09'
path_to_lib = '/Users/tom/Music/music-lib-experiments/'

split_lib(lib_version,
                path_to_lib,
            split_type = ['Genre','Album Scoring',],
              maximum_size_feature = 'Album Size' ,
              maximum_bin_size_in_hours = 4,
              maximum_bin_size_in_gb = 10)

split_lib(lib_version,
                path_to_lib,
            split_type = ['Genre','Album Scoring',],
              maximum_size_feature = 'Album Total Time' ,
              maximum_bin_size_in_hours = 10,
              maximum_bin_size_in_gb = 10)
