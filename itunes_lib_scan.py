import pandas as pd
import os
import xml.etree.ElementTree as ET ## XML parsing
from collections import defaultdict
import numpy as np
from itunesLibrary import library

from urllib.parse import unquote
from convert_cover import loop_over_a_music_path
from convert_playlist import convert_playlists

from convertion_functions import m3u8_to_csv,df_to_m3u8,PL_to_m3u8

import datetime

import pickle 

import parameters as param


grand_genre = ['Chant','Classique','Électro',
               'Jazz','Mix','Opéra','Pop','Rock',
               'Simple','Techno','Variété',
               ]


def get_lib_as_lib(path_to_lib_folder,
                   lib_name,
                   path_to_dest_folder):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        lib_name (_type_): _description_

    Returns:
        _type_: _description_
    """

    lib_name = f'{lib_name}.xml'
    pkl_name = f'{lib_name}.pickle'
    
    if pkl_name in os.listdir(path_to_dest_folder):

        with open(os.path.join(path_to_dest_folder,
                               pkl_name), 'rb') as handle:
            
            lib = pickle.load(handle)
    else:
        # must first parse...
        print(f'! Be Patient. Parsing your {lib_name} will take a long time (~60mins for a 30k songs lib with a Mac mini M2) !')
        lib = library.parse(os.path.join(path_to_lib_folder,lib_name))

        with open(os.path.join(path_to_dest_folder,pkl_name), 'wb') as handle:
            pickle.dump(lib, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    return lib

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

    numeric_columns = ['Artwork Count', 'Bit Rate', 
                       'Disc Count', 'Disc Number', 
                       'Movement Count', 'Movement Number', 
                       'Play Count', 'Play Date', 
                       'Sample Rate', 'Size', 'Skip Count',
                         'Track Count', 'Track ID', 
                         'Track Number', 'Year']
    
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

    date_columns = ['Date Added', 'Date Modified', 'Play Date UTC', 'Release Date', 'Skip Date']

    df[date_columns] = df[date_columns].apply(pd.to_datetime)

    df['Play Date'] = pd.to_datetime(df['Play Date'] - 2082826800, unit='s')


    df.loc[:,'Total Time'] = df['Total Time'].apply(pd.to_numeric)
    #df.loc[:,'Total Time'] = pd.to_timedelta(df['Total Time'], unit='ms')

    usefull_cols = ['Track ID', 'Name', 'Artist', 
                    'Album Artist', 'Composer', 'Album',
                    'Genre', 'Kind', 'Size', 'Total Time', 
                    'Disc Number', 'Disc Count',
                    'Track Number', 'Track Count', 
                    'Year', 'Date Modified', 'Date Added',
                    'Bit Rate', 'Sample Rate',  'Normalization',
                    'Compilation',  'Album Rating','Artwork Count',
                    'File Type', 'Play Count',
                    'Play Date', 'Play Date UTC', 'Rating',
                    'Sort Album','Sort Album Artist',
                    'Sort Composer','Sort Artist', 
                    'Sort Name','Persistent ID', 'Track Type', 
                    'Location','File Folder Count',
                    'Library Folder Count', 'Podcast',]
    
    all_cols = ([col for col in df.columns if col in usefull_cols] 
                + [col for col in df.columns if col not in usefull_cols])
    df.loc[:,'Location'] = df.loc[:,'Location'].apply(lambda x : unquote(x)) 
    df[all_cols].to_csv(os.path.join(path_to_lib_folder,f"{lib_name.split('.')[0]}.csv"))

    return df[all_cols]

def get_lib_as_csv(path_to_lib_folder,lib_name):
    """_summary_

    Args:
        path_to_lib_folder (_type_): _description_
        lib_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    lib_name = f'{lib_name}.xml'
    csv_name = f'{lib_name}.csv'
    if csv_name in os.listdir(path_to_lib_folder):

        df_lib = pd.read_csv(os.path.join(path_to_lib_folder,csv_name))
    else:
        # must first parse...
        print('! Be Patient this will take a few seconds !')
        df_lib =  convert_lib_to_csv(path_to_lib_folder,
                                        lib_name)
        
    
    df_lib.loc[:,'Location'] = df_lib.loc[:,'Location'].apply(lambda x : unquote(x)) 
    
    return df_lib

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
    album_type = x.Kind.mode()[0]

    album_location = x[ 'Album Location'].mode()[0]
    album_multi_location = len(x[ 'Album Location'].unique())>0



    return pd.Series({'Album Total Time': total_duration,
                       'Album Size' : size,
                       'Album Scoring' :scoring ,
                       'Album Scoring Int' :int_scoring ,
                       'Album Bit Rate' :mean_bit_rate,
                       'Album Files Kind': album_type,
                       'Album Location' : album_location,
                       'Album Has Multiple Locations' : album_multi_location,
                       'Num Tracks' : num_track,
                       'Min Track Number' :min_track,
                       'Max Track Number' :max_track,
                       'Track Number Delta' :track_num_delta,
                       'All Track Present' : all_track_present,
                       })




