# Transcriptions Recordings Analysis

## Columns

```python
columns = df_stats.columns
for c in columns:
    print(f"- **{c}** ({df_stats[c].dtype}): ")

```

- **name** (object): name of the recording, string
- **date** (object): date of the recording YYYY-MM-DD
- **classification.overall_sentiment** (object): string, categorical
- **classification.overall_mood** (object): string, categorical
- **classification.dad_tale_main_theme** (object): string, categorical
- **classification.dad_tale_topics** (object): string, comma separated list of values
- **classification.dad_love** (float64): 1 or 0
- **classification.dad_longing** (float64):  1 or 0
- **classification.mother_mentions** (int64):  1 or 0
- **classification.mother_family_mentions** (int64): string, categorical
- **classification.mother_mentions_sentiment** (object):  string, categorical
- **classification.mother_family_mentions_sentiment** (object):  string, categorical
- **classification.fairy_tale** (int64): string, unique
- **classification.fairy_tale_theme** (object):  string, categorical
- **classification.motto_sentence** (object):  string, unique
- **classification.dads_tale_overview** (object):  string, unique
- **classification.fairy_tale_overview** (object): string, unique
- **classification.other** (object): string, unique, sparse
- **classification.privacy_concern** (float64): 1 or 0
- **classification.privacy_concern_type** (object): string, comma separated list of values, sparse


