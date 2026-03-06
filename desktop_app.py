import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
from send2trash import send2trash
from PIL import Image, ImageTk

from ai_engine import (
    analyze_folder,
    analyze_cross_format,
    analyze_deep_ai,
    recommend_cluster,
    generate_cluster_explanation,
    get_file_metadata,
    get_image_thumbnail,
    export_report_txt,
    export_report_csv,
    TEXT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    AUDIO_EXTENSIONS,
)


# ============================================================
# THEME
# ============================================================

COLOR_BG      = "#0d0d1a"
COLOR_PANEL   = "#13131f"
COLOR_PANEL2  = "#1a1a2e"
COLOR_ACCENT  = "#6d28d9"
COLOR_ACCENT2 = "#8b5cf6"
COLOR_FG      = "#e2e8f0"
COLOR_MUTED   = "#64748b"
COLOR_GREEN   = "#34d399"
COLOR_RED     = "#f87171"
COLOR_GOLD    = "#fbbf24"
COLOR_BLUE    = "#60a5fa"
COLOR_PURPLE  = "#c084fc"
COLOR_DIVIDER = "#1e1e3a"
COLOR_WARN    = "#fb923c"

FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 11, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_SMALL  = ("Segoe UI", 8)
FONT_MONO   = ("Consolas", 9)
FONT_MONO_B = ("Consolas", 9, "bold")


# ============================================================
# GLOBAL STATE
# ============================================================

file_checkboxes: dict = {}

last_exact_groups  = []
last_near_clusters = []
last_sim_reasons   = {}
last_summary       = {}
last_all_files     = []

preview_image_ref  = None


# ============================================================
# HELPERS
# ============================================================

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)


def append_output(text, tag=None):
    output.config(state=tk.NORMAL)
    if tag:
        output.insert(tk.END, text, tag)
    else:
        output.insert(tk.END, text)
    output.see(tk.END)
    output.config(state=tk.DISABLED)


def clear_output():
    output.config(state=tk.NORMAL)
    output.delete(1.0, tk.END)
    output.config(state=tk.DISABLED)
    file_checkboxes.clear()


def set_ui_busy(busy):
    state = tk.DISABLED if busy else tk.NORMAL
    run_btn.config(state=state)
    folder_btn.config(state=state)
    delete_btn.config(state=state)
    export_btn.config(state=state)
    for rb in mode_buttons:
        rb.config(state=state)
    if busy:
        progress_bar.start(10)
        status_label.config(text="⚙️  Analysing…", fg=COLOR_GOLD)
    else:
        progress_bar.stop()
        progress_bar["value"] = 0
        status_label.config(text="✅  Ready", fg=COLOR_GREEN)


def update_status(msg):
    root.after(0, lambda: status_label.config(text=f"⚙️  {msg}", fg=COLOR_GOLD))


# ============================================================
# SUMMARY DASHBOARD
# ============================================================

def render_summary_dashboard(summary):
    def _render():
        for w in dashboard_frame.winfo_children():
            w.destroy()
        cards = [
            ("📂", "Files Scanned",    str(summary.get("total_files", 0)),        COLOR_BLUE),
            ("🔁", "Duplicates Found", str(summary.get("duplicate_files", 0)),     COLOR_RED),
            ("💾", "Space Wasted",     summary.get("wasted_str", "0 B"),           COLOR_GOLD),
            ("🎯", "Exact Groups",     str(summary.get("exact_groups_count", 0)),  COLOR_GREEN),
            ("🧠", "Near Clusters",    str(summary.get("near_clusters_count", 0)), COLOR_PURPLE),
        ]
        for emoji, label, value, color in cards:
            card = tk.Frame(dashboard_frame, bg=COLOR_PANEL2, padx=12, pady=8)
            card.pack(side=tk.LEFT, padx=6, pady=4)
            tk.Label(card, text=emoji, font=("Segoe UI", 18), bg=COLOR_PANEL2, fg=color).pack()
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg=COLOR_PANEL2, fg=color).pack()
            tk.Label(card, text=label, font=FONT_SMALL, bg=COLOR_PANEL2, fg=COLOR_MUTED).pack()
    root.after(0, _render)


