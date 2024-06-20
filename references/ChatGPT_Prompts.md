
## Recordings Classification Prompt

You are a psychologist who analyses transcriptions for the court. 

Attached or provided is a transcription of a recording from father to his 2.5y old son, who dad isn't able to see often. Father meets his son briefly, for just a short while every month or every two months. For various reasons. Can you please analyse the content of a dad's recordings transcritions and generate a classification json according to the schema. Dad will use the classification to submit it to the court and to allow analysis with the data analysis tools

You will classify the transcription using the following json. The json has been provided with the helpful descriptions and instructions for each element.

Technical notes: use 1 for True, 0 for False. For elemenets that are not applicable - use empty string "". For elements that should be a description or overview use up to 50 words and no less than 15.

Provide answer to this prompt as JSON only. No other commens and no acknowledgement.
it the summary and analysis to the court.

Acknowledge the following facts:
- Dad's family: babusia Stenia z krakowa, dziadzius Slawek z krakowa, wujek Michal, ciocia Daniela, wujek Mikolaj, ciocia Marta, kuzyn Arturek, kuzyn Filipek, kuzynka Anastazja
- Dad's friends: wujek Seweryn, ciocia Malgosia, kuzynka Hania, wujek Mungo, wujek Alex and some other uncles and aunts.
- Mom's family: babusia/babcia Teresa z Dobronia. Often when mentioned 'babcia' in the transcription without specifying which babcia is it - father means this babcia.
- Daycare aunts and uncles: ciocia Sylwia, ciocia Martyna, wujek Eryk, wujek Karol


```json
{
  "approach" : {
      "desciption": "for every element in the main json body except for approaches and justifications, provide a chain-of-though explanation how you will approach the classification of each of those elements, example: overall_sentiment, overall_mood, dad_tale_main_theme etc... . Do not include description element in the final document",
      "overall_sentiment": ...,
      "overall_mood": ...,
      ...
  },
  "justification": {
      "why": {
          "description": "this is where you will put justification for all classification items - as to why you have classified them that way. provide justification for all items. use original elements from the main json body here, example: overall_sentiment, overall_mood, dad_tale_main_theme etc... . Do not include description element in the final document",
          "overall_sentiment": ...,
          "overall_mood": ...,
          ...
       },      
       "where": {
          "description": "this is where you will put justification for all classification items - as to where in the text you found the reason to classify element like this. Do not include description element in the final document"
          "overall_sentiment": ...,
          "overall_mood": ...,
          ...
       }
  },
  "overall_sentiment": "positive, rather-positive, negative, rather-negative, or neutral (overall sentiment and tone of the recording)",
  "overall_mood": "sad, melancholic, neutral, happy, sentimental, touched, or enthusiastic (mood of the recording; choose the dominating one; don't use sentimental or touched just because dad misses son, only use those if dad is predominantly sentimental or touched)",
  "dad_tale_main_theme": "Type of theme - people, friends, family, phenomena, places, animals, activities, education, innovation, AI, etc. (Choose a single, reasonably granular item for recordings bucketing). Ignore the fairy tale, it is only about the dads tale, not the fairy tale",
  "dad_tale_topics": "(List of items in JSON style, single words only. Main topics without reference to the fairy tale. These will be used for the tags cloud) . Ignore the fairy tale, it is only about the dads tale, not the fairy tale",
  "dad_love": "true or false (Indicates if dad explicitly expresses love to his son)",
  "dad_longing": "true or false (Indicates if dad explicitly mentions that he misses his son)",
  "mother_mentions": "true or false (Indicates if dad mentions mother, even if only briefly)",
  "mother_family_mentions": "true or false (Indicates if dad mentions mother’s family, even if only briefly. Be careful to distinguish between dad's family and friends and mom's family)",
  "mother_mentions_sentiment": "positive, rather-positive, negative, rather-negative, neutral, or none (Dad's sentiment or tone towards mother; use '' if not mentioned)",
  "mother_family_mentions_sentiment": "positive, rather-positive, negative, rather-negative, neutral, or none (Dad's sentiment or tone towards mother’s family; use '' if not mentioned)",
  "fairy_tale": "true or false (Indicates if dad reads a fairy tale to son)",
  "fairy_tale_theme": "none (if no fairy tale), unspecified (if difficult to determine), winnie the pooh, mis uszatek, dragons, dinosaurs, etc.",
  "motto_sentence": "(Come up with a motto based on dad's tale, in Polish. Avoid overly mentioning love and longing, as it is common in every recording. Make it creative and fun)",
  "dads_tale_overview": "(Short overview of dad's story without the fairy tale, keep it positive and in Polish. Can include a song, poem, or other non-fairy tale elements. In that case provide a short overview of a song or poem) . Ignore the fairy tale, it is only about the dads tale, not the fairy tale",
  "fairy_tale_overview": "(Short overview of the fairy tale told/read by dad, keep it positive and in Polish. Use 'none' if no fairy tale)",
  "other": "(Any additional important details, try to fit data into main elements)",
}

```

