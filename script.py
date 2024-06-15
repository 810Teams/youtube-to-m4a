"""
    YouTube to M4A Script

    https://github.com/810Teams/youtube-to-m4a

    Author: 810Teams
    Version: 1.0.0
"""

import os
import shutil
import sys

from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
from pytube import YouTube


# Settings
DEFAULT_AUDIO_QUALITY = 0
DEFAULT_TRACK_GENRE = 'J-Pop'

SKIP_IF_FILE_EXIST = False
SHOW_LOG = True

# Definition
AUDIO_EXTENSION = '.m4a'
THUMBNAIL_EXTENSION = '.jpg'

# Data
M4A_TAGS = {
    'track title': '\xa9nam',
    'album': '\xa9alb',
    'artist': '\xa9ART',
    'album artist': 'aART',
    'composer': '\xa9wrt',
    'year': '\xa9day',
    'comment': '\xa9cmt',
    'description': 'desc',
    'purchase date': 'purd',
    'grouping': '\xa9grp',
    'genre': '\xa9gen',
    'lyrics': '\xa9lyr',
    'podcast URL': 'purl',
    'podcast episode GUID': 'egid',
    'podcast category': 'catg',
    'podcast keywords': 'keyw',
    'encoded by': '\xa9too',
    'copyright': 'cprt',
    'album sort order': 'soal',
    'album artist sort order': 'soaa',
    'artist sort order': 'soar',
    'title sort order': 'sonm',
    'composer sort order': 'soco',
    'show sort order': 'sosn',
    'show name': 'tvsh',
    'work': '\xa9wrk',
    'movement': '\xa9mvn',
    'part of a compilation': 'cpil',
    'part of a gapless album': 'pgap',
    'podcast': 'pcst',
    'track number, total tracks': 'trkn',
    'disc number, total discs': 'disk',
    'tempo/BPM': 'tmpo',
    'Movement Count': '\xa9mvc',
    'Movement Index': '\xa9mvi',
    'work/movement': 'shwm',
    'Media Kind': 'stik',
    'HD Video': 'hdvd',
    'Content Rating': 'rtng',
    'TV Episode': 'tves',
    'TV Season': 'tvsn',
    'plID': 'plID',
    'cnID': 'cnID',
    'geID': 'geID',
    'atID': 'atID',
    'sfID': 'sfID',
    'cmID': 'cmID',
    'akID': 'akID',
    'cover artwork': 'covr',
}


#################
# Main Function #
#################

def main() -> None:
    """ Main function """
    # Initialization
    if len(sys.argv) <= 1:
        error('URL not provided.')
        return
    url: str = sys.argv[1]
    args: str = ' '.join(sys.argv[2:])

    # Download
    download_audio(url, args=args)
    download_thumbnail(url)

    # File processing
    copy_thumbnail(url)
    crop_thumbnail(url)
    assign_metadata(url)


#######################
# Prodecure Functions #
#######################

def download_audio(url: str, args: str=str()) -> None:
    """ Download and extract audio from YouTube video """
    audio_list: list = list_audios()
    audio_name: str = retrieve_audio_name(url)

    if audio_name in audio_list:
        log('Audio \'{}\' already exists.'.format(audio_name))

        if SKIP_IF_FILE_EXIST:
            log('Audio re-download skipped.')
            return

        os.remove(audio_name)
        log('Audio \'{}\' removed. Proceeding to re-download.'.format(audio_name))

    default_args_dict = {
        '--audio-format': AUDIO_EXTENSION[1:],
        '--audio-quality': DEFAULT_AUDIO_QUALITY
    }
    arg_segments = args.split()
    for i in range(len(arg_segments)):
        if arg_segments[i] in default_args_dict:
            default_args_dict.pop(arg_segments[i])
    default_args = ' '.join(['{} {}'.format(i, default_args_dict[i]) for i in default_args_dict])

    os.system('yt-dlp "{}" -x {} {}'.format(url, default_args, args))


