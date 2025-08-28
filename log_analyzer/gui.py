import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
from pathlib import Path

from .parser import LogParser
from .analyzer import LogAnalyzer
from .filters import FilterCriteria
from .visualizer import Visualizer

class LogAnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Log File Analyzer")
        self.geometry("900x600")
        self._build_widgets()
        self.parser = LogParser()
        self.analyzer = LogAnalyzer()

    def _build_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Top controls
        ctl = ttk.Frame(frm)
        ctl.pack(fill=tk.X)
        self.path_var = tk.StringVar()
        ttk.Entry(ctl, textvariable=self.path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
        ttk.Button(ctl, text="Browse", command=self._browse).pack(side=tk.LEFT)

        # Filters
        flt = ttk.Frame(frm)
        flt.pack(fill=tk.X, pady=(10,0))
        self.keyword_var = tk.StringVar()
        self.level_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        ttk.Label(flt, text="Keyword").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(flt, textvariable=self.keyword_var, width=20).grid(row=0, column=1, padx=5)
        ttk.Label(flt, text="Level").grid(row=0, column=2, sticky=tk.W)
        ttk.Combobox(flt, textvariable=self.level_var, values=["", "INFO","WARNING","ERROR","DEBUG","UNKNOWN"], width=12).grid(row=0, column=3, padx=5)
        ttk.Label(flt, text="Start (YYYY-MM-DD)").grid(row=0, column=4, sticky=tk.W)
        ttk.Entry(flt, textvariable=self.start_var, width=14).grid(row=0, column=5, padx=5)
        ttk.Label(flt, text="End (YYYY-MM-DD)").grid(row=0, column=6, sticky=tk.W)
        ttk.Entry(flt, textvariable=self.end_var, width=14).grid(row=0, column=7, padx=5)
        ttk.Button(flt, text="Analyze", command=self._analyze).grid(row=0, column=8, padx=(10,0))

        # Results area
        self.text = tk.Text(frm, wrap=tk.NONE, height=20)
        self.text.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        # Save buttons
        savefrm = ttk.Frame(frm)
        savefrm.pack(fill=tk.X, pady=10)
        ttk.Button(savefrm, text="Save Bar Chart", command=self._save_bar).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(savefrm, text="Save Timeline", command=self._save_timeline).pack(side=tk.LEFT)

    def _browse(self):
        path = filedialog.askopenfilename(title="Select log file", filetypes=[("Log files","*.log"),("All","*.*")])
        if path:
            self.path_var.set(path)

    def _parse_date(self, s):
        s = s.strip()
        if not s: return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        messagebox.showerror("Invalid date", f"Could not parse date: {s}")
        return None

    def _analyze(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("No file", "Please choose a log file.")
            return
        self.text.delete("1.0", tk.END)
        self.analyzer = LogAnalyzer()  # reset
        crit = FilterCriteria(
            keyword=(self.keyword_var.get().strip() or None),
            level=(self.level_var.get().strip() or None),
            start=self._parse_date(self.start_var.get()),
            end=self._parse_date(self.end_var.get())
        )
        def work():
            try:
                for entry in self.parser.parse_file(path):
                    self.analyzer.ingest([entry])
                entries = self.analyzer.entries
                if any([crit.keyword, crit.level, crit.start, crit.end]):
                    entries = self.analyzer.filter(crit)
                summary = self.analyzer.summary(entries)
                self._show_summary(summary)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        threading.Thread(target=work, daemon=True).start()

    def _show_summary(self, summary: dict):
        self.text.insert(tk.END, "Summary\n\n")
        for k,v in summary.items():
            self.text.insert(tk.END, f"{k}: {v}\n")

    def _save_bar(self):
        counts = self.analyzer.counts_by_level()
        out = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if out:
            Visualizer.bar_counts(counts, out)
            messagebox.showinfo("Saved", f"Bar chart saved to {out}")

    def _save_timeline(self):
        tl = self.analyzer.timeline(bucket='hour')
        out = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if out:
            Visualizer.timeline(tl, out)
            messagebox.showinfo("Saved", f"Timeline saved to {out}")

def main():
    app = LogAnalyzerGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
