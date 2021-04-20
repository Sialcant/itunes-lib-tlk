import os
from PIL import Image, ImageFile
import io
import music_tag
#import pandas as pd
import shutil




##########################
# EDIT THE 5 LINES BELOW #
##########################
music_lib_path = '/Users/BenGast/Music/Music/Media.localized/Music'
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

music_formats += [format.upper() for format in music_formats]

image_formats = ['.jpg','.jpeg','.png']
image_formats += [format.upper() for format in image_formats]

def extract_tags(song_tag,
                 music_dir):

    result_dict = {}
    result_dict['artist'] = str(song_tag['artist'])
    result_dict['album'] = str(song_tag['album'])
    result_dict['album_artist'] = str(song_tag['album_artist'])
    result_dict['title'] = str(song_tag['title'])
    result_dict['genre'] = str(song_tag['genre'])

    result_dict['lyrics'] = len(song_tag['lyrics']) > 0

    result_dict['path'] = music_dir.replace(music_lib_path, '')
    return result_dict

def find_all_paths(music_lib_path):
    return sorted([x[0] for x in os.walk(music_lib_path)])

def exctract_artwork(song,
                     song_tag,
                    is_any_cover_image,
                    songs_wo_artwork,
                     music_dir):

    #@todo understand why 'artwork' can be missing
    try:
        song_tag['artwork']
        artwork = True
    except:

        artwork = False

    if not artwork:
        songs_wo_artwork.append(song)
    elif song_tag['artwork'] is None:
        songs_wo_artwork.append(song)
    elif song_tag['artwork'].first is None:
        songs_wo_artwork.append(song)

    else:
        if not is_any_cover_image:
            art_data = song_tag['artwork'].first.data
            image = Image.open(io.BytesIO(art_data))
            try:
                image.save(music_dir+'/'+'non_prog_temp.jpg',"JPEG",
                            quality=80, optimize=True, progressive=False)
            except:
                image = image.convert('RGB')
                image.save(music_dir+'/'+'non_prog_temp.jpg',"JPEG",
                                quality=80, optimize=True, progressive=False)
            is_any_cover_image = True

    return is_any_cover_image, songs_wo_artwork



def loop_over_music():

    paths_to_music = find_all_paths(music_lib_path)

    #csv_name = f'{str(datetime.now())}_music_lib.csv'
    #csv_name = 'music_lib.csv'
    #music_lib_df = pd.DataFrame([])

    for music_dir in paths_to_music:

        files = os.listdir(music_dir)

        #print(music_dir.split('/')[-1])

        music_files = [ f for f in files if ( True in [ f.endswith(form) for form in music_formats] )
                        and not f.startswith('._')]

        image_files = [ f for f in files if ( True in [ f.endswith(form) for form in image_formats] )
                        and not f.startswith('._')]

        is_any_cover_image = len(image_files)>0
        #print(image_files)

        #folder_in_path = ...
        #@todo find empty music folders
        #if not music_files and not folder_in_path:
        #    print('folder is empty')

        #@todo add check for multiple album inside a folder

        if image_files:
            image_file = image_files[0]

            with open(music_dir+'/'+image_file, 'rb') as image:
                image=image.read()
                image = Image.open(io.BytesIO(image))
                try:
                    image.save(music_dir+'/'+'non_prog_temp.jpg',"JPEG",
                                quality=80, optimize=True, progressive=False)
                except:
                    image = image.convert('RGB')
                    image.save(music_dir+'/'+'non_prog_temp.jpg',"JPEG",
                                    quality=80, optimize=True, progressive=False)

        songs_wo_artwork = []

        album_title = music_dir.split('/')[-1]

        for song in music_files:

            song_tag = music_tag.load_file(music_dir+'/'+song)

            is_any_cover_image, songs_wo_artwork = exctract_artwork(song,
                                                                    song_tag,
                                                                    is_any_cover_image,
                                                                    songs_wo_artwork,
                                                                    music_dir)

            #tags_dict = extract_tags(song_tag,music_dir)

            #music_lib_df = music_lib_df.append(tags_dict, ignore_index=True)
        #music_lib_df.to_csv(csv_name, index=False)

        if convert_to_non_prog and is_any_cover_image:

            image_files = [ f for f in files if ( True in [ f.endswith(form) for form in image_formats] )
                            and not f.startswith('._')]

            if 'non_prog_temp.jpg' in image_files:
                image_file = 'non_prog_temp.jpg'

                for song in music_files:
                    song_tag = music_tag.load_file(music_dir + '/' + song)

                    with open(music_dir+'/'+image_file, 'rb') as image:
                        song_tag['artwork'] = image.read()

                    song_tag.save()

        if is_any_cover_image and songs_wo_artwork and complete_missing_cover_art:

            for song in songs_wo_artwork:

                song_tag = music_tag.load_file(music_dir+'/'+song)

                image_files = [ f for f in files if ( True in [ f.endswith(form) for form in image_formats] )
                                and not f.startswith('._')]

                if 'non_prog_temp.jpg' in image_files:
                    image_file = 'non_prog_temp.jpg'

                    with open(music_dir+'/'+image_file, 'rb') as image:
                        song_tag['artwork'] = image.read()

                    song_tag.save()
        files = os.listdir(music_dir)
        image_files = [f for f in files if (True in [f.endswith(form) for form in image_formats])
                       and not f.startswith('._')]

        #print(image_files)

        if 'non_prog_temp.jpg' in image_files:
            if create_cover_jpg:
                shutil.copyfile(music_dir+'/'+'non_prog_temp.jpg', music_dir+'/'+'cover.jpg')
            if create_album_jpg:

                shutil.copyfile(music_dir+'/'+'non_prog_temp.jpg', music_dir+'/'+album_title+'.jpg')

            os.remove(music_dir+'/'+'non_prog_temp.jpg')

        elif songs_wo_artwork:
            print('**** Album wo artwork: ', music_dir)

        image_files = [f for f in files if (True in [f.endswith(form) for form in image_formats])
                       and not f.startswith('._')]

        #print(image_files)



loop_over_music()
