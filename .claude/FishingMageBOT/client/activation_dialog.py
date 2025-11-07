#!/usr/bin/env python3
"""
🔐 Diálogo de Ativação do Bot
Tela para inserir Login/Senha/License Key
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform


class ActivationDialog:
    """
    Diálogo de ativação com login/senha/license key

    Campos:
    - Login (email ou username)
    - Senha (qualquer senha)
    - License Key (do Keymaster)
    - Checkbox: Manter conectado
    """

    def __init__(self, parent=None):
        self.result = None
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("🔐 Ativação - Fishing Bot")
        self.root.geometry("450x400")
        self.root.resizable(False, False)

        # Centralizar janela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Configurar estilo
        self._setup_style()

        # Construir UI
        self._build_ui()

        # Fechar janela = cancelar
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _setup_style(self):
        """Configurar estilo visual"""
        style = ttk.Style()
        style.theme_use('clam')

        # Cores
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        entry_bg = "#3c3c3c"
        button_bg = "#0078d7"

        self.root.configure(bg=bg_color)

    def _build_ui(self):
        """Construir interface"""

        # ═══════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════

        header_frame = tk.Frame(self.root, bg="#2b2b2b")
        header_frame.pack(fill=tk.X, pady=(20, 10))

        tk.Label(
            header_frame,
            text="🎣 Fishing Bot",
            font=("Segoe UI", 18, "bold"),
            bg="#2b2b2b",
            fg="#0078d7"
        ).pack()

        tk.Label(
            header_frame,
            text="Ative sua licença para começar",
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="#cccccc"
        ).pack()

        # ═══════════════════════════════════════════════════════
        # FORMULÁRIO
        # ═══════════════════════════════════════════════════════

        form_frame = tk.Frame(self.root, bg="#2b2b2b")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Campo: Login
        tk.Label(
            form_frame,
            text="Login:",
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="#ffffff"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.login_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=5
        )
        self.login_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 15))

        # Campo: Senha (opcional - apenas salva localmente para conveniência)
        tk.Label(
            form_frame,
            text="Senha (opcional):",
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="#ffffff"
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=5,
            show="●"  # Ocultar senha
        )
        self.password_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 15))

        # Campo: License Key
        tk.Label(
            form_frame,
            text="License Key:",
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="#ffffff"
        ).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))

        self.license_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=5
        )
        self.license_entry.grid(row=5, column=0, sticky=tk.EW, pady=(0, 15))

        # Checkbox: Manter conectado
        self.remember_var = tk.BooleanVar(value=True)
        self.remember_check = tk.Checkbutton(
            form_frame,
            text="Manter conectado (salvar credenciais)",
            variable=self.remember_var,
            font=("Segoe UI", 9),
            bg="#2b2b2b",
            fg="#cccccc",
            selectcolor="#3c3c3c",
            activebackground="#2b2b2b",
            activeforeground="#ffffff"
        )
        self.remember_check.grid(row=6, column=0, sticky=tk.W, pady=(0, 20))

        # Expandir coluna
        form_frame.columnconfigure(0, weight=1)

        # ═══════════════════════════════════════════════════════
        # BOTÕES
        # ═══════════════════════════════════════════════════════

        button_frame = tk.Frame(self.root, bg="#2b2b2b")
        button_frame.pack(fill=tk.X, padx=40, pady=(0, 20))

        # Botão: Ativar
        self.activate_btn = tk.Button(
            button_frame,
            text="🚀 Ativar",
            font=("Segoe UI", 11, "bold"),
            bg="#0078d7",
            fg="#ffffff",
            activebackground="#005a9e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._on_activate
        )
        self.activate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Botão: Cancelar
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg="#555555",
            fg="#ffffff",
            activebackground="#444444",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._on_cancel
        )
        self.cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Focus no login
        self.login_entry.focus()

        # Enter = Ativar
        self.root.bind('<Return>', lambda e: self._on_activate())

    def _on_activate(self):
        """Ação ao clicar em Ativar"""

        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip() or "default"  # Senha opcional
        license_key = self.license_entry.get().strip()
        remember = self.remember_var.get()

        # Validação básica
        if not login:
            messagebox.showwarning("⚠️ Atenção", "Digite seu login!")
            self.login_entry.focus()
            return

        # Senha é opcional (servidor não valida, apenas salva localmente)

        if not license_key:
            messagebox.showwarning("⚠️ Atenção", "Cole sua license key!")
            self.license_entry.focus()
            return

        # Retornar credenciais
        self.result = {
            "login": login,
            "password": password,
            "license_key": license_key,
            "remember": remember,
            "pc_name": platform.node()
        }

        self.root.quit()
        self.root.destroy()

    def _on_cancel(self):
        """Ação ao clicar em Cancelar"""
        self.result = None
        self.root.quit()
        self.root.destroy()

    def show(self):
        """
        Mostrar diálogo e retornar resultado

        Retorna:
            dict ou None:
                {
                    "login": str,
                    "password": str,
                    "license_key": str,
                    "remember": bool,
                    "pc_name": str
                }
        """
        self.root.mainloop()
        return self.result


# ═══════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    dialog = ActivationDialog()
    result = dialog.show()

    if result:
        print("✅ Ativação solicitada:")
        print(f"   Login: {result['login']}")
        print(f"   Senha: {'*' * len(result['password'])}")
        print(f"   License Key: {result['license_key'][:10]}...")
        print(f"   Manter conectado: {result['remember']}")
        print(f"   PC: {result['pc_name']}")
    else:
        print("❌ Ativação cancelada")
