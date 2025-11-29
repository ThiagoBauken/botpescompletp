#!/usr/bin/env python3
"""
🔐 Ultimate Fishing Bot v4.0 - Dialog de Autenticação Unificado
Coleta Login + Senha + License Key em uma única janela
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform
import os
import sys
import requests
import random
import string

# Importar sistema i18n
try:
    from utils.i18n import i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("[WARN] i18n not available in unified_auth_dialog")

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


class UnifiedAuthDialog:
    """
    Dialog unificado de autenticação

    Coleta em uma única janela:
    - Login (email ou username)
    - Senha (opcional)
    - License Key (do Keymaster)
    - Checkbox: Manter conectado

    Processo:
    1. Valida license key com Keymaster
    2. Se válida, conecta ao servidor com todas as credenciais
    """

    @staticmethod
    def _generate_random_title():
        """Gera um título aleatório com 8-12 caracteres"""
        length = random.randint(8, 12)
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def __init__(self, license_manager):
        self.license_manager = license_manager
        self.result = None
        self.root = None
        self.validating = False

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

    def show(self):
        """Mostrar diálogo e retornar resultado"""
        self.root = tk.Tk()

        # ✅ Gerar título aleatório (igual à main_window)
        random_title = self._generate_random_title()
        self.root.title(random_title)

        self.root.geometry("520x550")
        self.root.configure(bg='#2d2d2d')
        self.root.resizable(False, False)

        # ✅ Configurar ícone personalizado da janela
        try:
            icon_path = resource_path("magoicon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"[OK] Ícone personalizado carregado na janela de autenticação: {icon_path}")
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
        header_frame.pack(fill='x', pady=(0, 20))

        # Título
        title_label = tk.Label(
            header_frame,
            text="🎣 Fishing Bot v4.0",
            font=('Arial', 18, 'bold'),
            fg='#0078d7',
            bg='#2d2d2d'
        )
        title_label.pack()

        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Ative sua licença para começar",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2d2d2d'
        )
        subtitle_label.pack(pady=(5, 0))

        # ═══════════════════════════════════════════════════════
        # INFORMAÇÕES
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
        # FORMULÁRIO
        # ═══════════════════════════════════════════════════════

        form_frame = tk.Frame(main_frame, bg='#2d2d2d')
        form_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Campo: Login
        tk.Label(
            form_frame,
            text="Login:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.login_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.login_entry.pack(fill='x', pady=(0, 15))

        # Campo: Senha (opcional)
        tk.Label(
            form_frame,
            text="Senha (opcional):",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        self.password_entry.pack(fill='x', pady=(0, 5))

        # Botão: Esqueci Minha Senha
        forgot_password_btn = tk.Button(
            form_frame,
            text="🔑 Esqueci Minha Senha",
            font=('Arial', 9),
            bg='#404040',
            fg='#00aaff',
            relief='flat',
            cursor='hand2',
            command=self.reset_password,
            borderwidth=0
        )
        forgot_password_btn.pack(anchor='e', pady=(0, 15))

        # Campo: License Key
        tk.Label(
            form_frame,
            text="License Key:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w', pady=(0, 5))

        self.license_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.license_entry.pack(fill='x', pady=(0, 15))

        # Checkbox: Manter conectado
        self.remember_var = tk.BooleanVar(value=True)
        self.remember_check = tk.Checkbutton(
            form_frame,
            text="Manter conectado (salvar credenciais)",
            variable=self.remember_var,
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#cccccc',
            selectcolor='#404040',
            activebackground='#2d2d2d',
            activeforeground='#ffffff'
        )
        self.remember_check.pack(anchor='w', pady=(0, 5))

        # ═══════════════════════════════════════════════════════
        # STATUS
        # ═══════════════════════════════════════════════════════

        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 10),
            fg='#ffcc00',
            bg='#2d2d2d',
            wraplength=450
        )
        self.status_label.pack(pady=(0, 15))

        # ═══════════════════════════════════════════════════════
        # BOTÕES
        # ═══════════════════════════════════════════════════════

        button_frame = tk.Frame(main_frame, bg='#2d2d2d')
        button_frame.pack(fill='x')

        # Botão Ativar
        self.activate_btn = tk.Button(
            button_frame,
            text="🚀 Ativar",
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.activate
        )
        self.activate_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))

        # Botão Cancelar
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancelar",
            font=('Arial', 11),
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.cancel
        )
        cancel_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # ═══════════════════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════════════════

        footer_text = "💡 Dica: Entre em contato para obter sua licença"
        footer_label = tk.Label(
            main_frame,
            text=footer_text,
            font=('Arial', 8),
            fg='#888888',
            bg='#2d2d2d'
        )
        footer_label.pack(pady=(15, 0))

        # Focus no login
        self.login_entry.focus()

        # Enter = Ativar
        self.root.bind('<Return>', lambda e: self.activate())

    def activate(self):
        """Ativar licença e autenticar"""

        # Prevenir duplo clique
        if self.validating:
            return

        # Validar campos
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip() or "default"
        license_key = self.license_entry.get().strip()
        remember = self.remember_var.get()

        if not login:
            self._show_warning("⚠️ Atenção", "Digite seu login!")
            self.login_entry.focus()
            return

        if not license_key:
            self._show_warning("⚠️ Atenção", "Cole sua license key!")
            self.license_entry.focus()
            return

        # Desabilitar botão e mostrar status
        self.validating = True
        self.activate_btn.config(state='disabled')
        self.status_label.config(text="🔄 Validando license key com Keymaster...", fg='#ffcc00')
        self.root.update()

        # Executar validação em thread separada
        def validate_thread():
            try:
                # ✅ DECISÃO INTELIGENTE: Ativar ou Validar?
                saved_key = self.license_manager.load_license()

                if saved_key == license_key:
                    # CASO 1: MESMA KEY → Apenas VALIDAR
                    self.root.after(0, lambda: self.status_label.config(
                        text="🔄 Validando license key existente...",
                        fg='#ffcc00'
                    ))

                    success, result = self.license_manager.validate_license(license_key)
                    message = result.get('message', 'Erro desconhecido') if isinstance(result, dict) else result

                else:
                    # CASO 2: KEY DIFERENTE ou NOVA → ATIVAR
                    self.root.after(0, lambda: self.status_label.config(
                        text="🔄 Ativando nova license key...",
                        fg='#ffcc00'
                    ))

                    success, result = self.license_manager.activate_license(license_key)
                    message = result if isinstance(result, str) else result.get('message', 'Erro desconhecido')

                if success:
                    # FASE 2: Preparar credenciais para servidor
                    self.root.after(0, lambda: self.handle_success(
                        login=login,
                        password=password,
                        license_key=license_key,
                        remember=remember
                    ))
                else:
                    # Falha na validação/ativação
                    self.root.after(0, lambda: self.handle_error(message))

            except Exception as e:
                self.root.after(0, lambda: self.handle_error(str(e)))

        threading.Thread(target=validate_thread, daemon=True).start()

    def handle_success(self, login, password, license_key, remember):
        """Tratar sucesso na validação"""
        self.status_label.config(
            text="✅ License key válida! Preparando conexão...",
            fg='#28a745'
        )
        self.root.update()

        # Retornar todas as credenciais
        self.result = {
            'login': login,
            'password': password,
            'license_key': license_key,
            'remember': remember,
            'pc_name': platform.node(),
            'validated': True
        }

        # Fechar diálogo após 1 segundo
        self.root.after(1000, self.root.destroy)

    def handle_error(self, error_message):
        """Tratar erro na validação"""
        self.validating = False
        self.activate_btn.config(state='normal')
        self.status_label.config(
            text=f"❌ Erro: {error_message}",
            fg='#dc3545'
        )

    def _ask_password(self, title, prompt):
        """Dialog customizado para pedir senha (com ícone correto)"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
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
        frame = tk.Frame(dialog, bg='#2d2d2d', padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # Prompt
        tk.Label(
            frame,
            text=prompt,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#2d2d2d',
            wraplength=350
        ).pack(pady=(0, 15))

        # Entry
        entry = tk.Entry(
            frame,
            font=('Arial', 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5,
            show='●'
        )
        entry.pack(fill='x', pady=(0, 20))
        entry.focus()

        # Botões
        btn_frame = tk.Frame(frame, bg='#2d2d2d')
        btn_frame.pack(fill='x')

        def on_ok():
            result['value'] = entry.get()
            dialog.destroy()

        def on_cancel():
            result['value'] = None
            dialog.destroy()

        tk.Button(
            btn_frame,
            text="✅ OK",
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=on_ok
        ).pack(side='left', fill='x', expand=True, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=on_cancel
        ).pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Enter = OK
        entry.bind('<Return>', lambda e: on_ok())

        dialog.wait_window()
        return result['value']

    def reset_password(self):
        """Resetar senha do usuário"""
        # Validar license key
        license_key = self.license_entry.get().strip()

        if not license_key:
            self._show_warning(
                "⚠️ Atenção",
                "Digite sua License Key primeiro para resetar a senha!"
            )
            self.license_entry.focus()
            return

        # Pedir nova senha (DIALOG CUSTOMIZADO)
        new_password = self._ask_password(
            "🔑 Reset de Senha",
            "Digite sua NOVA senha (mínimo 6 caracteres):"
        )

        if not new_password:
            return  # Usuário cancelou

        if len(new_password) < 6:
            self._show_error(
                "❌ Erro",
                "A senha deve ter no mínimo 6 caracteres!"
            )
            return

        # Confirmar senha (DIALOG CUSTOMIZADO)
        confirm_password = self._ask_password(
            "🔑 Confirmar Senha",
            "Digite a senha novamente para confirmar:"
        )

        if new_password != confirm_password:
            self._show_error(
                "❌ Erro",
                "As senhas não coincidem! Tente novamente."
            )
            return

        # Mostrar status
        self.status_label.config(text="🔄 Resetando senha...", fg='#ffcc00')
        self.root.update()

        # Executar reset em thread separada
        def reset_thread():
            try:
                # Obter HWID
                hwid = self.license_manager.get_hardware_id()

                # URL do servidor
                server_url = "https://private-serverpesca.pbzgje.easypanel.host"

                # Chamar endpoint de reset
                response = requests.post(
                    f"{server_url}/auth/reset-password",
                    json={
                        "license_key": license_key,
                        "hwid": hwid,
                        "new_password": new_password
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    self.root.after(0, lambda: self.handle_reset_success(new_password, data))
                else:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Erro desconhecido")
                    self.root.after(0, lambda: self.handle_reset_error(error_msg))

            except requests.exceptions.Timeout:
                self.root.after(0, lambda: self.handle_reset_error(
                    "Tempo esgotado! Verifique sua conexão com a internet."
                ))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.handle_reset_error(
                    "Erro de conexão! Verifique sua internet e tente novamente."
                ))
            except Exception as e:
                self.root.after(0, lambda: self.handle_reset_error(str(e)))

        threading.Thread(target=reset_thread, daemon=True).start()

    def handle_reset_success(self, new_password, data):
        """Tratar sucesso no reset de senha"""
        message = data.get("message", "Senha resetada com sucesso!")
        login = data.get("login", "")

        messagebox.showinfo(
            "✅ Sucesso",
            f"{message}\n\nVocê pode fazer login agora com a nova senha!"
        )

        # Atualizar campo de senha com a nova
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, new_password)

        # Atualizar login se retornou
        if login:
            self.login_entry.delete(0, tk.END)
            self.login_entry.insert(0, login)

        # Limpar status
        self.status_label.config(text="✅ Senha atualizada! Você pode fazer login agora.", fg='#28a745')

    def handle_reset_error(self, error_message):
        """Tratar erro no reset de senha"""
        messagebox.showerror(
            "❌ Erro no Reset",
            f"Não foi possível resetar a senha:\n\n{error_message}"
        )
        self.status_label.config(text=f"❌ Erro: {error_message}", fg='#dc3545')

    def cancel(self):
        """Cancelar autenticação"""
        self.result = None
        self.root.destroy()


# ═══════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock do LicenseManager para teste
    class MockLicenseManager:
        def get_hardware_id_display(self):
            return "XXXX-XXXX-XXXX-XXXX"

        def activate_license(self, license_key):
            # Simular validação
            import time
            time.sleep(2)

            if license_key.startswith("TEST"):
                return True, "Licença válida"
            else:
                return False, "License key inválida"

    license_manager = MockLicenseManager()
    dialog = UnifiedAuthDialog(license_manager)
    result = dialog.show()

    if result:
        print("✅ Autenticação completa:")
        print(f"   Login: {result['login']}")
        print(f"   Senha: {'*' * len(result['password'])}")
        print(f"   License Key: {result['license_key'][:10]}...")
        print(f"   Manter conectado: {result['remember']}")
        print(f"   PC: {result['pc_name']}")
        print(f"   Validada: {result['validated']}")
    else:
        print("❌ Autenticação cancelada")
