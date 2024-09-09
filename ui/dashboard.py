import tkinter as tk
from memory_manager import get_memory_info, free_memory_cache
from storage_manager import get_disk_info, get_partition_info

class Dashboard(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Memory Section
        memory_frame = tk.LabelFrame(self, text="Memory Usage", padx=10, pady=10)
        memory_frame.pack(fill="x", padx=5, pady=5)

        memory_info = get_memory_info()
        memory_label = tk.Label(memory_frame, text=f"Used: {memory_info['used']} / {memory_info['total']}")
        memory_label.pack()

        clear_cache_button = tk.Button(memory_frame, text="Clear Cache", command=free_memory_cache)
        clear_cache_button.pack()

        # Storage Section
        storage_frame = tk.LabelFrame(self, text="Storage Usage", padx=10, pady=10)
        storage_frame.pack(fill="x", padx=5, pady=5)

        disk_info = get_disk_info()
        storage_label = tk.Label(storage_frame, text=f"Used: {disk_info['used']} / {disk_info['total']}")
        storage_label.pack()

        # Partition Info
        partitions = get_partition_info()
        partition_list = tk.Listbox(storage_frame)
        for part in partitions:
            partition_list.insert(tk.END, f"{part[0]}: {part[2]} {part[1]}")
        partition_list.pack()

        # Add more sections for swap management, optimization, etc.
