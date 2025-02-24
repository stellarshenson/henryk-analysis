import os
import openai
import pandas as pd
import json
import time
import pathlib

# for un-makrdowning the text from openai
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain
from json_repair import repair_json
from names_generator import generate_name

from lib_henryk.config import *
from lib_henryk.logger import *
from lib_henryk import utils
from lib_henryk.recordings import transcriptions


class Transcription_Classifier():
    """
    A class to handle transcription classification using OpenAI's GPT models.

    Attributes:
    -----------
    unmarkdown_parser : MarkdownIt
        Parser to remove markdown from responses.
    client : openai.OpenAI
        OpenAI API client.
    df_transcriptions_classifications : pd.DataFrame
        DataFrame to store transcription classification results.
    temp_df_transcriptions_classifications_parquet : str
        Temporary file path to save intermediate results.
    assistant : openai.types.beta.assistant.Assistant
        OpenAI assistant instance.
    assistant_name : str
        Name of the assistant.
    model : str
        OpenAI model to use.
    prompt_recording_classification : str
        Prompt for recording classification.
    messages : list
        List of messages from the model.
    run : openai.types.beta.threads.Run
        Run object for model execution.
    thread : openai.types.beta.threads.Thread
        Thread object for interaction.
    response_md : str
        Response in markdown format.
    response_json : dict
        Response in JSON format.
    __in_progress : bool
        Flag to indicate if classification is in progress.
    __inference_settings : dict
        Settings for inference.

    Methods:
    --------
    __init__(api_key: str, model: str = 'gpt-4o', assistant_name: str = 'Professor Hendrickson', df_transcriptions_classifications: pd.DataFrame = None):
        Initializes the Transcription_Classifier with the provided parameters.

    initialise_prompt(prompt_file_path: str):
        Loads the classification prompt and initializes the assistant.

    perform_classification(df_transcriptions: pd.DataFrame, df_transcriptions_classifications: pd.DataFrame = None, cooldown_frequency: int = 4, cooldown_seconds: int = 5, retry: int = 3, verbose: bool = False):
        Performs classification on the provided transcriptions DataFrame.

    reset_assistant():
        Resets the assistant by deleting the current instance.

    __inference(transcription: str, thread, assistant) -> dict:
        Performs inference on the provided transcription.

    __save_classification_response(messages_dict: dict, name: str):
        Saves the classification response to the DataFrame.

    save_classification_parquet(path: str, override: bool = False):
        Saves the classification results to a parquet file.

    __retrieve_assistant(assistant_name: str) -> openai.types.beta.assistant.Assistant:
        Retrieves the assistant by name if it exists.
    """

    
    def __init__(
        self, 
        api_key:str,
        model:str = 'gpt-4o',
        assistant_name:str='Professor Hendrickson',
        df_transcriptions_classifications:pd.DataFrame=None,
    ):
        """
        Initializes the Transcription_Classifier with the provided parameters.

        Parameters:
        -----------
        api_key : str
            API key for OpenAI.
        model : str
            OpenAI model to use for classification (default is 'gpt-4o').
        assistant_name : str
            Name of the assistant (default is 'Professor Hendrickson').
        df_transcriptions_classifications : pd.DataFrame, optional
            DataFrame to store transcription classification results.
        """
        # parser for un-markdowning responses
        self.unmarkdown_parser = MarkdownIt(renderer_cls=RendererPlain)

        # load openai client and create assistant
        self.client = openai.OpenAI(api_key=api_key)

        # prepare transcription_classification dataframe
        if df_transcriptions_classifications is not None:
            seld.df_transcriptions_classifications = df_transcriptions_classifications.reset_index(drop=True).copy()
        else:
            self.df_transcriptions_classifications = pd.DataFrame({
                "name": [],
                "classification_json": []
            })

        # temp file to save results just in case - openai is expensive
        # every time this will be a different name - to make sure one invocation
        # doesn't accidently overwrite previous results. clever, ha? lost 20 bucks this way...
        self.temp_dataset_file_prefix = f"/tmp/temp_"
        
        # assistant (will be provided later)
        self.assistant = None
        self.assistant_name = assistant_name
        self.model = model

        # prompt (will be loaded later)
        self.prompt_recording_classification = None

        # runtime objects from model
        self.messages = None
        self.run = None
        self.thread = None
        self.response_md = None
        self.response_json = None
        self.__in_progress = False
        self.__inference_settings = {}
        self.stats = None

    def initialise_prompt(self, prompt_file_path: str=FILE_PROMPT_RECORDING_CLASSIFICATION):
        """
        Loads the classification prompt and initializes the assistant.

        Parameters:
        -----------
        prompt_file_path : str
            Path to the file containing the prompt for recording classification.
        """
 
        # load prompts
        self.prompt_recording_classification = open(FILE_PROMPT_RECORDING_CLASSIFICATION, 'r').read()

        # attempt retrieval of an assistant
        self.assistant = self.__retrieve_assistant(assistant_name=self.assistant_name)
        
        # initialise assistant if not loaded
        if self.assistant is None:
            self.assistant = self.client.beta.assistants.create(
                name=self.assistant_name,
                instructions=self.prompt_recording_classification,
                model=self.model,
            )

        
    def perform_classification(
        self, 
        df_transcriptions: pd.DataFrame, 
        df_transcriptions_classifications: pd.DataFrame = None, 
        cooldown_frequency:int=4,
        cooldown_seconds:int=5, 
        retry=3,
        verbose=False,
    ):
        """
        Performs classification on the provided transcriptions DataFrame.
        
        This method processes each transcription in `df_transcriptions`, checks if it has already 
        been classified based on the provided `df_transcriptions_classifications` DataFrame, 
        and performs classification if it hasn't. It employs cooldowns to manage API rate limits 
        and retries in case of failures.
        
        Parameters:
        -----------
        df_transcriptions : pd.DataFrame
            DataFrame containing the transcriptions to classify. It must have 'name' and 'transcription' columns.
        df_transcriptions_classifications : pd.DataFrame, optional
            DataFrame containing existing classification results to skip already processed transcriptions. 
            It must have 'name' and 'classification_json' columns.
        cooldown_frequency : int
            Frequency of cooldown periods during processing to avoid hitting rate limits (default is 4).
        cooldown_seconds : int
            Duration of each cooldown period in seconds (default is 5).
        retry : int
            Number of retries for inference on failure (default is 3).
        verbose : bool
            Flag to enable verbose logging (default is False).
        
        Usage:
        ------
        To classify new transcriptions while skipping already classified ones:
        >>> classifier = Transcription_Classifier(api_key="your_api_key")
        >>> classifier.initialise_prompt(prompt_file_path=FILE_PROMPT_RECORDING_CLASSIFICATION)
        >>> classifier.perform_classification(df_transcriptions=new_transcriptions_df, 
                                              df_transcriptions_classifications=existing_classifications_df)
        
        The method processes each row in `df_transcriptions` and checks if the 'name' already exists 
        in `df_transcriptions_classifications`. If it does, it skips the row. Otherwise, it performs 
        classification using the OpenAI model, manages API rate limits with cooldowns, and retries 
        the inference in case of failures. Intermediate results are saved to a temporary parquet file 
        to avoid data loss in case of interruptions.
        
        Raises:
        -------
        Exception:
            If classification cannot be completed after the specified number of retries.
        """
        # generate new temp file name
        self.temp_df_transcriptions_classifications_parquet = f"{self.temp_dataset_file_prefix}{generate_name()}.parquet"
        
        # disclaimer
        logger.info(f'intermediate classification results will be written to {self.temp_df_transcriptions_classifications_parquet}')

        
        # if df_transcriptions_classifications is provided, set it as current
        if df_transcriptions_classifications is not None and self.__in_progress == False:
            self.df_transcriptions_classifications = df_transcriptions_classifications.reset_index(drop=True).copy()
            
            # requested vs completed stats
            stats = self.__get_completed_vs_requested_stats(df_transcriptions, self.df_transcriptions_classifications)
            logger.info(f'found {stats["num_completed"]} ({stats["num_requested_completed"]} from current request) existing classifications, those will not be processed.')
        elif df_transcriptions_classifications is not None and self.__in_progress == True:
            logger.warning(f'unable to provide initial classification dataset, classification is in progress')

        # set in progress flag - to protect dataset against consecutive executions
        self.__in_progress = True
        
        # print(f'0 --- {len(self.df_transcriptions_classifications)} ---')
        
        # initialise thread
        self.thread = self.client.beta.threads.create()

        # iterate over records in the dataframe and generate classification
        cooldown_counter = 0
        for i, (index, row) in enumerate(df_transcriptions.iterrows()):
            # prepare transcription to classify
            transcription = row['transcription']
            name = row['name'] # key
            name_truncated = utils.get_truncated_string(name, 64)

            # iteration stats
            stats = self.__get_completed_vs_requested_stats(df_transcriptions, self.df_transcriptions_classifications)
            progress_bar_prefix = f'classifying {stats["num_requested_completed"]:3}/{stats["num_requested"]} transcriptions'
            # print(f'1 --- {len(self.df_transcriptions_classifications)} ---')
            
            # check if this transcription has not been classified yet, we want this before cooldown
            if self.df_transcriptions_classifications[self.df_transcriptions_classifications['name'] == name].empty == False:
                if verbose:
                    logger.info(f'ignoring transcription [{index}] {name_truncated}')
                continue
            
            ######## COOLDOWN ##########
            
            # cooldown and wait every cooldown_frequency times
            cooldown_counter+=1 # increment just before check - so that iteration [0] wouldn't trigger cooldown
            if cooldown_frequency > 0 and cooldown_counter % cooldown_frequency == 0:
                if verbose == True: 
                    logger.info(f'COOLDOWN, iteration [{i}]')
                else:
                    progressBar(i, len(df_transcriptions), prefix=progress_bar_prefix, suffix=f'{"*** COOLDOWN ***":72}',length=40)
                time.sleep(cooldown_seconds) # cool down for a few seconds
                self.client.beta.threads.delete(self.thread.id) # delete previous thread
                self.thread = self.client.beta.threads.create() # start new thread, in new retry new thread will be used

            # print(f'2 --- {len(self.df_transcriptions_classifications)} ---')
            
            # feedback progress bar
            if verbose:
                logger.info(f'processing transcription [{index}] {name_truncated}')
            else:
                progressBar(i, len(df_transcriptions), prefix=progress_bar_prefix, suffix=f'[{index:3}] {name_truncated:64}',length=40)

            ######## INFERENCE ##########

            # inference is executed in a retry loop so that when inference fails,
            # additional measures - including number of retries can be used
            for retry_count in range(retry):                
                # run inference in a retry loop
                messages_dict = self.__inference(
                    transcription=transcription,
                    thread = self.thread,
                    assistant= self.assistant
                )
                
                # retrieve messages only if completed
                if messages_dict is not None:
                    self.__save_classification_response(messages_dict=messages_dict, name=name)
                    break # break the retry loop to next iteration
                # otherwise di retries and fail if retry didn't work
                elif retry_count < retry:
                    if verbose:
                        logger.info(f'retry no {retry_count} [{index}] {name_truncated}')
                    else:                
                        progressBar(i, len(df_transcriptions), prefix=progress_bar_prefix, suffix=f'{"*** RETRY ["}{retry_count}{"] ***":54}',length=40)
                    time.sleep(cooldown_seconds) # cooldown
                    self.client.beta.threads.delete(self.thread.id) # delete previous thread
                    self.thread = self.client.beta.threads.create() # start new thread, in new retry new thread will be used
                else:
                    raise Exception(f"unable to complete, run status: {run.status}")
    
        # finish progress bar
        progressBar(1, 1, prefix=f"classifying {len(df_transcriptions)} transcriptions", suffix=f'{"done.":72}', length=40)

        # find if all classifications were completed
        stats = self.__get_completed_vs_requested_stats(df_transcriptions, self.df_transcriptions_classifications)

        if stats["num_requested_completed"] == stats["num_requested"]:
            if stats["num_completed"] > stats["num_requested"]:
                logger.info(f'more ({stats["num_completed"]}) classifications than requested, classifier was executed before on different dataset ')
            logger.info(coloured_text(f'*** all {stats["num_requested"]} requested transcriptions classifications were completed ***', 'green'))
        else:
            logger.info(f'there are still {stats["num_remaining"]} missing requested classifications')

    
    def __get_completed_vs_requested_stats(self, df_requested: pd.DataFrame, df_completed: pd.DataFrame) -> dict:
        requested_names = set(df_requested['name'].to_list())
        completed_names = set(df_completed['name'].to_list())
        requested_completed_names = requested_names & completed_names
        remaining_names = requested_completed_names ^ requested_names
        num_requested = len(requested_names)
        num_completed = len(completed_names)
        num_requested_completed = len(requested_completed_names)
        num_remaining = len(remaining_names)

        self.stats = {
            "requested_names": requested_names,
            "completed_names": completed_names,
            "requested_completed_names": requested_completed_names,
            "remaining_names": remaining_names,
            "num_requested": num_requested,
            "num_completed": num_completed,
            "num_requested_completed": num_requested_completed,
            "num_remaining": num_remaining,
        }
        return self.stats


    def get_stats(self) -> dict:
        return self.stats

    
    def reset_assistant(self):
        """
        Resets the assistant by deleting the current instance.
        """
        if self.assistant != None:
            self.client.beta.assistants.delete(self.assistant.id)
    
    def __inference(
        self,
        transcription:str,
        thread,
        assistant,
    ) -> dict:
        """
        Performs inference on the provided transcription.
        
        Parameters:
        -----------
        transcription : str
            The transcription text to be classified.
        thread : openai.types.beta.threads.Thread
            The thread object for interaction.
        assistant : openai.types.beta.assistant.Assistant
            The assistant object for classification.
        
        Returns:
        --------
        dict
            The inference result as a dictionary.
        """
        # prepare message
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Please process the following transcription:\n{transcription}",
        )

        # run the message and inference, save run to class variable for inspection
        self.run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.assistant.id,
        )

        # retrieve messages only if completed, save message to a class variable for inspection
        if self.run.status == "completed":
            self.messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            return self.messages.to_dict()
        else:
            return None

    
    def __save_classification_response(self, messages_dict: dict, name: str):
        """
        Saves the classification response to the DataFrame.

        Parameters:
        -----------
        messages_dict : dict
            Dictionary containing the classification response.
        name : str
            The name associated with the transcription - used as key in all other datasets
        """
        # get the response
        self.response_md = messages_dict['data'][0]['content'][0]['text']['value']

        # un-markdown parser for text received from openai
        response_text = self.unmarkdown_parser.render(self.response_md)
        repaired_response_text = repair_json(response_text) # just in case apply repairs to json
        self.response_json = json.loads(repaired_response_text)

        # put response in the classification dataframe
        row = pd.DataFrame({ "name": [name], "classification_json": [json.dumps(self.response_json)]})
        logger.debug(f"adding new record to the dataset, it has currently {len(self.df_transcriptions_classifications)} entries")
        self.df_transcriptions_classifications = pd.concat([self.df_transcriptions_classifications, row], ignore_index=True) # proper way of adding rows

        # save the dataframe
        logger.debug(f"writng intermediate result to {self.temp_df_transcriptions_classifications_parquet}, it has now {len(self.df_transcriptions_classifications)} entries")
        self.df_transcriptions_classifications.to_parquet(self.temp_df_transcriptions_classifications_parquet)    
    
    def save_classification_parquet(self, path:str = FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET, override:bool=False):
        """
        Saves the classification results to a parquet file.

        Parameters:
        -----------
        path : str
            The file path to save the classification results.
        override : bool
            Flag to allow overriding an existing file.
        """
        logger.info(f"saving {len(self.df_transcriptions_classifications)} classification results to to {path}")

        # sanity  check if we have more results than in the existing file
        if pathlib.Path(path).is_file():
            df_old = pd.read_parquet(path)
            logger.info(f'found older file with the same name, checking the older file size vs new...')

            if len(df_old) > len(self.df_transcriptions_classifications):
                logger.warning(f'older file has more records ({len(df_old)}) than new ({len(self.df_transcriptions_classifications)})')

                if override == True:
                    logger.info(f'[override] replacing older file with new one')
                    self.df_transcriptions_classifications.to_parquet(path)
                    return
                else:
                    logger.error('new file will not be written, use "override" option to ignore')
                    return
            else:
                logger.info(f'old file will be overwritten by a new one (old has {len(df_old)} records vs new {len(self.df_transcriptions_classifications)})')

        # if not exited, just write the file
        self.df_transcriptions_classifications.to_parquet(path)
        
    
    def __retrieve_assistant(self, assistant_name:str) -> openai.types.beta.assistant.Assistant:
        """
        Retrieves the assistant by name if it exists.

        Parameters:
        -----------
        assistant_name : str
            Name of the assistant to retrieve.

        Returns:
        --------
        openai.types.beta.assistant.Assistant
            The retrieved assistant object, or None if not found.
        """
        # find out if assistant is still active and retrieve it
        assistant_id = None
        for a in self.client.beta.assistants.list().dict()['data']:
            if a['name'] == assistant_name:
                assistant_id = a['id']
        if assistant_id != None:
            return self.client.beta.assistants.retrieve(assistant_id)
        else:
            return None


    def get_classifications(self) -> pd.DataFrame:
        return self.df_transcriptions_classifications

    
    @staticmethod
    def json_to_markdown(json_string):
        """
        Converts a JSON string into a flattened markdown file where each element is a heading
        and its value is a paragraph.
    
        Parameters:
        -----------
        json_string : str
            JSON string to be converted to markdown format.
    
        Returns:
        --------
        str
            Flattened markdown string.
        """
        data = json.loads(json_string)
        markdown_list = []
    
        def add_to_markdown(data, level=1):
            for key, value in data.items():
                if isinstance(value, dict):
                    markdown_list.append(f"{'#' * level} {key}")
                    add_to_markdown(value, level + 1)
                elif isinstance(value, list):
                    markdown_list.append(f"{'#' * level} {key}")
                    for item in value:
                        markdown_list.append(f"- {item}")
                else:
                    markdown_list.append(f"{'#' * level} {key}\n\n{value}\n")
    
        add_to_markdown(data)
        return "\n".join(markdown_list)

    @staticmethod
    def get_json_from_parquet(path_parquet_with_json:str, column_name:str, iloc:int) -> dict:
        df = pd.read_parquet(path_parquet_with_json)
        return Transcription_Classifier.get_json_from_df(df, column_name, iloc)
    
    @staticmethod
    def get_json_from_df(df_with_json: pd.DataFrame, column_name:str, iloc:int) -> dict:
        text = df_with_json.iloc[iloc][column_name]
        text_json = json.loads(text)
        return text_json

    @staticmethod
    def flatten_json(json_obj, sep='.') -> dict:
        """
        Flattens a nested json dictionary.
    
        Parameters:
        -----------
        json_obj : dict
            The JSON object to flatten.
        sep : str
            The separator to use for nested keys.
    
        Returns:
        --------
        dict
            A flattened dictionary.
        """
        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + sep)
            elif type(x) is list:
                if len(x) == 0:
                    out[name[:-1]] = None
                else:
                    out[name[:-1]] = ','.join(map(str, x))
            else:
                out[name[:-1]] = x
    
        out = {}
        flatten(json_obj)
        return out

    @staticmethod
    def process_dataframe_json(df, json_column='content', sep='.') -> pd.DataFrame:
        """
        Processes the DataFrame to extract JSON strings into separate columns.
    
        Parameters:
        -----------
        df : pd.DataFrame
            The DataFrame containing the JSON strings.
        json_column : str
            The column name that contains the JSON strings.
        sep : str
            The separator to use for nested keys.
    
        Returns:
        --------
        pd.DataFrame
            A new DataFrame with flattened JSON columns.
        """
        all_flattened = []

        for i, row in df.iterrows():
            json_data = json.loads(row[json_column])
            flattened = Transcription_Classifier.flatten_json(json_data, sep)
            all_flattened.append(flattened)
    
        flattened_df = pd.DataFrame(all_flattened)
    
        # Attempt to convert each column to numeric types if possible
        for col in flattened_df.columns:
            try:
                flattened_df[col] = pd.to_numeric(flattened_df[col])
            except:
                pass    
            
        # Convert any remaining object types to string
        for col in flattened_df.select_dtypes(include=['object']).columns:
            flattened_df[col] = flattened_df[col].astype(str)
    
        result_df = pd.concat([df.drop(columns=[json_column]), flattened_df], axis=1)
        return result_df

            
# EOF