import os
import hashlib
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import time


class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Finder")

        self.start_directory = tk.StringVar()
        self.duplicates_tree = ttk.Treeview(root)
        self.duplicates_tree["columns"] = ("Paths",)
        self.duplicates_tree.column("#0", width=0, stretch=tk.NO)
        self.duplicates_tree.column("Paths", anchor=tk.W, width=400)
        self.duplicates_tree.heading("#0", text="", anchor=tk.W)
        self.duplicates_tree.heading(
            "Paths", text="Found Duplicates:", anchor=tk.W)
        self.duplicates_tree.tag_configure(
            "bold", font=("TkDefaultFont", 10, "bold"))
        self.info_label = tk.Label(root, text="")

        browse_button = tk.Button(
            root, text="Select Directory", command=self.browse_directory)
        find_button = tk.Button(
            root, text="Find Duplicates", command=self.find_duplicates)
        delete_button = tk.Button(
            root, text="Delete Selected", command=self.delete_selected)

        browse_button.pack(pady=10)
        find_button.pack(pady=10)
        delete_button.pack(pady=10)
        self.duplicates_tree.pack(expand=True, fill=tk.BOTH, padx=10)
        self.info_label.pack(pady=10)

        self.file_size_label = tk.Label(root, text="")
        self.file_size_label.pack(pady=10)

        self.duplicates_tree.bind("<Double-1>", self.open_folder)

    def browse_directory(self):
        self.start_directory.set(filedialog.askdirectory())

    def hash_file(self, file_path, block_size=65536):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file.read(block_size)
        return hasher.hexdigest()

    def find_duplicates(self):
        start_time = time.time()
        start_path = self.start_directory.get()
        if not start_path:
            self.info_label.config(text="Select a directory first.")
            return

        file_hashes = defaultdict(list)

        for dirpath, dirnames, filenames in os.walk(start_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_hash = self.hash_file(file_path)
                file_hashes[file_hash].append(file_path)

        duplicates = {hash_val: paths for hash_val,
                      paths in file_hashes.items() if len(paths) > 1}

        end_time = time.time()
        self.duration = end_time - start_time

        self.display_duplicates(duplicates)

    def display_duplicates(self, duplicates):
        self.duplicates_tree.delete(*self.duplicates_tree.get_children())
        count = 0
        total_size = 0

        for group_id, paths in enumerate(duplicates.values(), start=1):
            count += len(paths)
            group_text = f"Duplicate {group_id}"
            self.duplicates_tree.insert(
                "", "end", values=(group_text,), tags=("bold",))
            for path in paths:
                self.duplicates_tree.insert("", "end", values=(path,))
                total_size += os.path.getsize(path)

        self.info_label.config(
            text=f"Found {count // 2} duplicates in {len(duplicates)} groups. Time taken: {self.duration:.2f} seconds")

        freed_space_mb = total_size / (2 * 1024 * 1024)
        self.file_size_label.config(
            text=f"Removing duplicates will free up {freed_space_mb:.2f} MB on disk.")

    def open_folder(self, event):
        item = self.duplicates_tree.selection()[0]
        value = self.duplicates_tree.item(item, "values")[0]

        if value.startswith("Duplicate"):
            return

        folder_path = os.path.dirname(value)
        os.startfile(folder_path)

    def delete_selected(self):
        selected_items = self.duplicates_tree.selection()
        if not selected_items:
            return

        confirmation = messagebox.askokcancel(
            "Delete Confirmation", "Are you sure you want to delete selected files?")
        if not confirmation:
            return

        for item in selected_items:
            value = self.duplicates_tree.item(item, "values")[0]

            if value.startswith("Duplicate"):
                continue

            try:
                os.remove(value)
                self.duplicates_tree.delete(item)
                self.info_label.config(text="File(s) deleted successfully.")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to delete file {value}. Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
