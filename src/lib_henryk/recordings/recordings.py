"""
performs retrieval of the recordings and their stats
"""
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
from datetime import timedelta, datetime
import numpy as np
from tqdm.autonotebook import tqdm  # progress bar
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import matplotlib.dates as mdates
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
    if drop_date == True: df.drop('date', axis=1, inplace=True) # drop unnecessary column
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

    with tqdm(desc=f'processing {len(files_m4a)} audio files', total=len(files_m4a), **TQDM_PARAMS) as pbar:
        for i, f in enumerate(files_m4a):
    
            # get audio file info
            audio_recording_info = get_audio_file_info(recording_file_path=f)
    
            # add row to dataframe, recording info has the same items 
            # as those that we expect in the dataframe
            if audio_recording_info != None:
                df.loc[len(df)] = audio_recording_info

            # progressbar update
            pbar.update()

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


def identify_date_gaps(df, date_column='date', threshold=timedelta(days=1)):
    """
    Identifies gaps in datetime data that exceed a specified threshold.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe containing datetime data
    date_column : str
        Name of the column containing datetime data
    threshold : timedelta
        The minimum gap size to report
        
    Returns:
    --------
    pandas.DataFrame
        A dataframe containing the gaps found, with columns for start_date, 
        end_date, and gap_days
    """
    # Ensure the date column is datetime type
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Sort by date
    df = df.sort_values(by=date_column).reset_index(drop=True)
    
    # Calculate gaps
    gaps = []
    for i in range(1, len(df)):
        current_date = df[date_column].iloc[i]
        previous_date = df[date_column].iloc[i-1]
        gap = current_date - previous_date
        
        if gap > threshold:
            gaps.append({
                'start_date': previous_date,
                'end_date': current_date,
                'gap_days': gap.total_seconds() / (60*60*24) - 1 # Convert to days
            })
    
    # Create a dataframe of gaps
    if gaps:
        gaps_df = pd.DataFrame(gaps)
        return gaps_df
    else:
        return pd.DataFrame(columns=['start_date', 'end_date', 'gap_days'])


# Assuming 'df' is your dataframe with the date column
def analyze_and_print_gaps(df, min_gap_days = 1):
    print("Analyzing temporal data for discontinuities...")
    
    # Find gaps
    gaps_df = identify_date_gaps(df, threshold=timedelta(days=min_gap_days + 1))
    
    if len(gaps_df) > 0:
        print(f"Located {len(gaps_df)} temporal discontinuities exceeding {min_gap_days} days:")
        print("="*60)
        
        for i, (_, row) in enumerate(gaps_df.iterrows()):
            print(f"Gap {i+1}:")
            print(f"  Start: {row['start_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  End:   {row['end_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duration: {row['gap_days']:.2f} days")
            print("-"*60)
            
        # Output summary statistics
        print("\nSummary:")
        print(f"  Total gaps found: {len(gaps_df)}")
        print(f"  Average gap size: {gaps_df['gap_days'].mean():.2f} days")
        print(f"  Maximum gap size: {gaps_df['gap_days'].max():.2f} days")
        print(f"  Minimum gap size: {gaps_df['gap_days'].min():.2f} days")
    else:
        print("No temporal discontinuities detected, Star Captain. Data integrity confirmed.")


# def plot_recordings_stats(df: pd.DataFrame):

#     #### STAGE 1 - analyse the stats
    
#     # selector to select only those from father
#     df_from_me = df[ df['kind'] == 'Henryk' ]
    
#     """
#     calculate scalar values
#     - total duration
#     - total count
#     """
#     total_duration_s = df['duration'].sum()
#     total_duration_h = total_duration_s / 3600
#     total_duration_d = np.floor(total_duration_h / 24)
#     total_duration_d_h = total_duration_h - total_duration_d * 24
#     date_min = df['date'].min()
#     date_max = df['date'].max()
    
#     """
#     duration of the recordings, group them by day
#     and perform moving average on them
#     """
#     df_duration_by_date = df.groupby('date')['duration'].sum() / 60
#     df_duration_by_date =  df_duration_by_date.to_frame()['duration'].to_frame() \
#         .rolling(14, closed='both', center=True).mean()
#     df_duration_by_date = df_duration_by_date.bfill().ffill() # fill nulls after rolling average
    
#     # display(df_duration_by_date)
    
#     """
#     count of the recordings (per week) 
#     and index them by the 'week of' date column
#     and next average them by month (4 weeks)
#     """
    
