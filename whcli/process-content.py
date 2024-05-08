import json
import sys
import urllib.request
import lib_henryk
from lib_henryk.config import *

token_id = sys.argv[1]
request_id = sys.argv[2]
request_url = f'https://webhook.site/token/{token_id}/request/{request_id}/raw'

with urllib.request.urlopen(request_url) as response:
    json_text = response.read()

# print content but unescape first
json_text = json_text.decode('unicode_escape')
json_content = json.loads(json_text)
transcription_id = json_content['transcription_id']
json_filename = f'{transcription_id}.json'

print(f'transcription_id: {transcription_id}')

# # the json file where the output must be stored 
out_file = open(f'{json_filename}', "w") 
json.dump(json_content, out_file, indent = 4) 
out_file.close() 
