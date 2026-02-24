# Timesplit

A lightweight, minimalist speedrun timer with a transparent overlay.

## Features
- **Transparent UI**: Native transparency without chroma keying.
- **Always on Top**: Keeps the timer visible over your game.
- **Global Hotkeys**: Control the timer while in-game.
- **Sum of Best**: Automatically calculates your best possible time.
- **Local Storage**: Simple JSON files for your splits.

## Requirements
- Python 3.10+
- PyQt6
- keyboard (Requires Administrator/Root privileges for global hotkeys)

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Running
On Windows, run in an **Administrator** terminal for global hotkeys:
```bash
python main.py
```

## Hotkeys (Default)
- **NumPad 1**: Start / Split
- **NumPad 3**: Reset (Autosaves progress)
- **NumPad 8**: Undo Split
- **NumPad 2**: Skip Split
- **NumPad 5**: Pause / Resume

## Customization
Edit `data/example_run.json` to define your own segments and personal bests.
The app automatically saves your progress when you reset the timer or close the window.
