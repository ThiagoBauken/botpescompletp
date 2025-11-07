#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ultimate Fishing Bot v5.0 - Launcher (No Console)
Este arquivo .pyw inicia o bot sem mostrar o console CMD
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Importar e executar o main
if __name__ == "__main__":
    try:
        import main
        main.main()
    except Exception as e:
        # Em caso de erro, mostrar em uma janela de diálogo
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro ao Iniciar Bot",
                           f"Erro ao iniciar o bot:\n\n{str(e)}\n\nVerifique o arquivo de log para mais detalhes.")
        root.destroy()
        raise
