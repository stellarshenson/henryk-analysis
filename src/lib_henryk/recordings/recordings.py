"""
performs retrieval of the recordings and their stats
"""
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
from datetime import timedelta, datetime
import numpy as np

import os
import re
from glob import glob

# audio info processing
from pydub.utils import mediainfo
from lib_henryk.config import *
from lib_henryk.logger import *
from lib_henryk.utils import *

def get_recordings_info(path_recordings: str) -> pd.DataFrame:
    # load patsh to all audio files from wiadomości do Henryczka
    files_m4a = glob(f'{path_recordings}/**/*.m4a', recursive=True)
    files_txt = glob(f'{path_recordings}/**/*.txt', recursive=True)
    files_doc = glob(f'{path_recordings}/**/*.docx', recursive=True)
    files_json = glob(f'{path_recordings}/**/*.json', recursive=True)
    logger.info(f'retrieved {len(files_m4a)} files')

    # strip path from json, txt, doc files
    files_txt = [os.path.basename(f) for f in files_txt]
    files_doc = [os.path.basename(f) for f in files_doc]
    files_json = [os.path.basename(f) for f in files_json]
    
    # iterate over files and produce entries for the dataset
    df = pd.DataFrame( {
        'path': [], 
        'file': [], 
        'name': [], 
        'kind': [], 
        'date': [], 
        'type': [], 
        'duration': [], 
        'transcription_doc': [],
        'transcription_txt': [],
        'transcription_json': [],
    } )

    for i, f in enumerate(files_m4a):
        progressBar(i,len(files_m4a)-1, prefix=f'processing {len(files_m4a)} audio files')
        _row = get_file_info(path=f, path_recordings=path_recordings)

        # fill in json, txt and doc if found
        file_name_without_extension = get_file_name_without_extension(f)
        file_name_txt = file_name_without_extension + '.txt'
        file_name_doc = file_name_without_extension + '.docx'
        file_name_json = file_name_without_extension + '.json'

        # check if txt, doc and json found
        if file_name_doc in files_doc:
            _row['transcription_doc'] = file_name_doc

        if file_name_txt in files_txt:
            _row['transcription_txt'] = file_name_txt

        if file_name_json in files_json:
            _row['transcription_json'] = file_name_json

        # add row to dataframe
        if _row != None:
            df.loc[len(df)] = _row

    # return dataframe
    return df.sort_values(by='date')


def get_file_info(path: str, path_recordings: str) -> dict:
    """
    get info from a file and process into a dictionary
    """

    _recording_info = {}

    try:
        _info = mediainfo(path)
        _filename = os.path.basename(path) 
        _file_relativepath = path.replace(path_recordings + '/', '') # relative path to a file
        _filename_regex_groups = re.search('^(.+) (\d+-\d+-\d+) (.+)\.(.+)$', _filename) # kind, date, name, extension
        _recording_kind = _filename_regex_groups[1]
        _recording_date = _filename_regex_groups[2]
        _recording_date = datetime.strptime(_recording_date, "%Y-%m-%d")
        _recording_name = _filename_regex_groups[3]
        _recording_type = _filename_regex_groups[4]
        _recording_duration = _info['duration']
    
        _recording_info = {
            'path': _file_relativepath,
            'file': _filename,
            'name': _recording_name,
            'kind': _recording_kind,
            'date': _recording_date,
            'type': _recording_type,
            'duration': _recording_duration
        }
    except Exception as e:
        logger.warning(f'encountered error for {path}: {e}')
        return None
    
    return _recording_info


# EOF