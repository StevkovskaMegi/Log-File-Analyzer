import argparse
from pathlib import Path
from datetime import datetime
from .parser import LogParser
from .analyzer import LogAnalyzer
from .filters import FilterCriteria
from .exporter import JSONExporter
from .visualizer import Visualizer

def parse_args():
    p = argparse.ArgumentParser(description="Log File Analyzer (OOP)")
    p.add_argument("input", nargs='+', help="Log files or directories to analyze")
    p.add_argument("--keyword", help="Filter: keyword substring", default=None)
    p.add_argument("--level", help="Filter: level (INFO|WARNING|ERROR|DEBUG|UNKNOWN)", default=None)
    p.add_argument("--start", help="Filter: start date ISO (YYYY-MM-DD or full ISO)", default=None)
    p.add_argument("--end", help="Filter: end date ISO (YYYY-MM-DD or full ISO)", default=None)
    p.add_argument("--json-out", help="Path to save JSON summary", default=None)
    p.add_argument("--plot-out", help="Path to save bar chart (PNG)", default=None)
    p.add_argument("--timeline-out", help="Path to save timeline (PNG)", default=None)
    p.add_argument("--timeline-bucket", help="Timeline bucket: minute|hour|day", default="hour")
    return p.parse_args()

def iter_paths(inputs):
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            for file in p.rglob("*.log"):
                yield file
        elif p.is_file():
            yield p
        else:
            print(f"[warn] Not found: {p}")

def main():
    args = parse_args()
    crit = FilterCriteria(
        keyword=args.keyword,
        level=args.level,
        start=_parse_date(args.start) if args.start else None,
        end=_parse_date(args.end) if args.end else None,
    )
    parser = LogParser()
    analyzer = LogAnalyzer()

    for path in iter_paths(args.input):
        for entry in parser.parse_file(str(path)):
            analyzer.ingest([entry])

    entries = analyzer.entries
    if any([crit.keyword, crit.level, crit.start, crit.end]):
        entries = analyzer.filter(crit)

    summary = analyzer.summary(entries)
    print("Summary:\n", summary)

    if args.json_out:
        JSONExporter.save(summary, args.json_out)
        print(f"Saved JSON -> {args.json_out}")

    if args.plot_out:
        counts = analyzer.counts_by_level(entries)
        Visualizer.bar_counts(counts, args.plot_out)
        print(f"Saved bar chart -> {args.plot_out}")

    if args.timeline_out:
        tl = analyzer.timeline(bucket=args.timeline_bucket, entries=entries)
        Visualizer.timeline(tl, args.timeline_out)
        print(f"Saved timeline -> {args.timeline_out}")

def _parse_date(s: str):
    # Try YYYY-MM-DD first, then full ISO
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # As a last resort, try parsing seconds only
    try:
        return datetime.fromisoformat(s)
    except Exception:
        raise SystemExit(f"Could not parse date: {s}")

if __name__ == "__main__":
    main()