# ============================================================
# FILE PREVIEW PANEL
# ============================================================

def show_file_preview(path):
    global preview_image_ref
    for w in preview_inner.winfo_children():
        w.destroy()
    preview_image_ref = None

    if not path or not os.path.exists(path):
        return

    meta = get_file_metadata(path)
    ext  = meta["ext"]

    tk.Label(preview_inner, text="📋 File Preview",
             font=FONT_BOLD, bg=COLOR_PANEL2, fg=COLOR_ACCENT2).pack(anchor="w", pady=(0, 6))

    info_frame = tk.Frame(preview_inner, bg=COLOR_PANEL2)
    info_frame.pack(fill=tk.X, pady=(0, 8))

    def info_row(label, val):
        row = tk.Frame(info_frame, bg=COLOR_PANEL2)
        row.pack(fill=tk.X, pady=1)
        tk.Label(row, text=label, width=10, anchor="w",
                 font=FONT_SMALL, bg=COLOR_PANEL2, fg=COLOR_MUTED).pack(side=tk.LEFT)
        tk.Label(row, text=val, anchor="w",
                 font=FONT_SMALL, bg=COLOR_PANEL2, fg=COLOR_FG, wraplength=180).pack(side=tk.LEFT)

    info_row("Name:",     os.path.basename(path))
    info_row("Size:",     meta["size_str"])
    info_row("Modified:", meta["modified"])
    info_row("Type:",     ext or "unknown")

    ttk.Separator(preview_inner, orient="horizontal").pack(fill=tk.X, pady=6)

    if ext in IMAGE_EXTENSIONS:
        img = get_image_thumbnail(path, size=(200, 200))
        if img:
            try:
                tk_img = ImageTk.PhotoImage(img)
                preview_image_ref = tk_img
                tk.Label(preview_inner, image=tk_img, bg=COLOR_PANEL2).pack(pady=4)
            except Exception:
                pass
    elif ext in TEXT_EXTENSIONS:
        from ai_engine import extract_text
        snippet = extract_text(path)[:300]
        if snippet:
            tk.Label(preview_inner, text="Preview:", font=FONT_SMALL,
                     bg=COLOR_PANEL2, fg=COLOR_MUTED).pack(anchor="w")
            txt = tk.Text(preview_inner, height=8, width=28,
                          font=("Consolas", 8), bg=COLOR_BG, fg=COLOR_FG,
                          relief=tk.FLAT, wrap=tk.WORD)
            txt.insert(tk.END, snippet + "…")
            txt.config(state=tk.DISABLED)
            txt.pack(fill=tk.X, pady=4)
    elif ext in AUDIO_EXTENSIONS:
        tk.Label(preview_inner, text="🎵 Audio File",
                 font=FONT_BOLD, bg=COLOR_PANEL2, fg=COLOR_BLUE).pack(pady=20)


# ============================================================
# CHECKBOX FILE ENTRY
# ============================================================

def add_file_entry(path, color=COLOR_FG, indent=6, pre_check=False):
    var = tk.BooleanVar(value=pre_check)
    file_checkboxes[path] = var

    cb = tk.Checkbutton(
        output, variable=var,
        bg="#0a0a14", activebackground="#0a0a14",
        selectcolor="#2d2d4e", relief=tk.FLAT, cursor="hand2",
    )

    btn = tk.Button(
        output,
        text=f"  {os.path.basename(path)}",
        anchor="w", font=FONT_MONO,
        fg=color, bg="#0a0a14",
        activebackground="#1a1a2e", activeforeground=COLOR_ACCENT2,
        relief=tk.FLAT, cursor="hand2",
        command=lambda p=path: show_file_preview(p),
    )
    btn.bind("<Enter>", lambda e, b=btn: b.config(fg=COLOR_ACCENT2))
    btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(fg=c))

    output.config(state=tk.NORMAL)
    output.insert(tk.END, " " * indent)
    output.window_create(tk.END, window=cb)
    output.window_create(tk.END, window=btn)
    output.insert(tk.END, "\n")
    output.config(state=tk.DISABLED)


