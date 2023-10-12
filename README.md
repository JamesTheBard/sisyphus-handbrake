# Introduction

- Schema based off of HandBrake CLI version **1.6.1**.

The `sisyphus-handbrake` module is a Python module that wraps the Handbrake CLI binary and allows you to worry more about the options being passed and less about trying to figure out exactly _how_ they should be passed.

As with the other `sisyphus` modules, you can pass a JSON file to the parser and it will validate the JSON against the included schema file.

## Implementation

All of the option information is documented in the schema file.  Included is the JSON schema file in JSON and YAML formats.

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
