import jsonschema
from loguru import logger

from handbrake.parser import Parser

handbrake_data = {
    "source": "test.mkv",
    "output_file": "output.mkv",
    "video_options": {
        "encoder": "x265_10bit",
        "encoder_preset": "slow",
        "quality": 19
    },
    "audio_options": {
        "audio": [1, 3],
        "aencoder": ["opus", "opus"],
        "ab": [128, 192],
        "mixdown": ["stereo", "5_2_lfe"]
    },
    "subtitles_options": {
        "subtitle": [1, 2],
        "subname": [
            "Signs and Songs",
            "Full Subtitles"
        ]
    }
}

parser = Parser()
try:
    parser.load_from_object(handbrake_data)
except jsonschema.ValidationError as e:
    logger.warning(f"ValidationError: {e.message}")
    logger.warning(f"Path to Error: {e.json_path}")
except jsonschema.SchemaError as e:
    logger.warning(f"SchemaError: {e.message}")
    logger.warning(f"Path to Error: {e.json_path}")

command: str = parser.generate_command(as_string=True)
logger.debug(f"Command to run: {command}")

parser.run()