# ============================================================
# DELETE SELECTED
# ============================================================

def delete_selected():
    targets = [p for p, v in file_checkboxes.items() if v.get()]
    if not targets:
        messagebox.showinfo("Nothing selected",
                            "Tick the checkboxes next to files you want to remove.")
        return

    preview_lines = "\n".join(os.path.basename(t) for t in targets[:10])
    if len(targets) > 10:
        preview_lines += f"\n…and {len(targets) - 10} more"

    if not messagebox.askyesno("Confirm Delete",
                               f"Send {len(targets)} file(s) to the Recycle Bin?\n\n{preview_lines}"):
        return

    errors = []
    for path in targets:
        try:
            send2trash(path)
            file_checkboxes.pop(path, None)
        except Exception as e:
            errors.append(f"{os.path.basename(path)}: {e}")

    if errors:
        messagebox.showerror("Some files could not be moved", "\n".join(errors))
    else:
        messagebox.showinfo("Done ✅", f"{len(targets)} file(s) moved to Recycle Bin.")


# ============================================================
# EXPORT REPORT
# ============================================================

def export_report():
    if not last_summary:
        messagebox.showinfo("No results", "Run an analysis first before exporting.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text report", "*.txt"), ("CSV spreadsheet", "*.csv")],
        title="Save Duplicate Report",
    )
    if not path:
        return
    try:
        if path.endswith(".csv"):
            export_report_csv(path, last_exact_groups, last_near_clusters, last_sim_reasons)
        else:
            export_report_txt(path, last_exact_groups, last_near_clusters,
                              last_sim_reasons, last_summary)
        messagebox.showinfo("Exported ✅", f"Report saved to:\n{path}")
    except Exception as e:
        messagebox.showerror("Export failed", str(e))


# ============================================================
# THRESHOLD WARNING
# ============================================================

# Stage map: 1→0.20, 2→0.35, 3→0.45, 4→0.55, 5→0.65
THRESHOLD_STAGES = {1: 0.20, 2: 0.35, 3: 0.45, 4: 0.55, 5: 0.65}
STAGE_LABELS = {
    1: "⚠️ Stage 1 — Very loose, almost everything matches",
    2: "⚠️ Stage 2 — Low threshold, many false positives",
    3: "⚠️ Stage 3 — Moderate, loosely related files match",
    4: "Stage 4 — Balanced detection",
    5: "Stage 5 — Strict, only close matches (default)",
}
STAGE_COLORS = {
    1: COLOR_RED,
    2: COLOR_WARN,
    3: COLOR_GOLD,
    4: COLOR_MUTED,
    5: COLOR_FG,
}

def _snap_to_stage(*_):
    """Snap slider to nearest stage and update display."""
    raw = threshold_var.get()
    # Find nearest stage (1–5)
    stage = min(THRESHOLD_STAGES, key=lambda s: abs(THRESHOLD_STAGES[s] - raw))
    snapped = THRESHOLD_STAGES[stage]
    # Avoid recursive callback loop
    if abs(raw - snapped) > 0.001:
        threshold_var.set(snapped)
        return
    threshold_display.set(f"Stage {stage}  ({snapped:.2f})")
    threshold_warn.config(text=STAGE_LABELS[stage], fg=STAGE_COLORS[stage])

def _on_threshold_change(*_):
    _snap_to_stage()


# ============================================================
# ANALYSIS RUNNER
# ============================================================

