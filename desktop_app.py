import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

from ai_engine import analyze_folder, analyze_cross_format, recommend_cluster


def select_folder():

    folder = filedialog.askdirectory()

    if folder:
        folder_label.config(text=folder)


def run_analysis():

    folder = folder_label.cget("text")

    if folder == "No folder selected":
        messagebox.showerror("Error", "Please select a folder first.")
        return

    output.delete(1.0, tk.END)

    mode = mode_var.get()

    output.insert(tk.END, "\n=== SMART RECOMMENDATION CLUSTERS ===\n")

    if mode == "Standard":

        exact_duplicates, clusters = analyze_folder(folder)

        if exact_duplicates:

            output.insert(tk.END, "\n=== EXACT DUPLICATES ===\n")

            for group in exact_duplicates:

                output.insert(tk.END, "\n")

                for f in group:
                    output.insert(tk.END, f"{f}\n")

    else:

        clusters = analyze_cross_format(folder)

    if not clusters:

        output.insert(tk.END, "\nNo duplicate clusters found.\n")
        return

    for idx, cluster in enumerate(clusters, 1):

        keep, remove = recommend_cluster(cluster)

        output.insert(tk.END, f"\nCluster {idx} ({len(cluster)} Files)\n")

        output.insert(tk.END, f"KEEP: {keep[0]}\n")

        output.insert(tk.END, "Reason:\n")

        for r in keep[2]:
            output.insert(tk.END, f"  - {r}\n")

        output.insert(tk.END, "Suggested for Removal:\n")

        for f, _, _ in remove:
            output.insert(tk.END, f"  - {f}\n")


root = tk.Tk()
root.title("AI Smart Duplicate File Finder")
root.geometry("1000x700")


tk.Button(root, text="📁 Select Folder", command=select_folder).pack(pady=5)

folder_label = tk.Label(root, text="No folder selected", fg="blue")
folder_label.pack()


mode_var = tk.StringVar(value="Standard")

tk.Label(root, text="\nSelect Mode:", font=("Arial", 11, "bold")).pack()

tk.Radiobutton(root, text="Standard Mode", variable=mode_var, value="Standard").pack()
tk.Radiobutton(root, text="Cross-Format Mode", variable=mode_var, value="Cross").pack()


tk.Button(root, text="🧠 Run AI Analysis", command=run_analysis).pack(pady=10)


output = scrolledtext.ScrolledText(root, width=130, height=35)
output.pack(padx=10, pady=10)


root.mainloop()