Example:

```json
{
  "approach": {
    "overall_sentiment": "Examine the overall tone and language used by the father throughout the recording to determine the general sentiment.",
    "overall_mood": "Identify the predominant mood conveyed by the father, considering emotional expressions and the context of his speech.",
    "dad_tale_main_theme": "Focus on the main subject of the father's storytelling, excluding the fairy tale.",
    "dad_tale_topics": "Extract key topics mentioned in the father's tale using single words for tags.",
    "dad_love": "Determine if the father explicitly expresses love for his son.",
    "dad_longing": "Check for explicit mentions of the father's longing for his son.",
    "mother_mentions": "Identify any mentions of the mother in the recording.",
    "mother_family_mentions": "Identify any mentions of the mother’s family, ensuring correct differentiation from the father’s family.",
    "mother_mentions_sentiment": "Assess the father's tone when mentioning the mother.",
    "mother_family_mentions_sentiment": "Assess the father's tone when mentioning the mother’s family.",
    "fairy_tale": "Determine if a fairy tale is read or told.",
    "fairy_tale_theme": "Identify the theme of the fairy tale if mentioned.",
    "motto_sentence": "Create a motto based on the father's tale, making it creative and fun.",
    "dads_tale_overview": "Provide a brief, positive overview of the father's story excluding the fairy tale.",
    "fairy_tale_overview": "Provide a brief, positive overview of the fairy tale read or told by the father.",
    "other": "Include any additional important details."

  },
  "justification": {
    "why": {
      "overall_sentiment": "The father's language is affectionate and positive, despite expressing longing, indicating an overall positive sentiment.",
      "overall_mood": "The father's mood is predominantly sentimental, as he often expresses deep feelings of missing and loving his son.",
      "dad_tale_main_theme": "The main theme of the father's storytelling revolves around dinosaurs.",
      "dad_tale_topics": "The father discusses various topics including dinosaurs, family, love, longing, and meeting.",
      "dad_love": "The father frequently expresses his love for his son throughout the recording.",
      "dad_longing": "The father explicitly mentions how much he misses his son several times.",
      "mother_mentions": "The father mentions the mother when discussing future plans and current circumstances.",
      "mother_family_mentions": "There are no mentions of the mother's family in the transcription.",
      "mother_mentions_sentiment": "The father's tone towards the mother is positive when she is mentioned.",
      "mother_family_mentions_sentiment": "Not applicable as the mother's family is not mentioned.",
      "fairy_tale": "The father reads a fairy tale about dinosaurs to his son.",
      "fairy_tale_theme": "The theme of the fairy tale is dinosaurs.",
      "motto_sentence": "The motto captures the key elements of the father's message: dinosaurs, kites, and his love and longing.",
      "dads_tale_overview": "The overview focuses on the father's account of his day, his emotions, and future plans with his son.",
      "fairy_tale_overview": "The overview summarizes the fairy tale about diplodoks and other dinosaurs.",
      "other": "No additional details were necessary."
    },
    "where": {
      "description": "this is where you will put justification for all classification items - as to where in the text you found the reason to classify element like this. Do not include description element in the final document",
      "overall_sentiment": "The affectionate and hopeful language used throughout the transcript.",
      "overall_mood": "Repeated expressions of longing and love, such as 'bardzo bardzo za Tobą tęsknię' and 'tak bardzo Cię kocham'.",
      "dad_tale_main_theme": "Frequent discussions about dinosaurs, such as 'Dinozaury Henryczku przypominają smoki z opowieści'.",
      "dad_tale_topics": "Mentions of various topics including family, love, and longing, such as 'tęsknię za Tobą' and 'będziemy robić latawce'.",
      "dad_love": "Direct statements of love, e.g., 'kocham Cię'.",
      "dad_longing": "Explicit mentions of missing his son, e.g., 'bardzo za Tobą tęsknię'.",
      "mother_mentions": "'Mama i tata próbujemy zrobić wszystko Henryczku żebyś mógł mieć na z oboje'.",
      "mother_family_mentions": "No mentions of the mother’s family were found.",
      "mother_mentions_sentiment": "Positive mention of mother, e.g., 'Mama pokaże Ci co to jest latawiec'.",
      "mother_family_mentions_sentiment": "Not applicable.",
      "fairy_tale": "'A teraz Henryczku teraz przeczytam Ci kolejną bajkę o dinozaurach'.",
      "fairy_tale_theme": "'ta bajka nosi tytuł Mam książkę przy sobie Henryczku'.",
      "motto_sentence": "Based on the recurring themes of dinosaurs, kites, and expressions of love.",
      "dads_tale_overview": "Summarized from the father's narrative, such as 'Tata opowiada Henryczkowi o swoim dniu...'.",
      "fairy_tale_overview": "'Tata czyta bajkę o diplodokach i innych dinozaurach'.",
      "other": "No additional details were necessary."
    }
  },
  "overall_sentiment": "positive",
  "overall_mood": "sentimental",
  "dad_tale_main_theme": "dinosaurs",
  "dad_tale_topics": ["dinosaurs", "family", "love", "longing", "meeting"],
  "dad_love": 1,
  "dad_longing": 1,
  "mother_mentions": 1,
  "mother_family_mentions": 0,
  "mother_mentions_sentiment": "positive",
  "mother_family_mentions_sentiment": "",
  "fairy_tale": 1,
  "fairy_tale_theme": "dinosaurs",
  "motto_sentence": "Dinozaury, latawce i nasze chwile razem – kto wie co się może zdarzyć!",
  "dads_tale_overview": "Tata opowiada Henryczkowi o swoim dniu, tęsknocie za synem i planach na wspólne zabawy z kuzynami. Opowiada także o dinozaurach.",
  "fairy_tale_overview": "Tata czyta bajkę o diplodokach i innych dinozaurach, opisując ich życie i zabawy.",
  "other": ""
}
```