def run_analysis():
    folder = folder_label.cget("text")
    if folder == "No folder selected":
        messagebox.showerror("Error", "Please select a folder first.")
        return

    mode      = mode_var.get()
    threshold = threshold_var.get()
    clear_output()
    set_ui_busy(True)

    def task():
        try:
            _run(folder, mode, threshold)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            root.after(0, lambda: append_output(f"\n❌ Error: {e}\n{tb}\n", "error"))
        finally:
            root.after(0, lambda: set_ui_busy(False))

    threading.Thread(target=task, daemon=True).start()


def _run(folder, mode, threshold):
    global last_exact_groups, last_near_clusters, last_sim_reasons, last_summary, last_all_files

    def log(msg):
        root.after(0, lambda m=msg: append_output(m + "\n", "info"))
        root.after(0, lambda m=msg: update_status(m))

    def section(msg):
        root.after(0, lambda m=msg: append_output("\n" + m + "\n", "section"))

    # ── STANDARD ──
    if mode == "Standard":
        section("══════════════  STANDARD MODE: SHA-256 + TF-IDF  ══════════════")
        exact_dups, clusters, sim_reasons, summary, all_files = analyze_folder(
            folder, threshold=threshold, progress_callback=log)

        last_exact_groups  = exact_dups
        last_near_clusters = clusters
        last_sim_reasons   = sim_reasons
        last_summary       = summary
        last_all_files     = all_files

        render_summary_dashboard(summary)

        if exact_dups:
            section("── EXACT DUPLICATES (SHA-256 Match) ──")
            for idx, group in enumerate(exact_dups, 1):
                root.after(0, lambda i=idx, g=group: _render_exact_group(i, g))
        else:
            log("✅ No exact duplicates found.")

        section("── NEAR-DUPLICATE CLUSTERS ──")
        if not clusters:
            log("✅ No near-duplicate clusters found.")
        else:
            for idx, cluster in enumerate(clusters, 1):
                keep, remove = recommend_cluster(cluster)
                pr = {k: v for k, v in sim_reasons.items()
                      if k[0] in cluster and k[1] in cluster}
                root.after(0, lambda i=idx, c=cluster, k=keep, r=remove, p=pr:
                           _render_standard_cluster(i, c, k, r, p))

    # ── CROSS FORMAT ──
    elif mode == "Cross":
        section("══════════  CROSS-FORMAT MODE: TF-IDF + pHash + Audio  ══════════")
        clusters, sim_reasons, summary, all_files = analyze_cross_format(
            folder, threshold=threshold, progress_callback=log)

        last_exact_groups  = []
        last_near_clusters = clusters
        last_sim_reasons   = sim_reasons
        last_summary       = summary
        last_all_files     = all_files

        render_summary_dashboard(summary)

        section("── CROSS-FORMAT DUPLICATE CLUSTERS ──")
        if not clusters:
            log("✅ No cross-format duplicates found.")
        else:
            for idx, cluster in enumerate(clusters, 1):
                keep, remove = recommend_cluster(cluster)
                pr = {k: v for k, v in sim_reasons.items()
                      if k[0] in cluster and k[1] in cluster}
                root.after(0, lambda i=idx, c=cluster, k=keep, r=remove, p=pr:
                           _render_standard_cluster(i, c, k, r, p))

    # ── DEEP AI ──
    elif mode == "DeepAI":
        section("══════════  DEEP AI MODE: Sentence Transformers + FAISS + CLIP  ══════════")
        log("🚀 Initialising Deep AI engine…")
        clusters, sim_scores, sim_reasons, summary, all_files = analyze_deep_ai(
            folder, threshold=threshold, progress_callback=log)

        last_exact_groups  = []
        last_near_clusters = clusters
        last_sim_reasons   = sim_reasons
        last_summary       = summary
        last_all_files     = all_files

        render_summary_dashboard(summary)

        section("── AI-POWERED DUPLICATE CLUSTERS ──")
        if not clusters:
            log("✅ No semantic duplicates detected by Deep AI engine.")
        else:
            log(f"🔎 Found {len(clusters)} duplicate cluster(s).\n")
            for idx, cluster in enumerate(clusters, 1):
                keep, remove = recommend_cluster(cluster)
                explanation  = generate_cluster_explanation(cluster, keep, remove, sim_reasons)
                root.after(0, lambda i=idx, c=cluster, k=keep, r=remove, ex=explanation:
                           _render_deep_ai_cluster(i, c, k, r, ex))


