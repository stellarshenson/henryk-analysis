"""
Transcription classification using OpenAI's GPT models.
"""

import json
import pathlib
import time

from json_repair import repair_json
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain
from names_generator import generate_name
import openai
import pandas as pd

from henryk_analysis import utils
from henryk_analysis.config import (
    FILE_PROMPT_RECORDING_CLASSIFICATION,
    FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET,
)
from henryk_analysis.logger import coloured_text, logger, progressBar


class TranscriptionClassifier:
    """
    A class to handle transcription classification using OpenAI's GPT models.

    Attributes
    ----------
    client : openai.OpenAI
        OpenAI API client.
    df_transcriptions_classifications : pd.DataFrame
        DataFrame to store transcription classification results.
    assistant : openai.types.beta.assistant.Assistant
        OpenAI assistant instance.
    model : str
        OpenAI model to use.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        assistant_name: str = "Professor Hendrickson",
        df_transcriptions_classifications: pd.DataFrame = None,
    ):
        """
        Initialize the TranscriptionClassifier.

        Parameters
        ----------
        api_key : str
            API key for OpenAI.
        model : str
            OpenAI model to use (default: 'gpt-4o').
        assistant_name : str
            Name of the assistant (default: 'Professor Hendrickson').
        df_transcriptions_classifications : pd.DataFrame, optional
            DataFrame to store transcription classification results.
        """
        self.unmarkdown_parser = MarkdownIt(renderer_cls=RendererPlain)
        self.client = openai.OpenAI(api_key=api_key)

        if df_transcriptions_classifications is not None:
            self.df_transcriptions_classifications = df_transcriptions_classifications.reset_index(
                drop=True
            ).copy()
        else:
            self.df_transcriptions_classifications = pd.DataFrame(
                {"name": [], "classification_json": []}
            )

        self.temp_dataset_file_prefix = "/tmp/temp_"

        self.assistant = None
        self.assistant_name = assistant_name
        self.model = model

        self.prompt_recording_classification = None

        self.messages = None
        self.run = None
        self.thread = None
        self.response_md = None
        self.response_json = None
        self._in_progress = False
        self._inference_settings = {}
        self.stats = None
        self.temp_df_transcriptions_classifications_parquet = None

    def initialise_prompt(
        self, prompt_file_path: str | pathlib.Path = FILE_PROMPT_RECORDING_CLASSIFICATION
    ):
        """Load the classification prompt and initialize the assistant."""
        prompt_file_path = pathlib.Path(prompt_file_path)
        with open(prompt_file_path, "r") as f:
            self.prompt_recording_classification = f.read()

        self.assistant = self._retrieve_assistant(assistant_name=self.assistant_name)

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
        cooldown_frequency: int = 4,
        cooldown_seconds: int = 5,
        retry: int = 3,
        verbose: bool = False,
    ):
        """
        Perform classification on the provided transcriptions DataFrame.

        Parameters
        ----------
        df_transcriptions : pd.DataFrame
            DataFrame containing the transcriptions to classify.
        df_transcriptions_classifications : pd.DataFrame, optional
            DataFrame containing existing classification results.
        cooldown_frequency : int
            Frequency of cooldown periods (default: 4).
        cooldown_seconds : int
            Duration of each cooldown in seconds (default: 5).
        retry : int
            Number of retries for inference on failure (default: 3).
        verbose : bool
            Enable verbose logging (default: False).
        """
        self.temp_df_transcriptions_classifications_parquet = (
            f"{self.temp_dataset_file_prefix}{generate_name()}.parquet"
        )

        logger.info(
            f"intermediate classification results will be written to "
            f"{self.temp_df_transcriptions_classifications_parquet}"
        )

        if df_transcriptions_classifications is not None and self._in_progress is False:
            self.df_transcriptions_classifications = df_transcriptions_classifications.reset_index(
                drop=True
            ).copy()

            stats = self._get_completed_vs_requested_stats(
                df_transcriptions, self.df_transcriptions_classifications
            )
            logger.info(
                f"found {stats['num_completed']} ({stats['num_requested_completed']} "
                f"from current request) existing classifications, those will not be processed."
            )
        elif df_transcriptions_classifications is not None and self._in_progress is True:
            logger.warning(
                "unable to provide initial classification dataset, classification is in progress"
            )

        self._in_progress = True
        self.thread = self.client.beta.threads.create()

        cooldown_counter = 0
        for i, (index, row) in enumerate(df_transcriptions.iterrows()):
            transcription = row["transcription"]
            name = row["name"]
            name_truncated = utils.get_truncated_string(name, 64)

            stats = self._get_completed_vs_requested_stats(
                df_transcriptions, self.df_transcriptions_classifications
            )
            progress_bar_prefix = (
                f"classifying {stats['num_requested_completed']:3}/{stats['num_requested']} "
                f"transcriptions"
            )

            if (
                self.df_transcriptions_classifications[
                    self.df_transcriptions_classifications["name"] == name
                ].empty
                is False
            ):
                if verbose:
                    logger.info(f"ignoring transcription [{index}] {name_truncated}")
                continue

            # COOLDOWN
            cooldown_counter += 1
            if cooldown_frequency > 0 and cooldown_counter % cooldown_frequency == 0:
                if verbose:
                    logger.info(f"COOLDOWN, iteration [{i}]")
                else:
                    progressBar(
                        i,
                        len(df_transcriptions),
                        prefix=progress_bar_prefix,
                        suffix=f"{'*** COOLDOWN ***':72}",
                        length=40,
                    )
                time.sleep(cooldown_seconds)
                self.client.beta.threads.delete(self.thread.id)
                self.thread = self.client.beta.threads.create()

            if verbose:
                logger.info(f"processing transcription [{index}] {name_truncated}")
            else:
                progressBar(
                    i,
                    len(df_transcriptions),
                    prefix=progress_bar_prefix,
                    suffix=f"[{index:3}] {name_truncated:64}",
                    length=40,
                )

            # INFERENCE
            for retry_count in range(retry):
                messages_dict = self._inference(
                    transcription=transcription,
                    thread=self.thread,
                    assistant=self.assistant,
                )

                if messages_dict is not None:
                    self._save_classification_response(messages_dict=messages_dict, name=name)
                    break
                elif retry_count < retry:
                    if verbose:
                        logger.info(f"retry no {retry_count} [{index}] {name_truncated}")
                    else:
                        progressBar(
                            i,
                            len(df_transcriptions),
                            prefix=progress_bar_prefix,
                            suffix=f"{'*** RETRY ['}{retry_count}{'] ***':54}",
                            length=40,
                        )
                    time.sleep(cooldown_seconds)
                    self.client.beta.threads.delete(self.thread.id)
                    self.thread = self.client.beta.threads.create()
                else:
                    raise RuntimeError(f"unable to complete, run status: {self.run.status}")

        progressBar(
            1,
            1,
            prefix=f"classifying {len(df_transcriptions)} transcriptions",
            suffix=f"{'done.':72}",
            length=40,
        )

        stats = self._get_completed_vs_requested_stats(
            df_transcriptions, self.df_transcriptions_classifications
        )

        if stats["num_requested_completed"] == stats["num_requested"]:
            if stats["num_completed"] > stats["num_requested"]:
                logger.info(
                    f"more ({stats['num_completed']}) classifications than requested, "
                    f"classifier was executed before on different dataset"
                )
            logger.info(
                coloured_text(
                    f"*** all {stats['num_requested']} requested transcriptions "
                    f"classifications were completed ***",
                    "green",
                )
            )
        else:
            logger.info(
                f"there are still {stats['num_remaining']} missing requested classifications"
            )

    def _get_completed_vs_requested_stats(
        self, df_requested: pd.DataFrame, df_completed: pd.DataFrame
    ) -> dict:
        """Calculate statistics for completed vs requested classifications."""
        requested_names = set(df_requested["name"].to_list())
        completed_names = set(df_completed["name"].to_list())
        requested_completed_names = requested_names & completed_names
        remaining_names = requested_completed_names ^ requested_names

        self.stats = {
            "requested_names": requested_names,
            "completed_names": completed_names,
            "requested_completed_names": requested_completed_names,
            "remaining_names": remaining_names,
            "num_requested": len(requested_names),
            "num_completed": len(completed_names),
            "num_requested_completed": len(requested_completed_names),
            "num_remaining": len(remaining_names),
        }
        return self.stats

    def get_stats(self) -> dict:
        """Return current classification statistics."""
        return self.stats

    def reset_assistant(self):
        """Reset the assistant by deleting the current instance."""
        if self.assistant is not None:
            self.client.beta.assistants.delete(self.assistant.id)

    def _inference(self, transcription: str, thread, assistant) -> dict | None:
        """Perform inference on the provided transcription."""
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Please process the following transcription:\n{transcription}",
        )

        self.run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        if self.run.status == "completed":
            self.messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            return self.messages.to_dict()
        return None

    def _save_classification_response(self, messages_dict: dict, name: str):
        """Save the classification response to the DataFrame."""
        self.response_md = messages_dict["data"][0]["content"][0]["text"]["value"]

        response_text = self.unmarkdown_parser.render(self.response_md)
        repaired_response_text = repair_json(response_text)
        self.response_json = json.loads(repaired_response_text)

        row = pd.DataFrame(
            {"name": [name], "classification_json": [json.dumps(self.response_json)]}
        )
        logger.debug(
            f"adding new record to the dataset, it has currently "
            f"{len(self.df_transcriptions_classifications)} entries"
        )
        self.df_transcriptions_classifications = pd.concat(
            [self.df_transcriptions_classifications, row], ignore_index=True
        )

        logger.debug(
            f"writing intermediate result to {self.temp_df_transcriptions_classifications_parquet}, "
            f"it has now {len(self.df_transcriptions_classifications)} entries"
        )
        self.df_transcriptions_classifications.to_parquet(
            self.temp_df_transcriptions_classifications_parquet
        )

    def save_classification_parquet(
        self,
        path: str | pathlib.Path = FILE_TRANSCRIPTIONS_CLASSIFICATIONS_PARQUET,
        override: bool = False,
    ):
        """Save the classification results to a parquet file."""
        path = pathlib.Path(path)
        logger.info(
            f"saving {len(self.df_transcriptions_classifications)} classification results to {path}"
        )

        if path.is_file():
            df_old = pd.read_parquet(path)
            logger.info(
                "found older file with the same name, checking the older file size vs new..."
            )

            if len(df_old) > len(self.df_transcriptions_classifications):
                logger.warning(
                    f"older file has more records ({len(df_old)}) than new "
                    f"({len(self.df_transcriptions_classifications)})"
                )

                if override:
                    logger.info("[override] replacing older file with new one")
                    self.df_transcriptions_classifications.to_parquet(path)
                    return
                else:
                    logger.error('new file will not be written, use "override" option to ignore')
                    return
            else:
                logger.info(
                    f"old file will be overwritten by a new one (old has {len(df_old)} records "
                    f"vs new {len(self.df_transcriptions_classifications)})"
                )

        self.df_transcriptions_classifications.to_parquet(path)

    def _retrieve_assistant(self, assistant_name: str):
        """Retrieve the assistant by name if it exists."""
        assistant_id = None
        for a in self.client.beta.assistants.list().dict()["data"]:
            if a["name"] == assistant_name:
                assistant_id = a["id"]
        if assistant_id is not None:
            return self.client.beta.assistants.retrieve(assistant_id)
        return None

    def get_classifications(self) -> pd.DataFrame:
        """Return the classifications DataFrame."""
        return self.df_transcriptions_classifications

    @staticmethod
    def json_to_markdown(json_string: str) -> str:
        """Convert a JSON string into flattened markdown."""
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
    def get_json_from_parquet(
        path_parquet_with_json: str | pathlib.Path, column_name: str, iloc: int
    ) -> dict:
        """Extract JSON from a parquet file at specified index."""
        df = pd.read_parquet(path_parquet_with_json)
        return TranscriptionClassifier.get_json_from_df(df, column_name, iloc)

    @staticmethod
    def get_json_from_df(df_with_json: pd.DataFrame, column_name: str, iloc: int) -> dict:
        """Extract JSON from a DataFrame at specified index."""
        text = df_with_json.iloc[iloc][column_name]
        return json.loads(text)

    @staticmethod
    def flatten_json(json_obj: dict, sep: str = ".") -> dict:
        """Flatten a nested JSON dictionary."""
        out = {}

        def flatten(x, name=""):
            if isinstance(x, dict):
                for a in x:
                    flatten(x[a], name + a + sep)
            elif isinstance(x, list):
                if len(x) == 0:
                    out[name[:-1]] = None
                else:
                    out[name[:-1]] = ",".join(map(str, x))
            else:
                out[name[:-1]] = x

        flatten(json_obj)
        return out

    @staticmethod
    def process_dataframe_json(
        df: pd.DataFrame, json_column: str = "content", sep: str = "."
    ) -> pd.DataFrame:
        """Process DataFrame to extract JSON strings into separate columns."""
        all_flattened = []

        for _, row in df.iterrows():
            json_data = json.loads(row[json_column])
            flattened = TranscriptionClassifier.flatten_json(json_data, sep)
            all_flattened.append(flattened)

        flattened_df = pd.DataFrame(all_flattened)

        for col in flattened_df.columns:
            try:
                flattened_df[col] = pd.to_numeric(flattened_df[col])
            except (ValueError, TypeError):
                pass

        for col in flattened_df.select_dtypes(include=["object"]).columns:
            flattened_df[col] = flattened_df[col].astype(str)

        result_df = pd.concat([df.drop(columns=[json_column]), flattened_df], axis=1)
        return result_df


# Alias for backwards compatibility
Transcription_Classifier = TranscriptionClassifier

# EOF