## Transcription Summary

Summarize the attached recording from father to son, but create the summary in the form of a teaser that, with its tone, will encourage the child to listen to the whole thing. Keep the summary in a light tone and language friendly to a 3-year-old child.  

Do's:
- Use 1st person in the summary i.e. "Opowiadam o ..."
- Create the summary in Polish.
- The entire summary should not exceed 160 words.
- Provide chain-of-thought as "justification" before you produce the "transcription_overview_dad_perspective"
- Chain-of-thought should explain your reasoning vs. the instructions in the prompt

Don't-s
- Do not address son or anyone directly, make summary more passive, i.e. do not say "krzyczałem do ciebie" or "widziałem ciebie", those address son directly.
- Do not provide too many details of the stories told
- Do not say things like "kocham Cię" or "tęsknię za tobą" without specific context. They appear too often.

Produce the result only as JSON code, do not produce any other content.

Below is the json template:

```json
{
    "justification": {
        "tone_and_language": "...",
        "passive_narration": "..."
        "first_person_perspective": "...",
        "encouraging_listening": "...",
        "brevity": "..."
    },
    "summary": "..."
}
```

Below are examples (without justification, but you must provide justification):

Example 1:
```json
{
	"summary": "W tym nagraniu opowiadam o dniu, kiedy widziałem swojego synka. Opowiadam, jak bardzo tęskniłem za nim i jak mocno chciałem go przytulić. Widzieliśmy się tylko na chwilkę, a obok byli policjanci, którzy pomogli nam się zobaczyć.  Mówię też o planach na przyszłość, że może następnym razem zobaczymy się na dłużej. Opowiadam, jak bardzo kocham swojego synka i że mama i tata robią wszystko, aby mógł spędzać czas z obojgiem rodziców. Wspominam również, jak spędzam czas z jego kuzynami i jak będziemy robić latawce. Obiecuję, że kiedy Henryczek będzie starszy, będziemy robić latawce razem i puszczać je na Błoniach Krakowskich. Na koniec, opowiadam o dinozaurach, które przypominają smoki. Mówię, jak dawno temu żyły te ogromne stworzenia i jak wyglądał wtedy świat. Wspominam różne rodzaje dinozaurów, ich wielkość i zwyczaje. Czytam bajkę o diplodokach, które przystanęły na polanie, aby odpocząć. Mam nadzieję, że te bajki spodobają się Henryczkowi, i obiecuję, że będziemy rysować i kolorować dinozaury razem."
}
```

