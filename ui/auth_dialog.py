#!/usr/bin/env python3
"""
🔐 Ultimate Fishing Bot v5.0 - Sistema Completo de Autenticação
Suporta: Login, Cadastro, Recuperação de Senha
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform
import os
import sys
import re
import traceback
import random
import string

# Importar sistema i18n
try:
    from utils.i18n import i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("[WARN] i18n not available in auth_dialog")

# Função de tradução
def _(text, **kwargs):
    """Função auxiliar de tradução"""
    if I18N_AVAILABLE:
        return i18n.get_text(text, **kwargs)
    return text


def resource_path(relative_path):
    """
    Retorna o caminho absoluto para um recurso, funcionando em .exe compilado (Nuitka).
    """
    try:
        # Lista de arquivos compilados DENTRO do .exe
        compiled_resources = ["magoicon.ico"]
        normalized_path = relative_path.replace("\\", "/")
        is_compiled = normalized_path in [r.replace("\\", "/") for r in compiled_resources]

        # Se for recurso compilado E estiver em modo frozen
        if is_compiled and getattr(sys, 'frozen', False):
            # ✅ NUITKA: usar __compiled__.containing_dir
            try:
                base_path = __compiled__.containing_dir
                return os.path.join(base_path, relative_path)
            except NameError:
                # PYINSTALLER: fallback para _MEIPASS
                if hasattr(sys, '_MEIPASS'):
                    base_path = sys._MEIPASS
                    return os.path.join(base_path, relative_path)

        # Para recursos externos ou modo Python normal
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            # Rodando como script Python
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"[WARN] Erro ao resolver caminho de recurso: {e}")
        return relative_path


class AuthDialog:
    """
    Dialog completo de autenticação

    Suporta 3 modos:
    1. LOGIN: Usuário existente faz login
    2. CADASTRO: Primeira ativação da license key
    3. RECUPERAÇÃO: Resetar senha via email/código
    """

    @staticmethod
    def _generate_random_title():
        """Gera um título aleatório com 8-12 caracteres"""
        length = random.randint(8, 12)
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def __init__(self, license_manager, credential_manager):
        self.license_manager = license_manager
        self.credential_manager = credential_manager
        self.result = None
        self.root = None
        self.validating = False

        # Modo inicial (verifica se já tem credenciais salvas)
        saved_creds = self.credential_manager.load_credentials()
        self.initial_mode = "login" if saved_creds else "register"

        # ✅ Armazenar referências de widgets para atualização de idioma
        self.ui_elements = {}

    # ═══════════════════════════════════════════════════════
    # DIALOGS CUSTOMIZADOS COM ÍCONE
    # ═══════════════════════════════════════════════════════

    def _custom_dialog(self, title, message, dialog_type="info", buttons="ok"):
        """
        Dialog customizado com ícone correto

        Args:
            title: Título do dialog
            message: Mensagem
            dialog_type: 'info', 'warning', 'error'
            buttons: 'ok', 'yesno'

        Returns:
            True/False para 'yesno', None para 'ok'
        """
        dialog = tk.Toplevel(self.root if self.root else None)
        dialog.title(title)
        dialog.geometry("450x200")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        if self.root:
            dialog.transient(self.root)
        dialog.grab_set()

        # ✅ Aplicar ícone customizado
        try:
            icon_path = resource_path("magoicon.ico")
            if os.path.exists(icon_path):
                dialog.iconbitmap(icon_path)
        except:
            pass

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        result = {'value': None}

        # Frame principal
        frame = tk.Frame(dialog, bg='#2d2d2d', padx=25, pady=20)
        frame.pack(fill='both', expand=True)

        # Ícone e cor baseado no tipo
        icon_map = {
            'info': ('ℹ️', '#0078d7'),
            'warning': ('⚠️', '#ffc107'),
            'error': ('❌', '#dc3545')
        }
        icon, color = icon_map.get(dialog_type, icon_map['info'])

        # Header com ícone
        header_frame = tk.Frame(frame, bg='#2d2d2d')
        header_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            header_frame,
            text=icon,
            font=('Arial', 24),
            fg=color,
            bg='#2d2d2d'
        ).pack(side='left', padx=(0, 10))

        tk.Label(
            header_frame,
            text=title,
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(side='left')

        # Mensagem
        tk.Label(
            frame,
            text=message,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2d2d2d',
            wraplength=380,
            justify='left'
        ).pack(pady=(0, 20))

        # Botões
        btn_frame = tk.Frame(frame, bg='#2d2d2d')
        btn_frame.pack(fill='x')

        if buttons == 'yesno':
            def on_yes():
                result['value'] = True
                dialog.destroy()

            def on_no():
                result['value'] = False
                dialog.destroy()

            tk.Button(
                btn_frame,
                text="✅ Sim",
                font=('Arial', 10, 'bold'),
                bg='#28a745',
                fg='white',
                relief='flat',
                padx=20,
                pady=8,
                cursor='hand2',
                command=on_yes
            ).pack(side='left', fill='x', expand=True, padx=(0, 5))

            tk.Button(
                btn_frame,
                text="❌ Não",
                font=('Arial', 10),
                bg='#dc3545',
                fg='white',
                relief='flat',
                padx=20,
                pady=8,
                cursor='hand2',
                command=on_no
            ).pack(side='left', fill='x', expand=True, padx=(5, 0))
        else:  # ok
            def on_ok():
                result['value'] = None
                dialog.destroy()

            tk.Button(
                btn_frame,
                text="✅ OK",
                font=('Arial', 10, 'bold'),
                bg='#0078d7',
                fg='white',
                relief='flat',
                padx=30,
                pady=8,
                cursor='hand2',
                command=on_ok
            ).pack(fill='x')

            # Enter = OK
            dialog.bind('<Return>', lambda e: on_ok())

        dialog.wait_window()
        return result['value']

    def _show_info(self, title, message):
        """Substituir messagebox.showinfo"""
        return self._custom_dialog(title, message, 'info', 'ok')

    def _show_warning(self, title, message):
        """Substituir messagebox.showwarning"""
        return self._custom_dialog(title, message, 'warning', 'ok')

    def _show_error(self, title, message):
        """Substituir messagebox.showerror"""
        return self._custom_dialog(title, message, 'error', 'ok')

    def _ask_yesno(self, title, message):
        """Substituir messagebox.askyesno"""
        return self._custom_dialog(title, message, 'warning', 'yesno')

    def show(self):
        """Mostrar diálogo e retornar resultado"""
        self.root = tk.Tk()

        # ✅ Gerar título aleatório (igual à main_window)
        random_title = self._generate_random_title()
        self.root.title(random_title)

        self.root.geometry("600x780")
        self.root.configure(bg='#2d2d2d')

        # ✅ PERMITIR REDIMENSIONAMENTO com tamanho mínimo
        self.root.resizable(True, True)
        self.root.minsize(550, 650)  # Tamanho mínimo para evitar quebra da interface

        # ✅ Configurar ícone personalizado da janela
        try:
            icon_path = resource_path("magoicon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"[OK] Ícone personalizado carregado: {icon_path}")
            else:
                print(f"[WARN] Ícone não encontrado: {icon_path}")
        except Exception as e:
            print(f"[WARN] Erro ao carregar ícone: {e}")

        # Centralizar janela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Fechar janela = cancelar
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)

        self.create_widgets()

        # Aguardar resultado
        self.root.mainloop()

        return self.result

    def create_widgets(self):
        """Criar widgets do diálogo"""
        main_frame = tk.Frame(self.root, bg='#2d2d2d', padx=25, pady=20)
        main_frame.pack(fill='both', expand=True)

        # ═══════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════

        header_frame = tk.Frame(main_frame, bg='#2d2d2d')
        header_frame.pack(fill='x', pady=(0, 15))

        # ─────────────────────────────────────────────────────────
        # Seletor de Idioma (topo direito)
        # ─────────────────────────────────────────────────────────

        language_frame = tk.Frame(header_frame, bg='#2d2d2d')
        language_frame.pack(side='right', padx=(0, 0))

        tk.Label(
            language_frame,
            text="🌐",
            font=('Arial', 12),
            fg='#cccccc',
            bg='#2d2d2d'
        ).pack(side='left', padx=(0, 5))

        self.language_var = tk.StringVar(value=i18n.current_language if I18N_AVAILABLE else 'pt')
        self.language_buttons = {}  # Armazenar referências dos botões
        languages = [
            ('🇧🇷 PT', 'pt'),
            ('🇺🇸 EN', 'en'),
            ('🇪🇸 ES', 'es'),
            ('🇷🇺 RU', 'ru'),
            ('🇨🇳 ZH', 'zh')
        ]

        for lang_text, lang_code in languages:
            btn = tk.Button(
                language_frame,
                text=lang_text,
                font=('Arial', 8),
                bg='#404040' if self.language_var.get() != lang_code else '#0078d7',
                fg='white',
                relief='flat',
                padx=5,
                pady=2,
                cursor='hand2',
                command=lambda lc=lang_code: self.change_language(lc)
            )
            btn.pack(side='left', padx=2)
            self.language_buttons[lang_code] = btn  # Guardar referência

        # Título
        self.title_label = tk.Label(
            header_frame,
            text=_('auth_dialog.title') if I18N_AVAILABLE else "🎣 Ultimate Fishing Bot v5.0",
            font=('Arial', 18, 'bold'),
            fg='#0078d7',
            bg='#2d2d2d'
        )
        self.title_label.pack()

        # Subtítulo
        self.subtitle_label = tk.Label(
            header_frame,
            text=_('auth_dialog.subtitle') if I18N_AVAILABLE else "Sistema de Autenticação Seguro",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2d2d2d'
        )
        self.subtitle_label.pack(pady=(5, 0))

        # ═══════════════════════════════════════════════════════
        # INFORMAÇÕES (Hardware ID)
        # ═══════════════════════════════════════════════════════

        info_frame = tk.Frame(main_frame, bg='#3c3c3c', relief='flat', bd=1)
        info_frame.pack(fill='x', pady=(0, 20))

        info_inner = tk.Frame(info_frame, bg='#3c3c3c', padx=15, pady=10)
        info_inner.pack(fill='both')

        hwid_text = f"🆔 Hardware ID: {self.license_manager.get_hardware_id_display()}"
        hwid_label = tk.Label(
            info_inner,
            text=hwid_text,
            font=('Courier New', 9),
            fg='#00ff88',
            bg='#3c3c3c',
            justify='left'
        )
        hwid_label.pack(anchor='w')

        # ═══════════════════════════════════════════════════════
        # STATUS (criar ANTES das abas para evitar AttributeError)
        # ═══════════════════════════════════════════════════════

        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 10),
            fg='#ffcc00',
            bg='#2d2d2d',
            wraplength=500
        )
        self.status_label.pack(pady=(0, 15))

        # ═══════════════════════════════════════════════════════
        # ABAS (Login, Cadastro, Recuperação)
        # ═══════════════════════════════════════════════════════

        # Estilo customizado para abas
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#2d2d2d', borderwidth=0)
        style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white',
                       padding=[20, 10], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', '#0078d7')])

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 20))

        # Criar abas
        self.login_tab = tk.Frame(self.notebook, bg='#2d2d2d')
        self.register_tab = tk.Frame(self.notebook, bg='#2d2d2d')
        self.recovery_tab = tk.Frame(self.notebook, bg='#2d2d2d')

        # Adicionar abas com textos traduzidos
        self.notebook.add(self.login_tab, text=_('auth_dialog.tab_login') if I18N_AVAILABLE else '🔑 Login')
        self.notebook.add(self.register_tab, text=_('auth_dialog.tab_register') if I18N_AVAILABLE else '📝 Cadastro')
        self.notebook.add(self.recovery_tab, text=_('auth_dialog.tab_recovery') if I18N_AVAILABLE else '🔄 Recuperar Senha')

        # Popular abas
        self.create_login_tab()
        self.create_register_tab()
        self.create_recovery_tab()

        # Selecionar aba inicial
        if self.initial_mode == "register":
            self.notebook.select(self.register_tab)
        else:
            self.notebook.select(self.login_tab)

        # ═══════════════════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════════════════

        self.footer_label = tk.Label(
            main_frame,
            text=_('auth_dialog.footer_encrypted') if I18N_AVAILABLE else "🔒 Suas credenciais são criptografadas localmente",
            font=('Arial', 8),
            fg='#888888',
            bg='#2d2d2d'
        )
        self.footer_label.pack(pady=(0, 0))

    def create_login_tab(self):
        """Criar aba de Login"""
        frame = tk.Frame(self.login_tab, bg='#2d2d2d', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # Email/Username
        self.login_email_label = tk.Label(
            frame,
            text=_('auth_dialog.login_email_label') if I18N_AVAILABLE else "📧 Email ou Username:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        self.login_email_label.pack(anchor='w', pady=(0, 5))

        self.login_username_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.login_username_entry.pack(fill='x', pady=(0, 15))

        # Senha
        self.login_password_label = tk.Label(
            frame,
            text=_('auth_dialog.login_password_label') if I18N_AVAILABLE else "🔒 Senha:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        self.login_password_label.pack(anchor='w', pady=(0, 5))

        self.login_password_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        self.login_password_entry.pack(fill='x', pady=(0, 15))

        # License Key (DESTAQUE)
        license_frame = tk.Frame(frame, bg='#3c3c3c', relief='ridge', bd=2)
        license_frame.pack(fill='x', pady=(5, 15))

        self.login_license_label = tk.Label(
            license_frame,
            text=_('auth_dialog.login_license_label') if I18N_AVAILABLE else "🔑 License Key:",
            font=('Arial', 10, 'bold'),
            fg='#ffd700',
            bg='#3c3c3c'
        )
        self.login_license_label.pack(anchor='w', padx=10, pady=(10, 5))

        self.login_license_entry = tk.Entry(
            license_frame,
            font=('Courier New', 12, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88',
            insertbackground='#00ff88',
            relief='flat',
            bd=0
        )
        self.login_license_entry.pack(fill='x', padx=10, pady=(0, 10))

        # Checkbox: Lembrar credenciais
        self.login_remember_var = tk.BooleanVar(value=True)
        self.login_remember_checkbox = tk.Checkbutton(
            frame,
            text=_('auth_dialog.login_remember') if I18N_AVAILABLE else "✅ Manter conectado",
            variable=self.login_remember_var,
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#cccccc',
            selectcolor='#404040',
            activebackground='#2d2d2d',
            activeforeground='#ffffff'
        )
        self.login_remember_checkbox.pack(anchor='w', pady=(0, 20))

        # Botão Login
        self.login_button = tk.Button(
            frame,
            text=_('auth_dialog.login_button') if I18N_AVAILABLE else "🚀 Entrar",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.handle_login
        )
        self.login_button.pack(fill='x')

        # Carregar credenciais salvas (se existir)
        saved_creds = self.credential_manager.load_credentials()
        if saved_creds:
            self.login_username_entry.insert(0, saved_creds.get('username', ''))
            self.login_password_entry.insert(0, saved_creds.get('password', ''))
            self.login_license_entry.insert(0, saved_creds.get('license_key', ''))
            self.status_label.config(
                text="✅ Credenciais carregadas! Clique em 'Entrar' para continuar.",
                fg='#28a745'
            )

        # Enter = Login
        self.login_password_entry.bind('<Return>', lambda e: self.handle_login())
        self.login_license_entry.bind('<Return>', lambda e: self.handle_login())

    def create_register_tab(self):
        """Criar aba de Cadastro (primeira ativação)"""
        # ✅ CRIAR CANVAS COM SCROLLBAR
        canvas = tk.Canvas(self.register_tab, bg='#2d2d2d', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.register_tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # ✅ Habilitar scroll com roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Frame interno com padding
        frame = tk.Frame(scrollable_frame, bg='#2d2d2d', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # Instruções
        tk.Label(
            frame,
            text=_('auth_dialog.register_title') if I18N_AVAILABLE else "✨ Primeira ativação - Crie sua conta",
            font=('Arial', 11, 'bold'),
            fg='#0078d7',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 15))

        # Username
        tk.Label(
            frame,
            text=_('auth_dialog.register_username_label') if I18N_AVAILABLE else "👤 Username (login):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.register_username_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.register_username_entry.pack(fill='x', pady=(0, 15))

        # Email (opcional)
        tk.Label(
            frame,
            text=_('auth_dialog.register_email_label') if I18N_AVAILABLE else "📧 Email (opcional - para recuperação de senha):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.register_email_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.register_email_entry.pack(fill='x', pady=(0, 15))

        # Senha
        tk.Label(
            frame,
            text=_('auth_dialog.register_password_label') if I18N_AVAILABLE else "🔒 Senha (mínimo 6 caracteres):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.register_password_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        self.register_password_entry.pack(fill='x', pady=(0, 15))

        # Confirmar Senha
        tk.Label(
            frame,
            text=_('auth_dialog.register_confirm_label') if I18N_AVAILABLE else "🔒 Confirmar Senha:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.register_password_confirm_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        self.register_password_confirm_entry.pack(fill='x', pady=(0, 15))

        # License Key (DESTAQUE)
        license_frame = tk.Frame(frame, bg='#3c3c3c', relief='ridge', bd=2)
        license_frame.pack(fill='x', pady=(5, 15))

        tk.Label(
            license_frame,
            text=_('auth_dialog.register_license_label') if I18N_AVAILABLE else "🔑 License Key:",
            font=('Arial', 10, 'bold'),
            fg='#ffd700',
            bg='#3c3c3c'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.register_license_entry = tk.Entry(
            license_frame,
            font=('Courier New', 12, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88',
            insertbackground='#00ff88',
            relief='flat',
            bd=0
        )
        self.register_license_entry.pack(fill='x', padx=10, pady=(0, 10))

        # Botão Cadastrar
        tk.Button(
            frame,
            text=_('auth_dialog.register_button') if I18N_AVAILABLE else "✨ Criar Conta e Ativar",
            font=('Arial', 12, 'bold'),
            bg='#007bff',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.handle_register
        ).pack(fill='x')

        # Enter = Register
        self.register_license_entry.bind('<Return>', lambda e: self.handle_register())

    def create_recovery_tab(self):
        """Criar aba de Recuperação de Senha"""
        # ✅ CRIAR CANVAS COM SCROLLBAR
        canvas = tk.Canvas(self.recovery_tab, bg='#2d2d2d', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.recovery_tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # ✅ Habilitar scroll com roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Frame interno com padding
        frame = tk.Frame(scrollable_frame, bg='#2d2d2d', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # Instruções
        tk.Label(
            frame,
            text=_('auth_dialog.recovery_title') if I18N_AVAILABLE else "🔄 Recuperar Senha",
            font=('Arial', 12, 'bold'),
            fg='#0078d7',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(
            frame,
            text=_('auth_dialog.recovery_description') if I18N_AVAILABLE else "Digite seu email ou license key para receber\no código de recuperação.",
            font=('Arial', 10),
            fg='#aaaaaa',
            bg='#2d2d2d',
            justify='left'
        ).pack(anchor='w', pady=(0, 25))

        # Email ou License Key
        tk.Label(
            frame,
            text=_('auth_dialog.recovery_identifier_label') if I18N_AVAILABLE else "📧 Email ou License Key:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.recovery_identifier_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.recovery_identifier_entry.pack(fill='x', pady=(0, 15))

        # Botão Solicitar Código
        tk.Button(
            frame,
            text=_('auth_dialog.recovery_request_button') if I18N_AVAILABLE else "📤 Solicitar Código de Recuperação",
            font=('Arial', 11, 'bold'),
            bg='#ffc107',
            fg='black',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.handle_request_recovery
        ).pack(fill='x', pady=(0, 30))

        # Separador
        separator_frame = tk.Frame(frame, bg='#2d2d2d', height=2)
        separator_frame.pack(fill='x', pady=(10, 25))

        tk.Frame(separator_frame, bg='#555555', height=1).pack(fill='x')

        # Seção: Já tem o código?
        tk.Label(
            frame,
            text="✉️ Já recebeu o código?" if I18N_AVAILABLE else "✉️ Já recebeu o código?",
            font=('Arial', 11, 'bold'),
            fg='#0078d7',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 20))

        # Código de Recuperação
        tk.Label(
            frame,
            text=_('auth_dialog.recovery_code_label') if I18N_AVAILABLE else "🔢 Código de Recuperação (recebido por email):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.recovery_code_entry = tk.Entry(
            frame,
            font=('Courier New', 12, 'bold'),
            bg='#404040',
            fg='#ffd700',
            insertbackground='#ffd700',
            relief='flat',
            bd=5
        )
        self.recovery_code_entry.pack(fill='x', pady=(0, 20))

        # Nova Senha
        tk.Label(
            frame,
            text=_('auth_dialog.recovery_new_password_label') if I18N_AVAILABLE else "🔒 Nova Senha (mínimo 6 caracteres):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.recovery_new_password_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        self.recovery_new_password_entry.pack(fill='x', pady=(0, 20))

        # Botão Resetar Senha
        tk.Button(
            frame,
            text=_('auth_dialog.recovery_reset_button') if I18N_AVAILABLE else "✅ Resetar Senha",
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.handle_reset_password
        ).pack(fill='x')

    # ═══════════════════════════════════════════════════════
    # LANGUAGE SELECTOR
    # ═══════════════════════════════════════════════════════

    def change_language(self, language_code):
        """Mudar idioma da interface instantaneamente"""
        if not I18N_AVAILABLE:
            self._show_warning(
                "⚠️ Aviso",
                "Sistema de tradução não disponível"
            )
            return

        # ✅ Mudar idioma
        i18n.set_language(language_code)
        self.language_var.set(language_code)

        # ✅ Atualizar cores dos botões de idioma
        for lang_code, btn in self.language_buttons.items():
            if lang_code == language_code:
                btn.config(bg='#0078d7')  # Azul quando selecionado
            else:
                btn.config(bg='#404040')  # Cinza quando não selecionado

        # ✅ Atualizar textos da interface
        try:
            # Título e subtítulo
            self.title_label.config(text=_('auth_dialog.title'))
            self.subtitle_label.config(text=_('auth_dialog.subtitle'))

            # Títulos das abas
            self.notebook.tab(self.login_tab, text=_('auth_dialog.tab_login'))
            self.notebook.tab(self.register_tab, text=_('auth_dialog.tab_register'))
            self.notebook.tab(self.recovery_tab, text=_('auth_dialog.tab_recovery'))

            # Rodapé
            self.footer_label.config(text=_('auth_dialog.footer_encrypted'))

            # ✅ Atualizar TODOS os textos dentro das abas
            # Aba de LOGIN
            self.login_email_label.config(text=_('auth_dialog.login_email_label'))
            self.login_password_label.config(text=_('auth_dialog.login_password_label'))
            self.login_license_label.config(text=_('auth_dialog.login_license_label'))
            self.login_remember_checkbox.config(text=_('auth_dialog.login_remember'))
            self.login_button.config(text=_('auth_dialog.login_button'))

            # ✅ RECRIAR abas de Cadastro e Recuperação (têm muitos elementos)
            # Guardar aba atual selecionada
            current_tab = self.notebook.select()

            # Limpar conteúdo das abas
            for widget in self.register_tab.winfo_children():
                widget.destroy()
            for widget in self.recovery_tab.winfo_children():
                widget.destroy()

            # Recriar abas com novos textos
            self.create_register_tab()
            self.create_recovery_tab()

            # Restaurar aba selecionada
            self.notebook.select(current_tab)

            # Mensagem de sucesso
            self.status_label.config(
                text=f"✅ Idioma alterado para {language_code.upper()} - Interface atualizada!",
                fg='#28a745'
            )

        except Exception as e:
            print(f"[WARN] Erro ao atualizar interface: {e}")
            traceback.print_exc()
            self._show_info(
                "🌐 Idioma Alterado",
                f"Idioma alterado para {language_code.upper()}!\n\nAlguns textos serão atualizados no próximo acesso."
            )

    # ═══════════════════════════════════════════════════════
    # HANDLERS
    # ═══════════════════════════════════════════════════════

    def handle_login(self):
        """Processar login"""
        if self.validating:
            return

        # Validar campos
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()
        license_key = self.login_license_entry.get().strip()
        remember = self.login_remember_var.get()

        if not username or not password or not license_key:
            self._show_warning("⚠️ Atenção", "Preencha todos os campos!")
            return

        self.authenticate(
            username=username,
            password=password,
            license_key=license_key,
            remember=remember,
            mode='login'
        )

    def handle_register(self):
        """Processar cadastro"""
        if self.validating:
            return

        # Validar campos
        username = self.register_username_entry.get().strip()
        email = self.register_email_entry.get().strip()
        password = self.register_password_entry.get().strip()
        password_confirm = self.register_password_confirm_entry.get().strip()
        license_key = self.register_license_entry.get().strip()

        # Validações
        # ✅ Email é OPCIONAL - usuário pode deixar em branco
        if not username or not password or not license_key:
            self._show_warning("⚠️ Atenção", "Preencha Login, Senha e License Key!")
            return

        if len(password) < 6:
            self._show_warning("⚠️ Atenção", "Senha deve ter no mínimo 6 caracteres!")
            return

        if password != password_confirm:
            self._show_error("❌ Erro", "As senhas não coincidem!")
            return

        # Validar email (OPCIONAL - só validar se usuário preencheu)
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self._show_warning("⚠️ Atenção", "Email inválido!")
            return

        # Validar username (alfanumérico + _ -)
        if not re.match(r'^[\w-]{3,20}$', username):
            self._show_warning(
                "⚠️ Atenção",
                "Username deve ter 3-20 caracteres (letras, números, _ ou -)"
            )
            return

        self.authenticate(
            username=username,
            email=email,
            password=password,
            license_key=license_key,
            remember=True,  # Sempre salvar no cadastro
            mode='register'
        )

    def handle_request_recovery(self):
        """Solicitar código de recuperação"""
        identifier = self.recovery_identifier_entry.get().strip()

        if not identifier:
            self._show_warning("⚠️ Atenção", "Digite seu email ou license key!")
            return

        self.status_label.config(
            text="📤 Solicitando código de recuperação...",
            fg='#ffcc00'
        )
        self.root.update()

        # Executar em thread
        def request_thread():
            try:
                import requests
                # ✅ PRODUÇÃO: Servidor de autenticação
                server_url = os.getenv('AUTH_SERVER_URL', 'https://private-serverpesca.pbzgje.easypanel.host')

                response = requests.post(
                    f"{server_url}/auth/request-reset",
                    json={'identifier': identifier},
                    timeout=10
                )

                if response.status_code == 200:
                    self.root.after(0, lambda: self.handle_recovery_success())
                else:
                    error = response.json().get('message', 'Erro desconhecido')
                    self.root.after(0, lambda: self.handle_recovery_error(error))

            except Exception as e:
                self.root.after(0, lambda: self.handle_recovery_error(str(e)))

        threading.Thread(target=request_thread, daemon=True).start()

    def handle_recovery_success(self):
        """Código de recuperação enviado"""
        self.status_label.config(
            text="✅ Código enviado! Verifique seu email.",
            fg='#28a745'
        )
        self._show_info(
            "✅ Sucesso",
            "Código de recuperação enviado para seu email!\n\nVerifique sua caixa de entrada."
        )

    def handle_recovery_error(self, error_msg):
        """Erro ao solicitar recuperação"""
        self.status_label.config(
            text=f"❌ Erro: {error_msg}",
            fg='#dc3545'
        )

    def handle_reset_password(self):
        """Resetar senha com código"""
        code = self.recovery_code_entry.get().strip()
        new_password = self.recovery_new_password_entry.get().strip()

        if not code or not new_password:
            self._show_warning("⚠️ Atenção", "Preencha o código e a nova senha!")
            return

        if len(new_password) < 6:
            self._show_warning("⚠️ Atenção", "Senha deve ter no mínimo 6 caracteres!")
            return

        self.status_label.config(
            text="🔄 Resetando senha...",
            fg='#ffcc00'
        )
        self.root.update()

        # Executar em thread
        def reset_thread():
            try:
                import requests
                # ✅ PRODUÇÃO: Servidor de autenticação
                server_url = os.getenv('AUTH_SERVER_URL', 'https://private-serverpesca.pbzgje.easypanel.host')

                response = requests.post(
                    f"{server_url}/auth/reset-password",
                    json={
                        'code': code,
                        'new_password': new_password
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    self.root.after(0, lambda: self.handle_reset_success())
                else:
                    error = response.json().get('message', 'Erro desconhecido')
                    self.root.after(0, lambda: self.handle_reset_error(error))

            except Exception as e:
                self.root.after(0, lambda: self.handle_reset_error(str(e)))

        threading.Thread(target=reset_thread, daemon=True).start()

    def handle_reset_success(self):
        """Senha resetada com sucesso"""
        self.status_label.config(
            text="✅ Senha resetada! Faça login novamente.",
            fg='#28a745'
        )
        self._show_info(
            "✅ Sucesso",
            "Senha resetada com sucesso!\n\nFaça login na aba 'Login'."
        )
        # Mudar para aba de login
        self.notebook.select(self.login_tab)

    def handle_reset_error(self, error_msg):
        """Erro ao resetar senha"""
        self.status_label.config(
            text=f"❌ Erro: {error_msg}",
            fg='#dc3545'
        )

    def authenticate(self, username, password, license_key, remember, mode, email=None):
        """
        Autenticar no servidor (login ou cadastro)

        Args:
            username: Nome de usuário
            password: Senha
            license_key: Chave de licença
            remember: Salvar credenciais
            mode: 'login' ou 'register'
            email: Email (apenas para cadastro)
        """
        self.validating = True
        self.status_label.config(
            text=f"🔄 {'Criando conta' if mode == 'register' else 'Autenticando'}...",
            fg='#ffcc00'
        )
        self.root.update()

        # Executar em thread
        def auth_thread():
            try:
                import requests

                # 1. Capturar HWID
                hwid = self.license_manager.get_hardware_id()
                pc_name = platform.node()

                # 2. Preparar payload
                # ✅ PRODUÇÃO: Servidor de autenticação
                server_url = os.getenv('AUTH_SERVER_URL', 'https://private-serverpesca.pbzgje.easypanel.host')

                # ✅ CORREÇÃO: Servidor Python usa APENAS /auth/activate para ambos os modos
                # Não existe mais /auth/login nem /auth/register
                endpoint = f"{server_url}/auth/activate"
                payload = {
                    'login': username,  # servidor espera 'login', não 'username'
                    'email': email if mode == 'register' else '',
                    'password': password,
                    'license_key': license_key,
                    'hwid': hwid,
                    'pc_name': pc_name
                }

                # 3. Fazer requisição
                print(f"[AUTH] Enviando para: {endpoint}")
                response = requests.post(endpoint, json=payload, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    # Sucesso!
                    self.root.after(0, lambda: self.handle_auth_success(
                        username=username,
                        password=password,
                        license_key=license_key,
                        remember=remember,
                        token=data.get('token'),
                        user_data=data
                    ))
                else:
                    # Erro
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', f'Erro HTTP {response.status_code}')
                    except:
                        error_msg = f'Erro HTTP {response.status_code}'

                    self.root.after(0, lambda: self.handle_auth_error(error_msg))

            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.handle_auth_error(
                    "Não foi possível conectar ao servidor"
                ))
            except requests.exceptions.Timeout:
                self.root.after(0, lambda: self.handle_auth_error(
                    "Timeout - Servidor demorou para responder"
                ))
            except Exception as e:
                self.root.after(0, lambda: self.handle_auth_error(str(e)))

        threading.Thread(target=auth_thread, daemon=True).start()

    def handle_auth_success(self, username, password, license_key, remember, token, user_data):
        """Autenticação bem-sucedida"""
        self.validating = False

        # Salvar credenciais se solicitado
        if remember:
            self.credential_manager.save_credentials(
                username=username,
                password=password,
                license_key=license_key
            )

        # Salvar license key no LicenseManager
        self.license_manager.save_license(license_key)
        self.license_manager.license_key = license_key

        self.status_label.config(
            text="✅ Autenticação bem-sucedida!",
            fg='#28a745'
        )

        # Retornar resultado
        self.result = {
            'login': username,  # ✅ CORRIGIDO: main.py espera 'login', não 'username'
            'password': password,
            'license_key': license_key,
            'token': token,
            'remember': remember,
            'pc_name': platform.node(),
            'authenticated': True,
            'user_data': user_data
        }

        # Fechar após 1 segundo
        self.root.after(1000, self.root.destroy)

    def handle_auth_error(self, error_msg):
        """Erro na autenticação"""
        self.validating = False
        self.status_label.config(
            text=f"❌ {error_msg}",
            fg='#dc3545'
        )
        self._show_error("❌ Erro de Autenticação", error_msg)

    def cancel(self):
        """Cancelar autenticação"""
        if self._ask_yesno("❌ Cancelar", "Deseja cancelar a autenticação?\n\nO bot não funcionará sem autenticação."):
            self.result = None
            self.root.destroy()


# ═══════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock dos managers
    class MockLicenseManager:
        def get_hardware_id_display(self):
            return "XXXX-XXXX-XXXX-XXXX"

        def get_hardware_id(self):
            return "test_hwid_12345"

        def save_license(self, key):
            print(f"[MOCK] Salvando license: {key}")

        license_key = None

    class MockCredentialManager:
        def load_credentials(self):
            return None  # Sem credenciais salvas

        def save_credentials(self, username, password, license_key):
            print(f"[MOCK] Salvando credenciais: {username}")

    license_manager = MockLicenseManager()
    credential_manager = MockCredentialManager()

    dialog = AuthDialog(license_manager, credential_manager)
    result = dialog.show()

    if result:
        print("\n✅ Autenticação completa:")
        print(f"   Username: {result['username']}")
        print(f"   Senha: {'*' * len(result['password'])}")
        print(f"   License Key: {result['license_key'][:10]}...")
        print(f"   Token: {result.get('token', 'N/A')[:20]}...")
        print(f"   Lembrar: {result['remember']}")
    else:
        print("\n❌ Autenticação cancelada")
