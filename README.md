# Introduction

- Schema based off of HandBrake CLI version **1.6.1**.

The `sisyphus-handbrake` module is a Python module that wraps the Handbrake CLI binary and allows you to worry more about the options being passed and less about trying to figure out exactly _how_ they should be passed.

As with the other `sisyphus` modules, you can pass a JSON file to the parser and it will validate the JSON against the included schema file.

## Installation

### Prerequisites

- `HandBrakeCLI` installed.
- `ffmpeg` installed if you want to use the progress bar.
- `python` version 3.11 or greater installed
- `poetry` installed

### Procedure

1. Clone the repository.

    ```bash
    git clone https://github.com/JamesTheBard/sisyphus-handbrake
    ```

2. Install the dependencies.

    ```bash
    poetry install
    ```

3. Enjoy!

## Quick Python Example

To whip up a quick "take-in-a-JSON-file-and-encode" program:

```python
from handbrake.parser import Parser

parser = Parser()
parser.load_from_file("handbrake.json")
parser.run()
```

The `handbrake.json` file is just the JSON file that has all of the options you want to use in HandBrake.  A good example of what that JSON file should look like is shown in the following sections.

## Implementation

All of the option information is documented in the schema file.  Included is the JSON schema file in JSON and YAML formats.

## The `Parser` Class

There are really only four methods in this class, and one option you can pass when creating an instance of it.  The methods are explained in the next sections.

```python
from handbrake.parser import Parser

# This will create a Parser instance, and track down the path
# of the HandBrakeCLI binary.
parser = Parser()

# This will override the HandBrakeCLI binary path.  Very good if
# the binary is not on the system path or you have changed the
# name of the binary for some odd reason as a challenge.
parser = Parser(handbrake_path="/path/to/HandBrakeCLI")
```

### `Parser.load_from_file` Method

#### Example

```python
from handbrake.parser import Parser

parser = Parser()
parser.load_from_file("path_to_json_file.json")
```

#### Description

This will take the JSON file, validate it against the schema, and load it into the `data` attribute on the `parser` object.  That data is what will be used to generate commands.

#### Raises

- `jsonschema.ValidationError`: When your data is either malformed or doesn't conform to the provided JSON schema.
- `jsonschema.SchemaError`: When the author of this module made a serious mistake in the schema file and its borked.

### `Parser.load_from_object` Method

#### Example

```python
from handbrake.parser import Parser

handbrake_data = {
    "source": "test_file.mkv",
    "output_file": "output.mkv"
}

parser = Parser()
parser.load_from_object(handbrake_data)
```

#### Description

This will load a Python dictionary, validate it against the schema, and basically do everything in the `Parser.load_from_file` description.  This makes sense as loading from file just turns it into a Python `dict` which then gets passed to this method.

#### Raises

- `jsonschema.ValidationError`: When your data is either malformed or doesn't conform to the provided JSON schema.
- `jsonschema.SchemaError`: When the author of this module made a serious mistake in the schema file and its borked.

### `Parser.generate_command` Method

#### Example

```python
from handbrake.parser import Parser

handbrake_data = {
    "source": "test_file.mkv",
    "output_file": "output.mkv"
}

parser = Parser()
parser.load_from_object(handbrake_data)

# Return the command as something perfectly suited to toss
# to the `subprocess` module.
command: list = parser.generate_command()

# Or have it return the command as something you can copy-pasta
# into a terminal window.
command: str = parser.generate_command(as_string=True)
```

#### Description

This parses the data after either `load_from_file` or `load_from_object` is called.  This will only generate a proper command if:

- Either `load_from_file` or `load_from_object` are called successfully, and
- The data contained in the JSON file/Python `dict` are validated against the schema.

### `Parser.run` Method

#### Example

```python
from handbrake.parser import Parser

handbrake_data = {
    "source": "test_file.mkv",
    "output_file": "output.mkv"
}

parser = Parser()
parser.load_from_object(handbrake_data)

# This will run with a very pretty progress bar (ffmpeg required)
# Same as return_code = parser.run(progress_bar=True)
return_code = parser.run() 

# This will run completely without progress and show nothing
return_code = parser.run(progress_bar=False, verbose=False)

# This will show the HandBrakeCLI output as it runs
return_code = parser.run(progress_bar=False, verbose=True)
```

#### Description

This runs the encode with the setting that have been loaded and validated.  Once this starts, grab a tasty beverage, sit back, and watch the progress bar fill up.

## JSON Format Breakdown

### Input

```json
{
    "source": "cool_video.mkv",
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
```

### Output

```
'/path/to/HandBrakeCLI.exe' --input cool_video.mkv --output output.mkv --encoder x265_10bit --encoder-preset slow --quality 19 --audio 1,3 --aencoder opus,opus --ab 128,192 --mixdown stereo,5_2_lfe --subtitle 1,2 --subname 'Signs and Songs,Full Subtitles'
```

## Command Line Options

For all of the options listed in the documentation/`-h` option, there are a few "gotchas".
- All of the options use underscores instead of dashes.  For example, the `--ssa-offset` command-line option is `ssa_offset` in the schema file.  The only two that significantly changed were the `--maxHeight` and `--maxWidth` options which were camel-cased for some odd reason.  They were renamed to `max_height` and `max_width`.

- All command-line options are grouped via the section they appear in documentation.  The groups are:
    - `source_options`
    - `destination_options`
    - `video_options`
    - `audio_options`
    - `picture_options`
    - `filters_options`
    - `subtitles_options`

- The source file and the destination files use the standard naming conventions of `source` and `output_file` for `sisyphus` modules.  These have been removed from `source_options` and `destination_options` respectively.

- Any option that specified listing tracks separated by commas have turned into arrays of values.  For example, the `--audio` option specifies that you select the audio tracks you want to process separated by commas (e.g. `--audio 1,2,3`).  For `sisyphus-json`, this turns into the following object:

    ```python
    {
        "audio": [1, 2, 3]
    }
    ```

- Any option that specifies `attr1=val1:attr2=val2` such as custom filters has been converted into an object which should make things a bit easier to validate.  For example, the `--bwdif` filter setting can use custom settings, so `--bwdif mode=3:parity=1` would look like the following object.

    ```python
    {
        "bwdif": {
            "mode": 3,
            "parity": 1
        }
    }
    ```

- Options in the documentation that have a preset, a custom setting, or can be set without any value are also represented in JSON.  The aforementioned `--bwdif` option has three forms:

    - The setting without options (e.g. `--bwdif` by itself).  This would be represented by setting `bwdif` to the value `true` in JSON.
    - The setting with a preset (e.g. `--bwdif bob`).  This would be represented by setting `bwdif` to the preset name in JSON.
    - The setting with custom settings (e.g. `--bwdif mode=3:parity=1`). This is represented as demonstrated above.

- Command-line options that have a corresponding `--no-` prefix can simply be set via the regular version of the command-line option.  For example, the `--keep-display-aspect` has an opposite command-line option called `--no-kee-display-aspect`.  In the JSON, you can just set `keep_display_aspect` to `false` for the same result.  This also applies to options like `bwdif`.

    ```python
    {
        "keep_display_aspect": False
    }
    ```

- The `--pixel-aspect` setting does still use the `<par_x:par_y>` formatting (e.g. `3:2`) as it made more sense to keep it that way.

    ```python
    {
        "pixel_aspect": "3:2"
    }
    ```

- The `--crop` setting also breaks out into an object with four attributes: `up`, `down`, `left`, and `right`.  The order you specify them in does not matter.