#     df_count_by_week = df.copy()
#     df_count_by_week['week'] = df['date'].dt.strftime('%Y') + '-' + df['date'].dt.strftime('%W')
#     df_count_by_week = df_count_by_week.groupby('week').agg({'date':['min'], 'name' : ['count']})
#     df_count_by_week = df_count_by_week.droplevel(axis=1, level=1).rename(columns={'name':'count'}) \
#         .reset_index().set_index('date').drop('week', axis=1)
#     df_count_by_week.iloc[[0,-1],[0]] = None # remove count value from first and last row, because weeks are incomplete
#     df_count_by_week = df_count_by_week['count'].to_frame().rolling(1, closed='both', center=True).mean()
#     df_count_by_week = df_count_by_week.bfill().ffill() # fill nulls after rolling average
#     df_count_by_week['count'] = df_count_by_week['count'].round()
    
#     ### STAGE 2 - plot the results
    
#     # plot number of minutes / day
#     fig, axs = plt.subplots(2, 1, figsize=(12,8))
#     sns.scatterplot(ax=axs[0], data=df_duration_by_date, linewidth=0.05, s=25, alpha=1)
#     axs[0].vlines(x=df_duration_by_date.index, ymin=0, ymax=df_duration_by_date['duration'], color='skyblue', alpha =0.8)
#     axs[0].set_title(f'Długość {len(df)} nagrań od taty dla Henryka od {date_min.date()} do {date_max.date()}' 
#                  + '\n' + f'Całkowita długość nagrań wynosi {total_duration_h:,.0f} godzin ({total_duration_d:,.0f} pełnych dni i {total_duration_d_h:.0f} godzin)' )
#     axs[0].grid(axis='y')
#     axs[0].legend(loc='upper right', labels=['Długość nagrań dla Henryka'])
#     axs[0].get_legend().remove()
#     axs[0].tick_params(axis='x', labelrotation=45, labelsize=8)
#     axs[0].set_ylabel("Długość nagrań (minuty)")
#     axs[0].set_xlabel("Data")
#     axs[0].set_xlim( (date_min, date_max) )
#     axs[0].set_ylim( bottom=0 )
#     axs[0].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))   #to get a tick every 15 minutes
    
#     # plot number of recordings / week
#     sns.barplot(ax=axs[1], x=df_count_by_week.index, hue=df_count_by_week.index, y=df_count_by_week['count'], palette='Blues_d', legend=False)
#     axs[1].set_title(f'Tygodniowa liczba nagrań od taty dla Henryka, ponad {len(df_count_by_week)} tygodni alienacji' )
#     axs[1].grid(axis='y')
#     axs[1].set_ylabel("Ilość nagrań w tygodniu")
#     axs[1].set_xlabel("Tydzień")
#     y_max = int(axs[1].get_ybound()[1])
#     axs[1].set_xticks( range(0,y_max) )
#     axs[1].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))   #to get a tick every 15 minutes
#     axs[1].tick_params(axis='x', labelrotation=45, labelsize=8)
#     fig.tight_layout(rect=[0, 0.01, 1, 0.99])
#     plt.show()

