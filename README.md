# DVTAG

A command-line tool designed to tag your doujin voice library.

## How DVTAG Works

DVTAG operates by recursively searching the directory specified by the user. This directory can be a relative path, or even the current directory. It looks for all directories that have a work number in their names.

A work number is a unique identifier from the product link on dlsite, in the format of `RJxxxxxx`, `BJxxxxxx`, or `VJxxxxxx`, where `xxxxxx` can be either 6 or 8 digits.

For every supported audio file format found inside each of these directories, DVTAG uses the corresponding work number to fetch metadata from the web. It then tags the audio files with this metadata.

## Installation

DVTAG requires Python 3.9 or higher. You can install it using pip or pipx:

```bash
pip install dvtag
```

or 

```bash
pipx install dvtag
```

To upgrade DVTAG, use:

```bash
pip install --upgrade dvtag
```

or

```bash
pipx upgrade dvtag
```

## Usage

```
$ dvtag -h
usage: dvtag [-h] [-v] [-w2f] [-w2m] dirpath

Doujin Voice Tagging Tool (tagging in place)

positional arguments:
  dirpath        a required directory path

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -w2f           transcode all wav files to flac [LOSELESS]
  -w2m           transcode all wav files to mp3

```

Please ensure that every doujin voice folder name contains a specific work number format - like `RJ123123`, `rj123123 xxx`, `xxxx RJ01123123`, `BJ01123123`, `VJ123123`, etc.

To tag your library, use the `dvtag` command:

```bash
dvtag /path/to/your/library
```

## Transcoding

Transcoding is an additional functionality of DVTAG. If you have `wav` audio files and you want to convert these all to `flac` or `mp3`, run with option `-w2f` or `-w2m`. For example:

```bash
dvtag -w2f /path/to/your/library
```

Please note that transcoding depends on ffmpeg and users seeking additional related features should use the ffmpeg tool directly.