from handbrake.parser import Parser
import jsonschema
from loguru import logger

handbrake_data = {
    "source": "test.mkv",
    "output_file": "output.mkv",
    "subtitles_options": {
        "subtitle_lang_list": [
            "jpn",
            "eng"
        ],
        "subtitle_forced": False,
        "native_language": "eng",
        "subtitle": [1, 2, 3, 4, 5]
    },
    "video_options": {
        "encoder": "x265_10bit",
        "encopts": {
            "profile": "slow",
            "b-frames": "100"
        }
    }
}

parser = Parser()
try:
    parser.validate_from_data(handbrake_data)
except jsonschema.ValidationError as e:
    logger.warning(f"ValidationError: {e.message}")
    logger.warning(f"Path to Error: {e.json_path}")
except jsonschema.SchemaError as e:
    logger.warning(f"SchemaError: {e.message}")
    logger.warning(f"Path to Error: {e.json_path}")

command = parser.generate_command()
print(command)
print(' '.join(command))