#!/usr/bin/env python3
"""
🔐 Ultimate Fishing Bot v4.0 - License Dialog
Interface para ativação e gerenciamento de licenças
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

class LicenseDialog:
    """Diálogo para ativação de licença"""
    
    def __init__(self, license_manager):
        self.license_manager = license_manager
        self.result = None
        self.root = None
        
    def show(self) -> str:
        """Mostrar diálogo e retornar chave inserida"""
        self.root = tk.Tk()
        self.root.title("🔐 Ultimate Fishing Bot v4.0 - Licença")
        self.root.geometry("500x400")
        self.root.configure(bg='#2d2d2d')
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.root.transient()
        self.root.grab_set()
        
        self.create_widgets()
        
        # Aguardar resultado
        self.root.mainloop()
        
        return self.result
    
    def create_widgets(self):
        """Criar widgets do diálogo"""
        main_frame = tk.Frame(self.root, bg='#2d2d2d', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🔐 Ativação de Licença",
            font=('Arial', 16, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        title_label.pack(pady=(0, 20))
        
        # Informações
        info_text = f"""Ultimate Fishing Bot v4.0 requer uma licença válida para operar.

Hardware ID: {self.license_manager.get_hardware_id_display()}

Por favor, insira sua chave de licença abaixo:"""
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2d2d2d',
            justify='left',
            wraplength=450
        )
        info_label.pack(pady=(0, 20))
        
        # Frame para entrada de chave
        key_frame = tk.Frame(main_frame, bg='#2d2d2d')
        key_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            key_frame,
            text="Chave de Licença:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(anchor='w')
        
        self.key_entry = tk.Entry(
            key_frame,
            font=('Arial', 12),
            width=50,
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.key_entry.pack(fill='x', pady=(5, 0))
        self.key_entry.focus()
        
        # Bind Enter key
        self.key_entry.bind('<Return>', lambda e: self.activate_license())
        
        # Frame para botões
        button_frame = tk.Frame(main_frame, bg='#2d2d2d')
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Botão Ativar
        self.activate_btn = tk.Button(
            button_frame,
            text="🔓 Ativar Licença",
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=self.activate_license
        )
        self.activate_btn.pack(side='left', padx=(0, 10))
        
        # Botão Cancelar
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancelar",
            font=('Arial', 11),
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=self.cancel
        )
        cancel_btn.pack(side='left')
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 10),
            fg='#ffcc00',
            bg='#2d2d2d'
        )
        self.status_label.pack(pady=(20, 0))
        
        # Informações adicionais
        footer_text = """💡 Dicas:
• Entre em contato para obter sua licença
• A licença é vinculada ao seu hardware
• Mantenha sua chave segura"""
        
        footer_label = tk.Label(
            main_frame,
            text=footer_text,
            font=('Arial', 8),
            fg='#888888',
            bg='#2d2d2d',
            justify='left'
        )
        footer_label.pack(pady=(20, 0))
    
    def activate_license(self):
        """Ativar licença inserida"""
        license_key = self.key_entry.get().strip()
        
        if not license_key:
            messagebox.showerror("Erro", "Por favor, insira uma chave de licença.")
            return
        
        # Desabilitar botão e mostrar status
        self.activate_btn.config(state='disabled')
        self.status_label.config(text="🔄 Ativando licença...")
        self.root.update()
        
        # Executar ativação em thread separada (seguindo lógica do v3)
        def activate_thread():
            try:
                # Tentar ativar (lógica do v3 - linha 6353)
                success, message = self.license_manager.activate_license(license_key)

                # Atualizar UI na thread principal
                self.root.after(0, lambda: self.handle_activation_result(success, message, license_key))

            except Exception as e:
                self.root.after(0, lambda: self.handle_validation_error(str(e)))

        threading.Thread(target=activate_thread, daemon=True).start()
    
    def handle_activation_result(self, success, message, license_key):
        """Tratar resultado da ativação (lógica do v3 - linha 6355)"""
        self.activate_btn.config(state='normal')

        if success:
            self.status_label.config(text="✅ Licença ativada com sucesso!", fg='#28a745')
            self.result = license_key
            # Fechar diálogo após 1.5 segundos (igual v3 - linha 6358)
            self.root.after(1500, self.root.destroy)
        else:
            # Mostrar mensagem de erro (igual v3 - linha 6360)
            self.status_label.config(text=f"❌ {message}", fg='#dc3545')
    
    def handle_validation_error(self, error_msg):
        """Tratar erro na validação"""
        self.activate_btn.config(state='normal')
        self.status_label.config(text=f"❌ Erro: {error_msg}", fg='#dc3545')
    
    def cancel(self):
        """Cancelar ativação"""
        self.result = None
        self.root.destroy()

class LicenseInfoDialog:
    """Diálogo para mostrar informações da licença"""
    
    def __init__(self, license_manager):
        self.license_manager = license_manager
        
    def show(self):
        """Mostrar informações da licença"""
        root = tk.Tk()
        root.title("🔐 Informações da Licença")
        root.geometry("400x300")
        root.configure(bg='#2d2d2d')
        root.resizable(False, False)
        
        main_frame = tk.Frame(root, bg='#2d2d2d', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🔐 Licença Ativa",
            font=('Arial', 16, 'bold'),
            fg='#28a745',
            bg='#2d2d2d'
        )
        title_label.pack(pady=(0, 20))
        
        # Informações da licença
        if self.license_manager.is_licensed():
            info = self.license_manager.get_license_info()
            
            info_text = f"""✅ Status: Licenciado
🆔 Hardware ID: {self.license_manager.get_hardware_id_display()}
📅 Expira em: {info.get('expires_at', 'N/A')}
📊 Status: {info.get('status', 'N/A')}
🎯 Plano: {info.get('plan_name', 'N/A')}
⏰ Tempo restante: {info.get('time_remaining', 'N/A')} segundos"""
        else:
            info_text = "❌ Sistema não licenciado"
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2d2d2d',
            justify='left'
        )
        info_label.pack(pady=(0, 20))
        
        # Botão fechar
        close_btn = tk.Button(
            main_frame,
            text="✅ OK",
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=root.destroy
        )
        close_btn.pack()
        
        root.mainloop()