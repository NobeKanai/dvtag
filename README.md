# DVTAG

A tool for tagging your doujin voice library.

## Installation

*Require Python>=3.9*

```bash
pip install dvtag
```

## Usage

```
$ dvtag -h
usage: dvtag [-h] [-w2f] [-w2m] dirpath

Doujin Voice Tagging Tool (tagging in place)

positional arguments:
  dirpath     a required directory path

options:
  -h, --help  show this help message and exit
  -w2f        transcode all wav files to flac [LOSELESS] (default: False)
  -w2m        transcode all wav files to mp3 (default: False)
```

You must ensure that every doujin voice folder name contains a specific id format(in dlsite) - like `RJ123123`, `rj123123 xxx`, `xxxx RJ123123`

```
├── EXcute
│   ├── RJ321580
│   └── RJ328009
│
├── Kaleidoscope
│   └── RJ329141
│
├── PINK PUNK PRO
│   └── RJ321217
│
├── plug in.XX
│   ├── [RJ310972][XXXxx][plug in.XX]
│   └── RJ341111
│
├── ReApple
│   ├── [RJ263247]
│   └── RJ301616
```

Then tagging with command `dvtag`:

```bash
dvtag /path/to/your/library
```

If you have `wav` audio files and you want to convert these all to `flac`/`mp3`, run with option `-w2f`/`-w2m`. For example

```bash
dvtag -w2f /path/to/your/library
```