# ============================================================
# RENDER HELPERS
# ============================================================

def _render_exact_group(idx, group):
    append_output(f"\nGroup {idx} — {len(group)} identical files:\n", "section")
    add_file_entry(group[0], color=COLOR_GREEN)
    for f in group[1:]:
        add_file_entry(f, color=COLOR_RED, pre_check=True)


def _render_standard_cluster(idx, cluster, keep, remove, sim_reasons=None):
    append_output(f"\n{'─' * 68}\n", "divider")

    # Determine category from the majority file type in the cluster
    def _cat(f):
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_EXTENSIONS: return "🖼️  Images"
        if ext in AUDIO_EXTENSIONS: return "🎵 Audio"
        if ext == ".pdf":           return "📄 PDF"
        if ext in {".docx", ".txt", ".xlsx", ".pptx"}: return "📝 Documents"
        return "📁 Files"

    from collections import Counter
    cat_counts = Counter(_cat(f) for f in cluster)
    cat = cat_counts.most_common(1)[0][0]

    append_output(f"Cluster {idx}  ·  {cat}  ·  {len(cluster)} files\n", "section")

    if sim_reasons:
        for (f1, f2), reason in sim_reasons.items():
            if f1 in cluster and f2 in cluster:
                append_output(f"  🎯 {reason}\n", "ai")
                break

    append_output("  ✅ KEEP:\n", "keep")
    add_file_entry(keep[0], color=COLOR_GREEN)
    meta = get_file_metadata(keep[0])
    append_output(f"      {meta['size_str']}  ·  modified {meta['modified']}"
                  f"  ·  {', '.join(keep[2])}\n", "info")

    if remove:
        append_output("  🗑️  Suggested for removal:\n", "remove")
        for f, _, _ in remove:
            add_file_entry(f, color=COLOR_RED)
            meta = get_file_metadata(f)
            append_output(f"      {meta['size_str']}  ·  modified {meta['modified']}\n", "info")


def _render_deep_ai_cluster(idx, cluster, keep, remove, explanation):
    similarity_text, keep_line = explanation
    append_output(f"\n{'═' * 60}\n", "divider")

    from collections import Counter
    def _cat(f):
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_EXTENSIONS: return "🖼️  Images"
        if ext in AUDIO_EXTENSIONS: return "🎵 Audio"
        if ext == ".pdf":           return "📄 PDF"
        if ext in {".docx", ".txt", ".xlsx", ".pptx"}: return "📝 Documents"
        return "📁 Files"
    cat_counts = Counter(_cat(f) for f in cluster)
    cat = cat_counts.most_common(1)[0][0]

    append_output(f"Cluster {idx}  ·  {cat}  ·  {len(cluster)} files\n", "section")

    if similarity_text:
        for line in similarity_text.split("\n"):
            append_output(f"  🎯 {line}\n", "ai")

    append_output("  ✅ KEEP:\n", "keep")
    add_file_entry(keep[0], color=COLOR_GREEN)
    meta = get_file_metadata(keep[0])
    append_output(f"      {meta['size_str']}  ·  modified {meta['modified']}\n", "info")

    if remove:
        append_output("  🗑️  Remove:\n", "remove")
        for f, _, _ in remove:
            add_file_entry(f, color=COLOR_RED)
            meta = get_file_metadata(f)
            append_output(f"      {meta['size_str']}  ·  modified {meta['modified']}\n", "info")


# ============================================================
# UI SETUP
# ============================================================

root = tk.Tk()
root.title("🧠 AI Smart Duplicate File Finder")
root.geometry("1300x860")
root.configure(bg=COLOR_BG)
root.resizable(True, True)

