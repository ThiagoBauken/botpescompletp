#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste simples de carregamento do GIF"""

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys

def safe_print(text):
    """Print com fallback para emojis"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def test_gif():
    root = tk.Tk()
    root.title("Teste GIF")
    root.geometry("800x600")

    gif_path = os.path.join("templates", "motion.gif")

    if not os.path.exists(gif_path):
        safe_print(f"[X] GIF nao encontrado: {gif_path}")
        label = tk.Label(root, text=f"GIF nao encontrado:\n{gif_path}", fg="red")
        label.pack(pady=20)
        root.mainloop()
        return

    safe_print(f"[OK] GIF encontrado: {gif_path}")

    # Carregar GIF
    gif_image = Image.open(gif_path)
    frames = []
    durations = []

    try:
        for frame in ImageSequence.Iterator(gif_image):
            # Preservar proporção original
            original_width, original_height = frame.size
            target_height = 96  # Altura para teste (maior para ver melhor)
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)

            safe_print(f"Original: {original_width}x{original_height}, Redimensionado: {target_width}x{target_height}")

            resized = frame.copy().resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            frames.append(photo)
            duration = frame.info.get('duration', 100)
            durations.append(duration)
    except EOFError:
        pass

    safe_print(f"[OK] {len(frames)} frames carregados")

    # Criar label e título
    container = tk.Frame(root)
    container.pack(pady=50)

    gif_label = tk.Label(container)
    gif_label.pack(side='left', padx=10)

    title_label = tk.Label(container, text="Fishing MageBOT", font=('Arial', 24, 'bold'))
    title_label.pack(side='left', padx=10)

    # Animar
    current_frame = [0]

    def animate():
        gif_label.config(image=frames[current_frame[0]])
        current_frame[0] = (current_frame[0] + 1) % len(frames)
        root.after(durations[current_frame[0]], animate)

    animate()

    root.mainloop()

if __name__ == "__main__":
    test_gif()
