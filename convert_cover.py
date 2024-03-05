import os
from PIL import Image, ImageFile
import io
import music_tag
import pandas as pd
import shutil



def find_all_paths(music_lib_path):
    return sorted([x[0] for x in os.walk(music_lib_path)])

##########################
# EDIT THE 5 LINES BELOW #
##########################
music_lib_path = '/Volumes/MasterAudio/Audio/'
create_cover_jpg = True
create_album_jpg = True
complete_missing_cover_art = True
convert_to_non_prog = True
##########################
#                        #
##########################

ImageFile.MAXBLOCK = 2**20

#@todo take care of capital extensions.

music_formats = ['.aac', '.aiff', '.dsf', '.flac',
                 '.m4a', '.mp3', '.ogg', '.opus',
                 '.wav', '.wv']

image_formats = ['.JPG','.jpg','.PNG','.png']


def extract_tags(song_tag,
                 song_path):

    result_dict = {}
    for feature in song_tag.keys():

        result_dict[feature] = str(song_tag[feature])

    result_dict['Location'] = song_path
    return result_dict



def exctract_artwork(song_path,
                     song_tag,
                    is_any_cover_image,
                    songs_wo_artwork):

    #@todo understand why 'artwork' can be missing
    try:
        song_tag['artwork']
        artwork = True
    except:

        artwork = False

    if not artwork:
        songs_wo_artwork.append(song_path)
    elif song_tag['artwork'] is None:
        songs_wo_artwork.append(song_path)
    elif song_tag['artwork'].first is None:
        songs_wo_artwork.append(song_path)

    else:
        if not is_any_cover_image:
            art_data = song_tag['artwork'].first.data
            image = Image.open(io.BytesIO(art_data))
            try:
                image.save(os.join.path(os.path.dirname(song_path),
                                        'non_prog_temp.jpg'),"JPEG",
                            quality=80, optimize=True, 
                            progressive=False)
            except:
                image = image.convert('RGB')
                image.save(os.join.path(os.path.dirname(song_path),
                                        'non_prog_temp.jpg'),"JPEG",
                                quality=80, optimize=True,
                                  progressive=False)
            is_any_cover_image = True

    return is_any_cover_image, songs_wo_artwork


def get_music_files_paths(music_dir):
    
    files = os.listdir(music_dir)
    
    files = [ f for f in files if ( True in [ f.endswith(form) for form in music_formats] )
                        and not f.startswith('._')]
    
    paths = [ os.path.join(music_dir,file) for file in files]

    return paths


def get_images_files_paths(music_dir):
    
    files = os.listdir(music_dir)
    
    files = [ f for f in files if ( True in [ f.endswith(form) for form in image_formats] )
                        and not f.startswith('._')]
    
    paths = [ os.path.join(music_dir,file) for file in files]

    return paths
    
    
def assign_artwork_to_song(song_path,
                         image_path):
    

    song_tag = music_tag.load_file(song_path)
    
    with open(image_path, 'rb') as image:
        song_tag['artwork'] = image.read()

    song_tag.save()

def assign_non_prog_artwork_to_song_list(music_dir,
                                         music_files_paths
                                         ):

    image_files_paths = get_images_files_paths(music_dir)

    if os.path.join(music_dir,'non_prog_temp.jpg') in image_files_paths:
        image_path = os.path.join(music_dir,'non_prog_temp.jpg')

        for song_path in music_files_paths:
            assign_artwork_to_song(song_path,image_path)




def loop_over_a_music_path(music_lib_path = '/Volumes/MasterAudio/Audio/',
                            create_cover_jpg = True,
                            create_album_jpg = True,
                            complete_missing_cover_art = True,
                            convert_to_non_prog = True,):

    paths_to_music = find_all_paths(music_lib_path)


    music_lib_df = pd.DataFrame([])

    for music_dir in paths_to_music:

        music_files_paths = get_music_files_paths(music_dir)

        image_files_paths = get_images_files_paths(music_dir)


        album_title = music_dir.split('/')[-1]

        is_any_cover_image = len(image_files)>0
    

        #@todo find empty music folders
        #if not music_files and not folder_in_path:
        #    print('folder is empty')

        #@todo add check for multiple album inside a folder

        if image_files_paths:
            image_file_path = image_files_paths[0]

            with open(image_file_path, 'rb') as image:

                image=image.read()
                image = Image.open(io.BytesIO(image))
                try:
                    image.save(os.join.path(music_dir,
                                        'non_prog_temp.jpg'),"JPEG",
                                quality=80, optimize=True, progressive=False)
                except:
                    image = image.convert('RGB')
                    image.save(os.join.path(music_dir,
                                        'non_prog_temp.jpg'),"JPEG",
                                    quality=80, optimize=True, progressive=False)

        songs_wo_artwork_paths = []

        for song_path in music_files_paths:

            song_tag = music_tag.load_file(song_path)

            is_any_cover_image, songs_wo_artwork_paths = exctract_artwork(song_path,
                                                                    song_tag,
                                                                    is_any_cover_image,
                                                                    songs_wo_artwork_paths)

            tags_dict = extract_tags(song_tag,song_path)

            music_lib_df = pd.concat(music_lib_df,
                                     pd.Series(tags_dict), ignore_index=True)


        if convert_to_non_prog and is_any_cover_image:

            assign_non_prog_artwork_to_song_list(music_dir,music_files_paths)

        if is_any_cover_image and songs_wo_artwork_paths and complete_missing_cover_art:

            assign_non_prog_artwork_to_song_list(music_dir,songs_wo_artwork_paths)

        image_files = get_images_files_paths(music_dir)

        if 'non_prog_temp.jpg' in image_files:
            if create_cover_jpg:
                shutil.copyfile(os.join.path(music_dir,'non_prog_temp.jpg'),
                                os.join.path(music_dir,'cover.jpg'))
            if create_album_jpg:

                shutil.copyfile(os.join.path(music_dir,'non_prog_temp.jpg'), 
                                os.join.path(music_dir,f'{album_title}.jpg'))

            os.remove(os.join.path(music_dir,'non_prog_temp.jpg'))

        elif songs_wo_artwork_paths:
            print('**** Album wo artwork: ', music_dir)
    return music_lib_df


loop_over_a_music_path(music_lib_path = '/Volumes/MasterAudio/Audio/',
                       create_cover_jpg = True,
                       create_album_jpg = True,
                       complete_missing_cover_art = True,
                       convert_to_non_prog = True)
