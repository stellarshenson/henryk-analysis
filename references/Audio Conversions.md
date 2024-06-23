
## code to convert any audio file to a segment

```python
from pydub import AudioSegment 
song = AudioSegment.from_file(file_to_transcribe, format='m4a')
```

## code to truncate file to 10% length

```python
import io
song_truncated = song[0:int(len(song)*0.1)]
buffer = io.BytesIO()
song_truncated.export(buffer, format='mp3')
file_to_transcribe = 'sample.mp3'
```