def assign_score_to_df(lib_lib,
                        df_lib,
                        path_to_lib,
                       pl_list =['0',
                                 '*',
                                 '**', 
                                 '***', 
                                 '****', 
                                 '*****']
                       ):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        lib_name (_type_): _description_
        pl_list (list, optional): _description_. 
        Defaults to ['*', '**', '***', '****', '*****'].

    Returns:
        _type_: _description_
    """

    #get_all_playlists_from_a_lib(path_to_lib, lib_name)
    
    pl_dict = {}
    df_list = []

    for i in range(len(pl_list)):

        pl_dict[i] = lib_lib.getPlaylist(pl_list[i])
        df = PL_to_m3u8(path_to_lib,pl_dict[i])
        df.loc[:,'Scoring'] = i
        df_list.append(df)


    df_score = pd.concat(df_list)
    full_df = df_lib.merge(df_score[['Location','Scoring']], on='Location')

    return full_df  





def get_cd_df(df_lib,
              lib_lib = None,
                path_to_lib = None,
                pl_list =['0',
                          '*',
                          '**', 
                          '***',
                          '****',
                          '*****']
                ):
    """_summary_

    Args:
        path_to_lib (_type_): _description_
        lib_name (_type_): _description_
        pl_list (list, optional): _description_. Defaults to ['*', '**', '*** 1', '**** 1', '***** 1'].

    Returns:
        _type_: _description_
    """
    if lib_lib !=None:

        df_lib = assign_score_to_df(lib_lib,
                                    df_lib,
                                    path_to_lib = path_to_lib,
                                    pl_list =pl_list)

    df_lib.loc[:,'Album'] =  df_lib['Album'].apply(lambda x: x[:-1] if x.endswith(' ') else x)
    df_lib.loc[:,'Album Artist'] =  df_lib['Album Artist'].apply(lambda x: str(x)[:-1] if str(x).endswith(' ') else str(x))
    
    group_features = ['Album', 
                        'Album Artist', 
                        'Disc Number',
                        'Genre',  
                        'Disc Count'
                        ]

    grouped_df = df_lib.groupby(by=group_features).apply(group_by_cd).reset_index()

    #grouped_df.loc[:,'cumsum_time'] = np.cumsum((grouped_df.loc[:,'Total Time']/1000)/(4*60*60))

    df_lib = df_lib.merge(grouped_df, on=group_features)
    #df_lib.loc[:,'Album Location'] = df_lib.loc[:,'Location'].apply(lambda y: os.path.dirname(y))

    return df_lib,grouped_df


def get_scanned_df(music_lib_path,
                   path_to_dest_folder,
                   force_scan,
                   create_cover_jpg ,
                   create_album_jpg,
                   complete_missing_cover_art,
                     convert_to_non_prog):

    files = os.listdir(path_to_dest_folder)

    scanned_files = sorted([f for f in files if f.endswith(f'{str(datetime.datetime.now().date())}_music_lib_scan.csv')])
                                                 
    if len(scanned_files)>0 and not force_scan:
        df_lib_scanned = pd.read_csv(os.path.join(path_to_dest_folder,scanned_files[-1]))
    else:

        print(f'! Be Patient. Scanning all the music your {music_lib_path} will take a long time (~15mins for a 30k songs lib with a Mac mini M2) !')
        
        df_lib_scanned = loop_over_a_music_path(music_lib_path = music_lib_path,
                                                          create_cover_jpg = create_cover_jpg,
                                                          create_album_jpg = create_album_jpg,
                                                          complete_missing_cover_art = complete_missing_cover_art,
                                                          convert_to_non_prog = convert_to_non_prog)
        
        df_lib_scanned.to_csv(os.path.join(path_to_dest_folder,f'{str(datetime.datetime.now().date())}_music_lib_scan.csv'))
        
    return df_lib_scanned




class LibScan:

    def __init__(self,
                path_to_library_file=None,
                path_to_dest_folder = None,
                path_to_music_folder=None,
                force_scan = False,
                create_cover_jpg = True,
                create_album_jpg = True,
                complete_missing_cover_art = True,
                convert_to_non_prog = True,
                skip_scanning = True ):
        
        if path_to_dest_folder != None:
            self.path_to_dest_folder = path_to_dest_folder
        else:
            self.path_to_dest_folder= os.path.join(os.path.dirname(os.getcwd() ),'itunes-lib-data')

        if 'itunes-lib-data' not in os.listdir(os.path.join(os.path.dirname(os.getcwd()))):
            os.mkdir(self.path_to_dest_folder)

        self.create_cover_jpg = create_cover_jpg
        self.create_album_jpg = create_album_jpg
        self.complete_missing_cover_art = complete_missing_cover_art
        self.convert_to_non_prog = convert_to_non_prog
        
        if path_to_library_file != None:
            self.path_to_library_file = path_to_library_file
            self.path_to_library_folder = os.path.dirname(self.path_to_library_file)
            self.lib_name = os.path.basename(self.path_to_library_file)

        if path_to_music_folder != None:
            self.path_to_music_folder = path_to_music_folder

        if self.path_to_library_file != None:

            self.path_to_playlists_folder = os.path.join(self.path_to_dest_folder,
                                           f'{self.lib_name}_Playlists')
            
            if f'{self.lib_name}_Playlists' not in os.listdir(self.path_to_dest_folder):
                os.mkdir(self.path_to_playlists_folder)
        
            self.lib_lib = get_lib_as_lib(self.path_to_library_folder,
                                          self.lib_name,
                                          self.path_to_dest_folder
                                          )
            
            self.df_lib = get_lib_as_csv(self.path_to_library_folder,
                                         self.lib_name)
            
            self.df_lib.loc[:,'Album Location'] = self.df_lib.loc[:,'Location'].apply(lambda x :os.path.dirname(x))
                                                                                    


            self.album_paths = sorted(set(self.df_lib.loc[:,'Album Location']))
        else:
            self.lib_lib = None
            self.df_lib = pd.DataFrame([])
            self.path_to_playlists_folder = os.path.join(path_to_music_folder,
                                           f'Playlists')
            
            if f'Playlists' not in os.listdir(path_to_music_folder):
                os.mkdir(self.path_to_playlists_folder)

        if path_to_music_folder != None and not skip_scanning :

            print(' ! Warning this part is going to modify your music files !')


            self.df_lib_scanned = get_scanned_df(path_to_music_folder,
                                                 self.path_to_dest_folder,                                                 
                                                 force_scan,
                                                 create_cover_jpg = self.create_cover_jpg,
                                                create_album_jpg = self.create_album_jpg,
                                                complete_missing_cover_art = self.complete_missing_cover_art,
                                                    convert_to_non_prog = self.convert_to_non_prog)
            
            if self.df_lib.empty:
            
                self.df_lib = self.df_lib_scanned.rename(columns = param.tags_to_itunes_cols_dict)

            
        self.df_lib, self.df_cd  = get_cd_df(self.df_lib,
                                             lib_lib = self.lib_lib,
                                             path_to_lib  = self.path_to_dest_folder)
           
        self.df_cd.to_csv(os.path.join(self.path_to_dest_folder,f'{self.lib_name}_CDs.csv'))

        
    def get_all_playlists_from_a_lib(self):
        """_summary_


        Args:
            path_to_lib_folder (_type_): _description_
            lib_name (_type_): _description_
        """
        if self.lib_lib !=None:
            for playlist in self.lib_lib.playlists:
            #if '*' in  playlist.itunesAttributes['Name']:
                #print("PL ", playlist.itunesAttributes['Name'])
                PL_to_m3u8(self.path_to_playlists_folder,
                           playlist) 


    def get_all_playlists_with_alternative_path(self,
                                                new_root_folder):

        self.get_all_playlists_from_a_lib()
        if self.path_to_music_folder !=None:
            convert_playlists(path_to_playlists = self.path_to_playlists_folder,
                            destination_folder = 'Playlists_WM',
                            iTunes_lib_path = self.path_to_music_folder,
                            walkman_lib_path= new_root_folder)



    def get_locations_with_multiple_album(self):

        def group_by_location(x):
            
            return pd.Series({'Number of Album in Location': len(x.Album.unique())})


        grouped_df = self.df_lib.groupby(by='Album Location').apply(group_by_location).reset_index()

        self.df_cd = pd.merge(self.df_cd, grouped_df, on='Album',how = 'left')

        self.df_cd[self.df_cd['Number of Album in Location']>1].to_csv(os.path.join(self.path_to_dest_folder,
                                                                                    'locations_with_multiple_album.csv',index=False))






    def split_lib_by_features(self,
                split_type = ['Genre','Album Scoring',],
                maximum_size_feature = 'Album Size' ,
                maximum_bin_size_in_hours = 4,
                maximum_bin_size_in_gb = 1,
                grand_genre = grand_genre):
        """_summary_

        Args:
            lib_name (_type_): _description_
            path_to_lib_folder (_type_): _description_
            split_type (list, optional): _description_. Defaults to ['Genre','Album Scoring',].
            maximum_size_feature (str, optional): _description_. Defaults to 'Album Size'.
            maximum_bin_size_in_hours (int, optional): _description_. Defaults to 4.
            maximum_bin_size_in_gb (int, optional): _description_. Defaults to 1.
        """

        if split_type == 'random':

            sorted_df = self.df_cd.sample(frac = 1)
            split_name = 'random'
        elif type(split_type) == list:
            sorted_df = self.df_cd.sample(frac = 1)
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

        sorted_df.loc[:,'PL Id'] = np.cumsum((sorted_df.loc[:,maximum_size_feature])
                                             /(maximum_bin_size)).astype(int).astype(str)
        
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

        path_to_pl = os.path.join(self.path_to_lib_folder,PL_folder_name)

        if PL_folder_name not in os.listdir(self.path_to_lib_folder):
            os.mkdir(path_to_pl)
            
            
        group_features = ['Album', 
                            'Album Artist', 
                            'Disc Number',
                            'Genre',  
                            'Disc Count']

        #grouped_df = df_lib.groupby(by=group_features).apply(group_by_cd).reset_index()

        #grouped_df.loc[:,'cumsum_time'] = np.cumsum((grouped_df.loc[:,'Total Time']/1000)/(4*60*60))

        self.df_lib = self.df_lib.merge(sorted_df[group_features+['PL Name']], on=group_features)

        for pl_name in sorted_df.loc[:,'PL Name'].unique():

            self.df_lib[self.df_lib.loc[:,'PL Name']== pl_name].to_csv(os.path.join(path_to_pl, f'{pl_name}.csv'))
                                                            
            df_to_m3u8(self.df_lib[self.df_lib.loc[:,'PL Name']== pl_name],
                        pl_name, 
                        path_to_pl)

    def split_lib_by_location(self,
                            audio_location,
                            level):

        self.df_lib.dropna(subset=['Total Time'],inplace=True)
        self.df_lib.loc[:,'Location_rep'] = self.df_lib.Location
        self.df_lib.loc[:,'audio_loc_in_loc'] = self.df_lib.Location_rep.apply(lambda x : audio_location in x)


        self.df_lib.loc[:,'level_max'] = np.where(self.df_lib.loc[:,'audio_loc_in_loc'],
            self.df_lib.Location_rep.apply(lambda x : len(x.split(audio_location)[-1].split('/'))),
                                                            0)

        self.df_lib.loc[:,'pl_name'] = np.where(self.df_lib.loc[:,'audio_loc_in_loc'],
            self.df_lib.Location_rep.apply(lambda x : '_'.join(x.split(audio_location)[-1].split('/')[0:min([level+1,len(x.split(audio_location)[-1].split('/'))
                                                                                    ])
                                                                                    ])),
                                                            0)
        path_to_pl = os.path.join(self.path_to_lib_folder,audio_location.replace('/','_' ))

        if audio_location.replace('/','_' ) not in os.listdir(self.path_to_lib_folder):
                os.mkdir(path_to_pl)
                
        print(self.df_lib.loc[:,'pl_name'].unique())

        for pl_name in self.df_lib.loc[:,'pl_name'].unique():
            if pl_name!=0:
                print(pl_name.replace(' ','_'))
                if len(self.df_lib[self.df_lib.pl_name == pl_name])>1:
                    self.df_lib_to_m3u8(self.df_lib[self.df_lib.pl_name == pl_name],
                            pl_name.replace(' ','_'), 
                            path_to_pl)
                    
    def split_lib_by_resolution(self,
                                resolutions = [128,192,256,320,1000]):

        df_temp = self.df_lib.copy()
        
        for res in sorted(resolutions):
            df =  df_temp[df_temp['Album Bit Rate']<=res ]
            df_temp =  df_temp[df_temp['Album Bit Rate']>res ]
            
            file_name = f'up_to_{res}_kbps'

            df_to_m3u8(df,file_name, self.path_to_playlists_folder)

        file_name = f'above_{res}_kbps'
        df_to_m3u8(df_temp,file_name, self.path_to_playlists_folder)

    def split_lib_by_format(self):
            
        for format in self.df_lib['Album File Type'].unique():
            df = self.df_lib[self.df_lib['Album File Type'] == format]
            file_name = f'{format}_files'
            df_to_m3u8(df,file_name, self.path_to_playlists_folder)

    #find_album_with_missing_songs(self):
                
        
    def get_pl_by_locations(self,
                            audio_locations,
                            levels):
        
        #df = get_lib_as_csv(path_to_lib_folder,lib_name)
        
        for i in range(len(audio_locations)):

            audio_location = audio_locations[i]
            level = levels[i]

            print(audio_location)

            self.df_lib.dropna(subset=['Total Time'],inplace=True)
            self.df_lib.loc[:,'Location_rep'] = self.df_lib.Location
            self.df_lib.loc[:,'audio_loc_in_loc'] = self.df_lib.Location_rep.apply(lambda x : audio_location in x)
            #return df

            self.df_lib.loc[:,'level_max'] = np.where(self.df_lib.loc[:,'audio_loc_in_loc'],
                self.df_lib.Location_rep.apply(lambda x : len(x.split(audio_location)[-1].split('/'))),#:min([level, 
                                                                #                                          len(x.replace('%20',' ').split(audio_location)[1].split('/'))])]),
                                                                0)

            self.df_lib.loc[:,'pl_name'] = np.where(self.df_lib.loc[:,'audio_loc_in_loc'],
                self.df_lib.Location_rep.apply(lambda x : '_'.join(x.split(audio_location)[-1].split('/')[0:min([level+1,len(x.split(audio_location)[-1].split('/'))
                                                                                        ])
                                                                                        ])),#:min([level, 
                                                                #                                          len(x.replace('%20',' ').split(audio_location)[1].split('/'))])]),
                                                                0)
            path_to_pl = os.path.join(self.path_to_playlists_folder,audio_location.replace('/','_' ))

            if audio_location.replace('/','_' ) not in os.listdir(self.path_to_playlists_folder):
                    os.mkdir(path_to_pl)
                    
            print(self.df_lib.loc[:,'pl_name'].unique())

            for pl_name in self.df_lib.loc[:,'pl_name'].unique():
                if pl_name!=0:
                    print(pl_name.replace(' ','_'))
                    if len(self.df_lib[self.df_lib.pl_name == pl_name])>1:
                        df_to_m3u8(self.df_lib[self.df_lib.pl_name == pl_name],
                                pl_name.replace(' ','_'), 
                                path_to_pl)