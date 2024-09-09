import tkinter as tk
from tkinter import ttk

def create_progress_bar(parent, value):
    progress = ttk.Progressbar(parent, orient="horizontal", length=300, mode="determinate")
    progress['value'] = value
    progress.pack()
    return progress
