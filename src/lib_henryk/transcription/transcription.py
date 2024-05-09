import requests
import pandas as pd
import os
import shutil
import io
import json
import math

import subprocess

# local imports
from lib_henryk.logger import *
from lib_henryk.config import *


def submit_transcriptions_goodtape( df: pd.DataFrame, webhooks_token_id, goodtape_api_key, path_recordings, start=0, stop=None, verbose=False ):        
    # create new column if needed
    if not 'transcription_id' in  df.columns.to_list():
        df['transcription_id'] = None
        
    # set up callback
    token_id = webhooks_token_id
    callback_url = f'https://webhook.site/{token_id}'
    
    # load just few records
    counter=0
    for index, row in df[start:stop].iterrows():
        file_path = path_recordings + '/' + row['path']
        file_name = row['file']
        transcription_id = row['transcription_id']
    
        # run transcription API if needed, only if transcription wasn't made already
        if pd.isna(transcription_id) == True:
            file_name_max_length = 100
            file_name_truncated = file_name
            if len(file_name) > file_name_max_length:
                file_name_truncated = file_name[0:file_name_max_length] + "..."            
            print(f'processing [{index}]: {file_name_truncated}')

            # copy file to /tmp, curl has issue with some paths
            temp_ext = file_name.split('.')[-1]
            temp_path = f'/tmp/recording.{temp_ext}'
            shutil.copy(file_path, temp_path)

            # perform transcription via API & CURL        
            response = subprocess.check_output(
                f'curl -s -X POST "https://api.goodtape.io/transcribe"' \
                + f' -H "Authorization: {goodtape_api_key}"' \
                + f' -F "audio=@{temp_path}"' \
                + f' -F "callbackUrl={callback_url}"' \
                + f' -F "languageCode=pl"' \
                + f' -F "speakerLabels=true"' \
                + f' -F "timeStamps=false"' 
            , shell=True, ) 

            # verify and write down the response
            try:
                response_json = json.loads(response)
                transcription_id = response_json['transcriptionId']
                df.loc[index, 'transcription_id'] = transcription_id
                if verbose:
                    print(f'file [{index}]: {transcription_id}')
                counter+=1
            except:
                print(response)
                break
        else:
            if verbose:
                print(f'file [{index}]: {file_name} already submitted')
    
    print(f'submitted {counter} recordings to the transcription service GoodTape')


def retrieve_responses_goodtape_via_webhooks(df, webhooks_token_id, path_transcriptions_json):
    # create new column if needed
    if not 'transcription_json' in  df.columns.to_list():
        df['transcription_json'] = None
        
    # use webhooks.site API to pull latest requests list
    headers = {}
    r = requests.get('https://webhook.site/token/'+ webhooks_token_id +'/requests?sorting=newest', headers=headers)
    print(f'found {len(r.json()["data"])} requests to fetch')
    
    # process requests one by one
    counter=0
    for i, request in enumerate(r.json()['data']):
        # fetch the data         
        response = requests.get(f'https://webhook.site/token/{webhooks_token_id}/request/{request["uuid"]}/raw')
        json_content = response.json()
        transcription_id = json_content['transcription_id']

        # before we write the file, let's just check if
        # we have a corresponding transcription_id in the database
        idx = df[df['transcription_id']==transcription_id].index
        if idx == None: 
            continue
        else:
            file_name = df.loc[idx[0]]['file']
            file_index = idx[0]
            file_name_max_length = 64
            file_name_name_truncated = file_name
            file_name_without_ext = ".".join(file_name.split(".")[:-1])
            file_name_json = f'{file_name_without_ext}.json'
            path_json = f'{path_transcriptions_json}/{file_name_json}'
            if len(file_name) > file_name_max_length:
                file_name_truncated = file_name[0:file_name_max_length] + "..."
    
        # write json file
        with open(f'{path_json}', "w") as file: 
            json.dump(json_content, file, indent = 4) 
            file.close() 
    
        # mark as done in the transcription log
        df.loc[file_index, 'transcription_json'] = file_name_json
        print(f'retrieved transcription [{i}]: {transcription_id} -> file [{file_index}]: {file_name_truncated}')
        counter+=1
        
        # clean up this request as it was fetched
        response = requests.delete(f'https://webhook.site/token/{webhooks_token_id}/request/{request["uuid"]}')
    
    # print message that we are done
    print(f'{counter} transcriptions were retrieved')


def process_transcriptions_json_to_text(df, path_transcriptions_json, path_transcriptions_txt, verbose=False):
    # create new column if needed
    if not 'transcription_txt' in  df.columns.to_list():
        df['transcription_txt'] = None
    
    # iterate over records and process files
    counter=0
    for index, row in df.iterrows():
        file_name = row['file']
        file_name_without_ext = '.'.join(row['file'].split('.')[:-1])
        transcription_id = row['transcription_id']
        file_name_json = row['transcription_json']
        path_json = f'{path_transcriptions_json}/{file_name_json}'
        file_name_txt = f'{file_name_without_ext}.txt'
        path_txt = f'{path_transcriptions_txt}/{file_name_txt}'

        # failover in case json is not available
        if pd.isna(file_name_json) or (os.path.exists(path_json) == False): 
            continue        
        
        # skip if processed already
        if os.path.exists(path_txt):
            if verbose:
                print(f'file [{index}]: {file_name_json} was already processed')
            continue
        else:
            counter+=1
        
        # open json file
        json_content = json.load(open(path_json, 'r'))
        transcription_text = json_content['content']['text']
        
        # write to the final destination
        with open(path_txt, 'w') as file:
            file.write(file_name_without_ext + '\n\n')
            file.write(transcription_text.strip())
            file.close()

        # mark processing in the dataframe
        if verbose:
            print(f'processed [{index}]: {file_name_txt}')
        df.loc[index, 'transcription_txt'] = file_name_txt
    
    # print message that we are done
    print(f'{counter} new transcriptions were processed, there are {len(df[df["transcription_txt"].notnull()])} transcriptions available')


def cleanup_missing_transcriptions(df, path_transcriptions_json, path_transcriptions_txt):
    # find records to clean, we are probably waiting for a number of 
    # transcription responses - but the quota on webhooks.site might have been exceeded
    counter=0
    for index, row in df.iterrows():
        file_name_text = row['transcription_txt']
        file_name_json = row['transcription_json']
        path_json = f'{path_transcriptions_json}/{file_name_json}'
        path_text = f'{path_transcriptions_txt}/{file_name_text}'

        # check values and files
        if (pd.isna(file_name_text) == False) and (pd.isna(file_name_json) == False) \
        and (os.path.exists(path_json) == True) and (os.path.exists(path_text) == True):
            counter+=1
        # if record is invalid, clean up
        else:
            df.loc[index, 'transcription_id'] = None
            df.loc[index, 'transcription_txt'] = None
            df.loc[index, 'transcription_json'] = None

    print(f'there are {counter} processed and valid transcriptions')

# EOF