def plot_recordings_stats(df: pd.DataFrame):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    from matplotlib.lines import Line2D
    
    #### STAGE 1 - analyse the stats
    
    # selector to select only those from father
    df_from_me = df[ df['kind'] == 'Henryk' ]
    
    """
    calculate scalar values
    - total duration
    - total count
    """
    total_duration_s = df['duration'].sum()
    total_duration_h = total_duration_s / 3600
    total_duration_d = np.floor(total_duration_h / 24)
    total_duration_d_h = total_duration_h - total_duration_d * 24
    date_min = df['date'].min()
    date_max = df['date'].max()
    
    """
    duration of the recordings, group them by day
    and perform moving average on them
    """
    df_duration_by_date = df.groupby('date')['duration'].sum() / 60
    df_duration_by_date =  df_duration_by_date.to_frame()['duration'].to_frame() \
        .rolling(14, closed='both', center=True).mean()
    df_duration_by_date = df_duration_by_date.bfill().ffill() # fill nulls after rolling average
    
    # display(df_duration_by_date)
    
    """
    count of the recordings (per week) 
    and index them by the 'week of' date column
    and next average them by month (4 weeks)
    """
    
    df_count_by_week = df.copy()
    df_count_by_week['week'] = df['date'].dt.strftime('%Y') + '-' + df['date'].dt.strftime('%W')
    df_count_by_week = df_count_by_week.groupby('week').agg({'date':['min'], 'name' : ['count']})
    df_count_by_week = df_count_by_week.droplevel(axis=1, level=1).rename(columns={'name':'count'}) \
        .reset_index().set_index('date').drop('week', axis=1)
    df_count_by_week.iloc[[0,-1],[0]] = None # remove count value from first and last row, because weeks are incomplete
    df_count_by_week = df_count_by_week['count'].to_frame().rolling(1, closed='both', center=True).mean()
    df_count_by_week = df_count_by_week.bfill().ffill() # fill nulls after rolling average
    df_count_by_week['count'] = df_count_by_week['count'].round()
    
    ### STAGE 2 - plot the results
    
    # Define a dictionary of colors for years
    year_colors = {
        2021: '#1f77a4',  # blue
        2022: '#5ca05c',  # green
        2023: '#d65758',  # red
        2024: '#9477bd',  # purple
        2025: '#ff7f0e',  # orange
    }
    
    # Add year to the dataframes
    df_duration_by_date['year'] = df_duration_by_date.index.year
    
    # Create figure and axes
    fig, axs = plt.subplots(2, 1, figsize=(12,8))
    
    # FIRST PLOT: Duration data colored by year
    years = sorted(df_duration_by_date.index.year.unique())
    for year in years:
        # Get data for this year
        year_data = df_duration_by_date[df_duration_by_date.index.year == year]
        color = year_colors.get(year, 'blue')
        
        # Plot points
        axs[0].scatter(year_data.index, year_data['duration'], 
                     linewidth=0.05, s=25, alpha=1, color=color, label=str(year))
        
        # Plot lines
        axs[0].vlines(x=year_data.index, ymin=0, ymax=year_data['duration'], 
                     color=color, alpha=0.8)
    
    # Set properties for the first plot
    axs[0].set_title(f'Długość {len(df)} nagrań od taty dla Henryka od {date_min.date()} do {date_max.date()}' 
                 + '\n' + f'Całkowita długość nagrań wynosi {total_duration_h:,.0f} godzin ({total_duration_d:,.0f} pełnych dni i {total_duration_d_h:.0f} godzin)' )
    axs[0].grid(axis='y')
    axs[0].set_ylabel("Długość nagrań (minuty)")
    axs[0].set_xlabel("Data")
    axs[0].set_xlim((date_min, date_max))
    axs[0].set_ylim(bottom=0)
    axs[0].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))
    axs[0].tick_params(axis='x', labelrotation=45, labelsize=8)
    
    # Create a legend for years
    legend_elements = [Line2D([0], [0], color=year_colors.get(year, 'black'), lw=4, label=str(year)) 
                       for year in years]
    axs[0].legend(handles=legend_elements, loc='lower right', title='Lata')
    
    # SECOND PLOT: Weekly count data colored by year
    # Add year to weekly count dataframe
    df_count_by_week['year'] = df_count_by_week.index.year
    
    # Convert index to matplotlib dates for bar positions
    x_positions = mdates.date2num(df_count_by_week.index)
    
    # Determine bar width based on data - MAKE BARS WIDER
    if len(x_positions) > 1:
        # Calculate average spacing between bars
        avg_spacing = np.mean(np.diff(x_positions))
        # Make bars wider - use 98% of available space between points
        width = avg_spacing * 0.98
    else:
        width = 7  # Default to 7 days if only one data point
    
    # Calculate exact x-axis limits to eliminate margins
    min_date = min(df_count_by_week.index)
    max_date = max(df_count_by_week.index)
    
    # Calculate half bar width in date units to extend the limits exactly to bar edges
    half_width_days = width / 2
    
    # Plot bars with colors by year
    for i, (idx, row) in enumerate(df_count_by_week.iterrows()):
        if not np.isnan(row['count']):
            year = idx.year
            color = year_colors.get(year, 'blue')
            axs[1].bar(x_positions[i], row['count'], width=width, color=color, alpha=0.9, edgecolor='black', linewidth=0.5)
    
    # Set properties for the second plot
    axs[1].set_title(f'Tygodniowa liczba nagrań od taty dla Henryka, ponad {len(df_count_by_week)} tygodni alienacji')
    axs[1].grid(axis='y')
    axs[1].set_ylabel("Ilość nagrań w tygodniu")
    axs[1].set_xlabel("Tydzień")
    
    # Set exact x-axis limits to eliminate margins
    left_limit = mdates.date2num(min_date) - half_width_days
    right_limit = mdates.date2num(max_date) + half_width_days
    axs[1].set_xlim(left_limit, right_limit)
    
    # Set x-axis format for dates
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axs[1].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=14, maxticks=22))
    axs[1].tick_params(axis='x', labelrotation=45, labelsize=8)
    
    # Add legend to the second plot
    axs[1].legend(handles=legend_elements, loc='lower right', title='Lata')
    
    # Disable autoscaling after setting limits
    axs[1].autoscale(enable=False)
    
    # Eliminate any remaining padding
    plt.rcParams['axes.xmargin'] = 0
    
    fig.tight_layout(rect=[0, 0.01, 1, 0.99])
    plt.show()

# EOF