def download_thumbnail(url: str) -> None:
    """ Download YouTube video thumbnail """
    image_list: list = list_images()
    image_name: str = retrieve_image_name(url)

    if image_name in image_list:
        log('Thumbnail \'{}\' already exists.'.format(image_name))

        if SKIP_IF_FILE_EXIST:
            log('Thumbnail re-download skipped.')
            return

        os.remove(image_name)
        log('Thumbnail \'{}\' removed. Proceeding to re-download.'.format(image_name))

    os.system('pythumb "{}"'.format(url))


def copy_thumbnail(url: str) -> None:
    """ Copy image for manual cropping """
    image_name: str = retrieve_image_name(url)
    copied_image_name: str = image_name.replace(THUMBNAIL_EXTENSION, '_copy' + THUMBNAIL_EXTENSION)
    shutil.copy2(image_name, copied_image_name)
    log('Thumbnail \'{}\' copied as \'{}\' for manual cropping.'.format(image_name, copied_image_name))


def crop_thumbnail(url: str) -> None:
    """ Crop image to square size"""
    image_name: str = retrieve_image_name(url)
    image: Image.Image = Image.open(image_name)

    width, height = image.size
    size = min(width, height)
    offset = round((max(width, height) - size)/2)

    left = width - max(width - offset, size)
    top = height - max(height - offset, size)
    right = max(width - offset, size)
    bottom = max(height - offset, size)

    image = image.crop((left, top, right, bottom))
    image.save(image_name)

    log('Thumbnail \'{}\' cropped.'.format(image_name))


def assign_metadata(url: str) -> None:
    """ Assign METADATA to audio file """
    # Initialization
    audio_name: str = retrieve_audio_name(url)
    image_name: str = retrieve_image_name(url)
    audio_file: MP4 = MP4(audio_name)
    youtube: YouTube = YouTube(url)

    # Set Track Info
    audio_file[M4A_TAGS['track title']] = youtube.title
    audio_file[M4A_TAGS['artist']] = youtube.author
    audio_file[M4A_TAGS['album']] = '{} - Single'.format(youtube.title)
    audio_file[M4A_TAGS['album artist']] = youtube.author
    audio_file[M4A_TAGS['year']] = str(youtube.publish_date.year)
    audio_file[M4A_TAGS['genre']] = DEFAULT_TRACK_GENRE
    audio_file[M4A_TAGS['disc number, total discs']] = (1, 1),
    audio_file[M4A_TAGS['track number, total tracks']] = (1, 1),

    # Set Cover Artwork
    with open(image_name, 'rb') as f:
        audio_file[M4A_TAGS['cover artwork']]  = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)]
    log('Track \'{}\' cover artwork set.'.format(audio_name))
    os.remove(image_name)
    log('Thumbnail \'{}\' deleted.'.format(image_name))

    # Save
    audio_file.save()


#######################
# Utilities Functions #
#######################

def retrieve_id(url: str) -> str:
    """ Retrieve ID from URL """
    if 'youtube.com' in url:
        return url.split('?v=')[1].split('&')[0]
    elif 'youtu.be' in url:
        return url.split('.be/')[1].split('?si=')[0]


def list_audios() -> list:
    """ Get audio list """
    return [i for i in os.listdir() if i[-len(AUDIO_EXTENSION):] == AUDIO_EXTENSION]


def list_images() -> list:
    """ Get image list """
    return [i for i in os.listdir() if i[-len(THUMBNAIL_EXTENSION):] == THUMBNAIL_EXTENSION]


def retrieve_audio_name(url: str) -> str:
    """ Retrieve audio name from Youtube URL """
    audio_list: list = [audio_file for audio_file in list_audios() if retrieve_id(url) in audio_file]

    return audio_list[0] if len(audio_list) > 0 else None


def retrieve_image_name(url: str) -> str:
    """ Retrieve image name from Youtube URL """
    image_list: list = list_images()
    image_name: str = '{}{}'.format(retrieve_id(url), THUMBNAIL_EXTENSION)

    if image_name in image_list:
        return image_name
    return None


#####################
# Logging Functions #
#####################

def log(message: str) -> None:
    """ Display message """
    if SHOW_LOG:
        print(message)


def error(message: str) -> None:
    """ Display error message """
    print('[ERROR] {}'.format(message))


#######
# Run #
#######

if __name__ == '__main__':
    main()