# ── HEADER ───────────────────────────────────────────────────
header = tk.Frame(root, bg=COLOR_PANEL, pady=10, padx=20)
header.pack(fill=tk.X)
tk.Label(header, text="🧠 AI Smart Duplicate File Finder",
         font=FONT_HEADER, bg=COLOR_PANEL, fg=COLOR_ACCENT2).pack(side=tk.LEFT)
tk.Label(header, text="SanDisk Hackathon  ·  AI / ML Track",
         font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(side=tk.RIGHT, padx=10)

# ── FOLDER ───────────────────────────────────────────────────
ctrl_frame = tk.Frame(root, bg=COLOR_PANEL2, padx=14, pady=8)
ctrl_frame.pack(fill=tk.X, pady=(2, 0))

folder_btn = tk.Button(ctrl_frame, text="📁  Select Folder", command=select_folder,
                       font=FONT_BOLD, bg=COLOR_ACCENT, fg="white", relief=tk.FLAT,
                       padx=12, pady=4, cursor="hand2")
folder_btn.pack(side=tk.LEFT, padx=(0, 10))

folder_label = tk.Label(ctrl_frame, text="No folder selected",
                        fg=COLOR_BLUE, bg=COLOR_PANEL2, font=FONT_MAIN)
folder_label.pack(side=tk.LEFT)

# ── MODE + THRESHOLD ─────────────────────────────────────────
mode_frame = tk.Frame(root, bg=COLOR_PANEL, padx=14, pady=8)
mode_frame.pack(fill=tk.X, pady=(2, 0))

tk.Label(mode_frame, text="Mode:", font=FONT_BOLD,
         bg=COLOR_PANEL, fg=COLOR_FG).pack(side=tk.LEFT, padx=(0, 12))

mode_var = tk.StringVar(value="Standard")
mode_configs = [
    ("Standard",     "Standard",  "SHA-256 + TF-IDF text",              "#1f2937"),
    ("Cross-Format", "Cross",     "TF-IDF + pHash + Audio",              "#1f2937"),
    ("🚀 Deep AI",   "DeepAI",    "Transformers + FAISS + CLIP + Audio",  "#3b0764"),
]
mode_buttons = []
for label, value, tip, selbg in mode_configs:
    frm = tk.Frame(mode_frame, bg=COLOR_PANEL)
    frm.pack(side=tk.LEFT, padx=8)
    rb = tk.Radiobutton(frm, text=label, variable=mode_var, value=value,
                        font=FONT_MAIN, bg=COLOR_PANEL, fg=COLOR_FG,
                        selectcolor=selbg, activebackground=COLOR_PANEL,
                        activeforeground=COLOR_FG, cursor="hand2")
    rb.pack()
    tk.Label(frm, text=tip, font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack()
    mode_buttons.append(rb)

# Threshold
tk.Label(mode_frame, text="  Similarity Threshold:",
         font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(side=tk.LEFT, padx=(20, 4))

threshold_var     = tk.DoubleVar(value=0.65)   # default = Stage 5
threshold_display = tk.StringVar(value="Stage 5  (0.65)")

threshold_slider = ttk.Scale(mode_frame, from_=0.20, to=0.65,
                              orient=tk.HORIZONTAL, variable=threshold_var, length=160)
threshold_slider.pack(side=tk.LEFT)

threshold_val_lbl = tk.Label(mode_frame, textvariable=threshold_display,
                              font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_GOLD, width=16)
threshold_val_lbl.pack(side=tk.LEFT, padx=(4, 2))

threshold_warn = tk.Label(mode_frame, text="Stage 5 — Strict, only close matches (default)",
                           font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_FG)
threshold_warn.pack(side=tk.LEFT, padx=6)

threshold_var.trace_add("write", _on_threshold_change)

# ── ACTION BUTTONS ────────────────────────────────────────────
btn_row = tk.Frame(root, bg=COLOR_BG, pady=6)
btn_row.pack(fill=tk.X, padx=20)

run_btn = tk.Button(btn_row, text="▶  Run AI Analysis", command=run_analysis,
                    font=FONT_BOLD, bg=COLOR_GREEN, fg="#000000",
                    relief=tk.FLAT, padx=18, pady=5, cursor="hand2")
run_btn.pack(side=tk.LEFT, padx=(0, 10))

delete_btn = tk.Button(btn_row, text="🗑️  Delete Selected", command=delete_selected,
                       font=FONT_BOLD, bg=COLOR_RED, fg="white",
                       relief=tk.FLAT, padx=14, pady=5, cursor="hand2")
delete_btn.pack(side=tk.LEFT, padx=(0, 10))

export_btn = tk.Button(btn_row, text="💾  Export Report", command=export_report,
                       font=FONT_BOLD, bg=COLOR_GOLD, fg="#000000",
                       relief=tk.FLAT, padx=14, pady=5, cursor="hand2")
export_btn.pack(side=tk.LEFT)

status_label = tk.Label(btn_row, text="✅  Ready",
                        font=FONT_SMALL, bg=COLOR_BG, fg=COLOR_GREEN)
status_label.pack(side=tk.RIGHT, padx=10)

# ── PROGRESS + STAGE ─────────────────────────────────────────
progress_bar = ttk.Progressbar(root, mode="indeterminate", length=500)
progress_bar.pack(pady=(0, 4))

stage_frame = tk.Frame(root, bg=COLOR_BG)
stage_frame.pack(fill=tk.X, padx=20, pady=(0, 2))
for s in ["📂 Scanning", "🔐 Hashing", "📝 Text AI", "🖼️ Image AI", "🎵 Audio AI", "🔗 Clustering"]:
    tk.Label(stage_frame, text=s, font=FONT_SMALL,
             bg=COLOR_BG, fg=COLOR_MUTED, padx=8).pack(side=tk.LEFT)

# ── DASHBOARD ─────────────────────────────────────────────────
dashboard_frame = tk.Frame(root, bg=COLOR_BG)
dashboard_frame.pack(fill=tk.X, padx=20, pady=(0, 4))

# ── BODY: output + preview ────────────────────────────────────
body_frame = tk.Frame(root, bg=COLOR_BG)
body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

output = scrolledtext.ScrolledText(
    body_frame, font=FONT_MONO, bg="#0a0a14", fg=COLOR_FG,
    insertbackground="white", state=tk.DISABLED,
    wrap=tk.WORD, relief=tk.FLAT, padx=10, pady=10,
)
output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Preview panel
preview_frame = tk.Frame(body_frame, bg=COLOR_PANEL2, width=240)
preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
preview_frame.pack_propagate(False)

tk.Label(preview_frame, text="Click a file to preview",
         font=FONT_SMALL, bg=COLOR_PANEL2, fg=COLOR_MUTED).pack(pady=6)
ttk.Separator(preview_frame, orient="horizontal").pack(fill=tk.X)

preview_canvas = tk.Canvas(preview_frame, bg=COLOR_PANEL2, bd=0, highlightthickness=0)
preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=preview_canvas.yview)
preview_canvas.configure(yscrollcommand=preview_scroll.set)
preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

preview_inner = tk.Frame(preview_canvas, bg=COLOR_PANEL2, padx=10, pady=10)
preview_canvas.create_window((0, 0), window=preview_inner, anchor="nw")
preview_inner.bind("<Configure>",
                   lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all")))

# ── TEXT TAGS ─────────────────────────────────────────────────
output.tag_config("section", foreground=COLOR_GOLD,   font=FONT_MONO_B)
output.tag_config("keep",    foreground=COLOR_GREEN)
output.tag_config("remove",  foreground=COLOR_RED)
output.tag_config("info",    foreground=COLOR_MUTED)
output.tag_config("ai",      foreground=COLOR_PURPLE)
output.tag_config("error",   foreground=COLOR_RED,    font=FONT_MONO_B)
output.tag_config("divider", foreground=COLOR_DIVIDER)

root.mainloop()