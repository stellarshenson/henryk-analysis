## Recordings Classification Prompt

Attached or provided is a transcription of a recording from father to his 2.5y old son, who dad isn't able to see often. Father meets his son briefly, for just a short while every month or every two months. For various reasons. Can you please analyse the content of a dad's recordings transcritions and generate a classification json according to the schema. Dad will use the classification to submit the summary and analysis to the court.

```json
{
  "sentiment": "positive, rather-positive, negative, rather-negative, or neutral",
  "why_sentiment": "explain briefly why such sentiment, use polish language (LLM audit)",
  "mood": "sad, melancholic, neutral, happy, sentimental, touched, or enthusiastic (choose the dominating one; don't use sentimental or touched just because dad misses son, only use those if dad is predominantly sentimental or touched)",
  "why_mood": "explain briefly why such mood, use polish language (LLM audit)"
  "dad_tale_main_theme": "Type of theme - people, friends, family, phenomena, places, animals, activities, education, innovation, AI, etc. (Choose a single, reasonably granular item for recordings bucketing)",
  "dad_tale_topics": "(List of items in JSON style, single words only. Main topics without reference to the fairy tale. These will be used for the tags cloud)",
  "dad_love": "true or false (Indicates if dad explicitly expresses love to his son)",
  "dad_miss": "true or false (Indicates if dad explicitly mentions that he misses his son)",
  "mother": "true or false (Indicates if dad mentions mother, even if only briefly)",
  "where_mother": "Short, but not too short a reference to the context in which mother was mentioned, in Polish (LLM audit)",
  "mother_family": "true or false (Indicates if dad mentions mother’s family, even if only briefly. Be careful to distinguish between dad's family and friends and mom's family)",
  "where_mother_family": "Short, but not too short a reference to the context in which mother’s family was mentioned, in Polish (LLM audit)",
  "mother_sentiment": "positive, rather-positive, negative, rather-negative, neutral, or none (Dad's sentiment or tone towards mother; use 'none' if not mentioned)",
  "why_mother_sentiment": "explain briefly why such sentiment, none if not mentioned",
  "mother_family_sentiment": "positive, rather-positive, negative, rather-negative, neutral, or none (Dad's sentiment or tone towards mother’s family; use 'none' if not mentioned)",
  "why_mother_family_sentiment": "explain briefly why such sentiment, none if not mentioned",
  "fairy_tale": "true or false (Indicates if dad reads a fairy tale to son)",
  "fairy_tale_theme": "none (if no fairy tale), unspecified (if difficult to determine), winnie the pooh, mis uszatek, dragons, dinosaurs, etc.",
  "motto_sentence": "(Come up with a motto based on dad's tale, in Polish. Avoid overly mentioning love, as it is common in every recording)",
  "dads_tale_overview": "(Short overview of dad's story without the fairy tale, keep it positive and in Polish. Can include a song, poem, or other non-fairy tale elements. In that case provide a short overview of a song or poem)",
  "fairy_tale_overview": "(Short overview of the fairy tale told/read by dad, keep it positive and in Polish. Use 'none' if no fairy tale)",
  "other": "(Any additional important details, try to fit data into main elements)"
}

```

- Dad's family: babusia Stenia z krakowa, dziadzius Slawek z krakowa, wujek Michal, ciocia Daniela, wujek Mikolaj, ciocia Marta, kuzyn Arturek, kuzyn Filipek, kuzynka Anastazja
- Dad's friends: wujek Seweryn, ciocia Malgosia, kuzynka Hania. Also wujek Mungo, wujek Alex and other wujki.
- Mom's family: babusia (or babcia) Teresa z Dobronia. Double check if she was not mentioned.

Return just json, no additional content or acknowledgement