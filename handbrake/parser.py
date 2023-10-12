import json
import os
import platform
import shlex
import shutil
from pathlib import Path
from typing import Any, List, Optional, Union

import jsonschema
import yaml
from box import Box
from loguru import logger

# The location of the schema file
schema_file = 'schema/handbrake.schema.yaml'

# All of the options that can be set as a boolean value but
# should be ignored if set to 'False'.
edge_cases_bool = [
    "inline_parameter_sets",
    "non_anamorphic",
    "auto_anamorphic",
    "loose_anamorphic",
    "custom_anamorphic",
    "subtitle_forced",
    "subtitle_burned",
    "subtitle_default",
    "srt_default",
    "srt_burn",
    "ssa_lang,"
    "ssa_default",
    "ssa_burn",
]


class Parser:

    data: Union[Box, dict]

    def __init__(self, handbrake_path: Optional[Union[str, Path]] = None):
        self.data = Box()
        if handbrake_path:
            self.handbrake_path = Path(handbrake_path)
        else:
            binary = "HandBrakeCLI.exe" if platform.system() == "Windows" else "HandBrakeCLI"
            self.handbrake_path = Path(shutil.which(binary))

    def validate_from_file(self, filepath: Union[Path, str]):
        """Validate the HandBrakeCLI JSON options file against the HandBrake schema file.

        Args:
            filepath (Union[Path, str]): The path to the JSON options for HandBrake

        Raises:
            jsonschema.ValidationError: When the data in the provided file fails to validate against schema.
            jsonschema.SchemaError: When the schema is wrong/malformed.
        """
        filepath = Path(filepath)
        with filepath.open('r') as f:
            content = Box(json.load(f))
        self.validate_from_data(content)

    def validate_from_data(self, data: Union[dict, Box]):
        """Validate the HandBrakeCLI JSON options data against the HandBrake schema file.

        Args:
            data (Union[dict, Box]): The data object containing the options.

        Raises:
            jsonschema.ValidationError: When the data fails to validate against the HandBrake schema.
            jsonschema.SchemaError: When the schema is wrong/malformed.
        """
        schema_path = Path(os.path.dirname(os.path.abspath(__file__)))
        schema_path = schema_path / schema_file
        with schema_path.open('r') as f:
            schema = yaml.safe_load(f)

        jsonschema.validate(data, schema)
        self.data = Box(data)

    def generate_command(self, as_string: bool = False) -> Union[List, str]:
        """Generate all of the command-line options from the provided data.

        Args:
            as_string (bool, optional): Return the options as a string. Defaults to False.

        Returns:
            Union[List, str]: The HandBrake CLI command-line options as a list.
        """
        command = [str(self.handbrake_path.absolute())]
        if not self.data:
            return "" if as_string else command
        command.extend(['--input', self.data.source])
        command.extend(['--output', self.data.output_file])
        for k, v in self.data.items():
            if k in ['source', 'output_file']:
                continue
            logger.info(f"Processing '{k}'")
            f = getattr(self, f"process_{k}")
            command.extend(f())
        if as_string:
            return shlex.join(command)
        return command

    def __convert_cli_option(self, option: str) -> str:
        """Convert the module's attribute format to the format that HandBrake expects for command-line options.

        Args:
            option (str): The module's version of the command-line option.

        Returns:
            str: Handbrake-specific command-line setting.
        """
        edge_cases = {
            "max_height": "--maxHeight",
            "max_width": "--maxWidth"
        }
        if option in edge_cases.keys():
            return edge_cases[option]
        option = '--' + option.replace('_', '-')
        return option

    def __process_simple_option(self, k: str, v: Any) -> List[str]:
        """Take a simple option (key/value pair) and return the appropriate HandBrakeCLI representation.

        Args:
            k (str): The CLI option.
            v (Any): The object to process (usually str, int, float, or bool)

        Returns:
            List[str]: The list of command options.
        """
        command = list()
        if isinstance(v, bool) and v:
            command.append(self.__convert_cli_option(k))
        elif isinstance(v, bool):
            if k not in edge_cases_bool:
                k = "no_" + k
                command.append(self.__convert_cli_option(k))
        else:
            command.append(self.__convert_cli_option(k))
            command.append(str(v))
        return command

    def process_source_options(self) -> List[str]:
        """Process the 'source_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.source_options.items():
            match k:
                case "start_at" | "stop_at":
                    command.append(self.__convert_cli_option(k))
                    i, j = [(a, b) for a, b in v.items()][0]
                    command.append(f"{i}:{j}")
                case _:
                    command.extend(self.__process_simple_option(k, v))
        return command

    def process_destination_options(self):
        """Process the 'destination_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.destination_options.items():
            command.extend(self.__process_simple_option(k, v))
        return command

    def process_video_options(self):
        """Process the 'video_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.video_options.items():
            match k:
                case "encopts":
                    command.append(self.__convert_cli_option(k))
                    command.append(self.__generate_custom_format(v))
                case _:
                    command.extend(self.__process_simple_option(k, v))
        return command

    def process_audio_options(self):
        """Process the 'audio_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.audio_options.items():
            if isinstance(v, list):
                command.append(self.__convert_cli_option(k))
                command.append(self.__generate_list_format(v))
            else:
                command.extend(self.__process_simple_option(k, v))
        return command

    def process_picture_options(self):
        """Process the 'picture_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.picture_options.items():
            if k == "crop":
                command.append(self.__convert_cli_option(k))
                command.append(self.__generate_crop_format(v))
            else:
                command.extend(self.__process_simple_option(k, v))
        return command

    def process_filters_options(self):
        """Process the 'filters_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.filters_options.items():
            if isinstance(v, dict):
                for i, j in v.items():
                    if isinstance(j, dict):
                        command.append(self.__convert_cli_option(k))
                        command.append(self.__generate_custom_format(j))
                    else:
                        command.extend(self.__process_simple_option(k, j))
            else:
                command.extend(self.__process_simple_option(k, v))
        return command

    def process_subtitles_options(self):
        """Process the 'subtitles_options' section of the data.

        Returns:
            List[str]: A list of command-line options associated with the data.
        """
        command = list()
        for k, v in self.data.subtitles_options.items():
            if isinstance(v, list):
                command.append(self.__convert_cli_option(k))
                command.append(self.__generate_list_format(v))
            else:
                command.extend(self.__process_simple_option(k, v))
        return command

    def __generate_list_format(self, values: list) -> str:
        """Generate the 'list' format from a given list of values.

        Args:
            values (list): The list of values to parse and glue together with commas.

        Returns:
            str: The comma-delimited string made up of the values provided.
        """
        custom_format = list()
        for i in values:
            if isinstance(i, bool):
                custom_format.append(1 if i else 0)
            else:
                custom_format.append(i)
        return ','.join([str(i) for i in custom_format])

    def __generate_custom_format(self, options: Union[Box, dict]) -> str:
        """Generate the 'custom' format from a given set of keys and their associated values.  This is used for all of HandBrake's custom filter settings for the most part.

        Args:
            options (Union[Box, dict]): The key/value data to smoosh together.

        Returns:
            str: A string of key/value pairs joined with `=` signs, then combined with `:`s.
        """
        custom_format = list()
        for k, v in options.items():
            k = k.replace('_', '-')
            custom_format.append(f"{k}={v}")
        return ':'.join(custom_format)

    def __generate_crop_format(self, options: Union[Box, dict]) -> str:
        """Generatet the 'crop' setting format from the associated dictionary.

        Args:
            options (Union[Box, dict]): The crop settings from the data.

        Returns:
            str: The string representation of the crop settings.
        """
        custom_format = list()
        order = ["top", "bottom", "left", "right"]
        for o in order:
            try:
                custom_format.append(options[o])
            except:
                custom_format.append(0)
        return ':'.join([str(i) for i in custom_format])
