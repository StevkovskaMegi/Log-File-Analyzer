from typing import Dict, Optional
import matplotlib
matplotlib.use('Agg')  # headless
import matplotlib.pyplot as plt

class Visualizer:
    @staticmethod
    def bar_counts(counts: Dict[str, int], out_path: str, title: str = "Log entries by level"):
        levels = ["INFO","WARNING","ERROR","DEBUG","UNKNOWN"]
        values = [counts.get(l, 0) for l in levels]
        plt.figure()
        plt.bar(levels, values)
        plt.title(title)
        plt.xlabel("Level")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()

    @staticmethod
    def timeline(timeline_map, out_path: str, title: str = "Log entries over time"):
        # timeline_map: dict of datetime->count
        items = sorted(timeline_map.items(), key=lambda kv: kv[0])
        xs = [k for k,_ in items]
        ys = [v for _,v in items]
        plt.figure()
        plt.plot(xs, ys, marker='o')
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
