# Log File Analyzer (OOP, Python)

A Python program that parses `.log` files and generates useful summaries and visualizations. Built with an object‑oriented design.

## Features

- Parses multiple common log formats (ISO timestamps & syslog-like).
- Supports levels: **INFO**, **WARNING**, **ERROR** (and **DEBUG**, **UNKNOWN**).
- Counts per level and **JSON** export.
- Search / filter by **keyword** and **date range**.
- Summary report: total entries, first/last timestamp, top error messages.
- Visualizations with **matplotlib** (bar chart & timeline).
- **CLI** for automation and a **Tkinter GUI** for interactive analysis.
- Handles malformed lines gracefully.
- Suitable for large logs (streaming parse).

## Project Structure

```
log_analyzer/
  __init__.py
  models.py
  parser.py
  analyzer.py
  filters.py
  exporter.py
  visualizer.py
  cli.py
  gui.py
sample_logs/
  sample.log
screenshots/
requirements.txt
README.md
```

## Quick Start

1. **Create a virtual environment** (recommended) and install deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the CLI** on the provided sample:
   ```bash
   python -m log_analyzer.cli sample_logs/sample.log --json-out summary.json --plot-out counts.png --timeline-out timeline.png --timeline-bucket hour
   ```

3. **Open the GUI**:
   ```bash
   python -m log_analyzer.gui
   ```

## CLI Options

```
usage: cli.py [-h] [--keyword KEYWORD] [--level LEVEL] [--start START] [--end END]
              [--json-out JSON_OUT] [--plot-out PLOT_OUT] [--timeline-out TIMELINE_OUT]
              [--timeline-bucket TIMELINE_BUCKET]
              input [input ...]
```

- `input` — One or more log files or directories (recursive `*.log`).
- `--keyword` — Filter entries containing a substring.
- `--level` — INFO|WARNING|ERROR|DEBUG|UNKNOWN
- `--start/--end` — Date filters (e.g., `2025-08-27` or full ISO).
- `--json-out` — Save the summary as JSON.
- `--plot-out` — Save **bar chart** (PNG) for counts by level.
- `--timeline-out` — Save **timeline** (PNG) of total log frequency.
- `--timeline-bucket` — `minute` | `hour` | `day`.

## Screenshots

Example outputs generated from `sample_logs/sample.log`:

- Bar chart: `screenshots/counts.png`
- Timeline: `screenshots/timeline.png`

## Notes on Formats & Robustness

- Timestamps accepted: `YYYY-MM-DD HH:MM:SS[.ms|,ms]`, ISO `YYYY-MM-DDTHH:MM:SS[Z]`.
- Syslog-like (`Aug 27 10:00:01`) are supported (year inferred).
- Lines without recognizable level/timestamp are kept as `UNKNOWN` and counted as malformed.
- Parser is streaming, GUI loads file in a worker thread.

## Testing with Large Logs

You can concatenate the sample line many times to simulate a large log and ensure performance:
```bash
yes "2025-08-28 09:00:00,000 INFO System - Heartbeat" | head -n 200000 > big.log
python -m log_analyzer.cli big.log --plot-out big_counts.png
```

## License

MIT
