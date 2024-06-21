"""
performs retrieval of the recordings and their stats
"""
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
from datetime import timedelta, datetime
import numpy as np

import pathlib
import os
import re
from glob import glob

# audio info processing
from pydub.utils import mediainfo
from lib_henryk.config import *
from lib_henryk.logger import *
from lib_henryk import utils

def get_recordings_files_list(path_recordings: str=DIR_RECORDINGS) -> list[str]:
    return glob(f'{path_recordings}/**/*.m4a', recursive=True)


def get_recordings_names_df(path_recordings: str=DIR_RECORDINGS) -> pd.DataFrame:
    files_list = get_recordings_files_list(path_recordings) # first - get files list
    filenames_list = [os.path.basename(f) for f in files_list ] # get basenames of files
    names_list = [utils.get_file_name_without_extension(f) for f in files_list] # retrieve names

    # generate dataframe
    df = pd.DataFrame({
        "path": files_list,
        "file": filenames_list,
        "name": names_list,
    })
    return df

def sort_df_by_date_inferred_from_name( df: pd.DataFrame, drop_date:bool=True ) -> pd.DataFrame:
    # make sure that files are ordered in their natural temporal order (from name)
    df = df.reset_index(drop=True) # change index from name to ordinal
    series_date = df['name'].str.extract('^.+ (\d+-\d+-\d+) .+$')[0] # extract regex group [0]
    df['date'] = series_date # attach date to dataframe
    df = df.sort_values(by='date') # sort by date
    df.drop('date', axis=1, inplace=True) # drop unnecessary column
    df.reset_index(inplace=True, drop=True) # reset indexing after sorting
    return df

def get_recordings_info(path_recordings: str) -> pd.DataFrame:
    # load patsh to all audio files from wiadomości do Henryczka
    files_m4a = get_recordings_files_list(path_recordings=path_recordings)
    logger.info(f'retrieved {len(files_m4a)} files')
    
    # iterate over files and produce entries for the dataset
    df = pd.DataFrame( {
        'file': [], 
        'name': [], 
        'title': [], 
        'kind': [], 
        'date': [], 
        'type': [], 
        'duration': [], 
    } )

    for i, f in enumerate(files_m4a):
        progressBar(i,len(files_m4a)-1, prefix=f'processing {len(files_m4a)} audio files')

        # get audio file info
        audio_recording_info = get_audio_file_info(recording_file_path=f)

        # add row to dataframe, recording info has the same items 
        # as those that we expect in the dataframe
        if audio_recording_info != None:
            df.loc[len(df)] = audio_recording_info

    # sort and reindex
    df = df.sort_values(by='date')
    df = df.reset_index(drop=True)

    logger.info(f'generated stats for {len(df)} audio recordings')
    
    # return dataframe
    return df 


def get_audio_file_info(recording_file_path: str) -> dict:
    """
    get info from a file and process into a dictionary
    """

    _recording_info = {}

    try:
        _info = mediainfo(recording_file_path)
        _filename = os.path.basename(recording_file_path) 
        _filename_regex_groups = re.search('^(.+) (\d+-\d+-\d+) (.+)\.(.+)$', _filename) # kind, date, name, extension
        _recording_kind = _filename_regex_groups[1]
        _recording_date = _filename_regex_groups[2]
        _recording_date = datetime.strptime(_recording_date, "%Y-%m-%d")
        _recording_name = "".join(_filename.split(".")[:-1])
        _recording_title = _filename_regex_groups[3]
        _recording_type = _filename_regex_groups[4]
        _recording_duration = _info['duration']
    
        _recording_info = {
            'file': _filename,
            'name': _recording_name,
            'title': _recording_title,
            'kind': _recording_kind,
            'date': _recording_date,
            'type': _recording_type,
            'duration': float(_recording_duration)
        }
    except Exception as e:
        logger.warning(f'encountered error for {recording_file_path}: {e}')
        return None
    
    return _recording_info


# EOF