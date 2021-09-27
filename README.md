# DVTAG

A tool for tagging your doujin voice library.

## Installation

```bash
pip install dvtag
```

## Usage

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
├── plug in.東京
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