Example 2:
```json
{
    "summary": "W tym nagraniu opowiadam o niezwykłym kamperze, czyli domu na kółkach, który mają babusia i dziadziuś Henryczka. Wyobraź sobie, że można nim jeździć wszędzie, a w środku jest wszystko, co w prawdziwym domu – łóżko, stolik, lampka i nawet toaleta! Opowiadam, jak z Henryczkiem będziemy mogli razem podróżować tym kamperem na Mazury, gdzie jest dużo jezior i łódek. Opowiadam też o tym, jak chciałbym by Henryczek zobaczył wielką jaskinię Smoczą Jamę pod zamkiem na Wawelu. Na końcu czytam synkowi bajeczkę o misiu Uszatku, który uczy się pływać dzięki rakowi.  Dużo ciekawych przygód, o których chętnie opowiadam!"
}
```

Example 3:

```json
{
    "justification": {
        "tone_and_language": "Używam ciepłego i zachęcającego tonu oraz prostego języka, aby był przyjazny dla trzylatka.",
        "passive_narration": "Unikam bezpośrednich zwrotów do dziecka, zamiast tego stosuję opisy w trzeciej osobie.",
        "first_person_perspective": "Stosuję narrację w pierwszej osobie, aby wciągnąć dziecko w opowieść.",
        "encouraging_listening": "Podkreślam ciekawe fragmenty i obietnicę zabawnych historii, aby zachęcić do słuchania.",
        "brevity": "Podsumowanie jest krótkie, zwięzłe i obejmuje najważniejsze punkty bez nadmiaru szczegółów."
    },
    "summary": "W tym nagraniu opowiadam o dniu pełnym podróży, kiedy odwiedziłem Warszawę. Opowiadam o książce 'Zima na ulicy Czereśniowej' pełnej kolorowych obrazków, gdzie ludzie jeżdżą na saneczkach i noszą choinki. Jest tam wiele ciekawych postaci, jak śpiewający pan i grająca na skrzypcach pani. Opowiadam historię o babci, która znalazła choinkę, oraz czytam bajeczki o misiu Uszatku – jak króliczek pobrudził podłogę i jak ciasto próbowało uciec. To wszystko to wspaniałe opowieści, które czekają na odkrycie!"
}
```
