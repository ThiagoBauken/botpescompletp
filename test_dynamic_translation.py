# -*- coding: utf-8 -*-
"""
Teste do sistema de tradução dinâmica aprimorado
"""
import tkinter as tk
from tkinter import ttk
import sys
sys.path.insert(0, '.')

from utils.i18n import i18n, _

def _safe_print(text):
    """Print seguro para Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

class TestTranslationWindow:
    """Janela de teste para tradução dinâmica"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Teste de Traducao Dinamica")
        self.root.geometry("600x400")

        self.current_language = 'pt'
        self.translatable_widgets = {'labels': {}, 'buttons': {}}

        self.create_ui()

    def create_ui(self):
        """Criar interface de teste"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title = tk.Label(main_frame, text=_("ui.app_title"), font=('Arial', 14, 'bold'))
        title._translation_key = "ui.app_title"  # Estratégia 1: Com atributo
        title.pack(pady=10)

        # Frame de controle (labels sem _translation_key para testar Estratégia 2)
        control_frame = ttk.LabelFrame(main_frame, text=_("tabs.control_tab"))
        control_frame.pack(fill=tk.X, pady=10, padx=10)

        # Label sem _translation_key (deve ser detectado automaticamente)
        status_label = tk.Label(control_frame, text=_("ui.bot_status"), font=('Arial', 10))
        status_label.pack(pady=5)

        # Botões sem _translation_key
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)

        start_btn = tk.Button(btn_frame, text=_("ui.start_button"), bg='#4CAF50', fg='white', width=12)
        start_btn.pack(side=tk.LEFT, padx=5)

        stop_btn = tk.Button(btn_frame, text=_("ui.stop_button"), bg='#f44336', fg='white', width=12)
        stop_btn.pack(side=tk.LEFT, padx=5)

        # Frame de seleção de idioma
        lang_frame = ttk.LabelFrame(main_frame, text="Trocar Idioma")
        lang_frame.pack(fill=tk.X, pady=10, padx=10)

        lang_info = tk.Label(lang_frame,
                            text="Selecione um idioma e clique em 'Aplicar'\nO sistema deve atualizar TODOS os textos automaticamente",
                            justify=tk.LEFT)
        lang_info.pack(pady=5)

        # Combobox de idiomas
        lang_selector_frame = ttk.Frame(lang_frame)
        lang_selector_frame.pack(pady=5)

        tk.Label(lang_selector_frame, text="Idioma:").pack(side=tk.LEFT, padx=5)

        self.lang_var = tk.StringVar(value="Português")
        self.lang_combo = ttk.Combobox(lang_selector_frame,
                                       textvariable=self.lang_var,
                                       values=["Português", "English", "Español", "Русский"],
                                       state="readonly",
                                       width=15)
        self.lang_combo.pack(side=tk.LEFT, padx=5)

        apply_btn = tk.Button(lang_selector_frame,
                            text="Aplicar Traducao",
                            command=self.apply_language_change,
                            bg='#2196F3',
                            fg='white')
        apply_btn.pack(side=tk.LEFT, padx=5)

        # Status da última atualização
        self.update_status = tk.Label(main_frame, text="", fg='green', font=('Arial', 9))
        self.update_status.pack(pady=10)

    def apply_language_change(self):
        """Aplicar mudança de idioma"""
        # Mapear nome amigável para código
        lang_map = {
            "Português": "pt",
            "English": "en",
            "Español": "es",
            "Русский": "ru"
        }

        selected_lang = self.lang_var.get()
        lang_code = lang_map.get(selected_lang, 'pt')

        if lang_code == self.current_language:
            self.update_status.config(text="Idioma ja selecionado!", fg='orange')
            return

        _safe_print(f"\n[TEST] Mudando idioma de {self.current_language} para {lang_code}")
        old_lang = self.current_language
        self.current_language = lang_code

        # Atualizar idioma no i18n
        i18n.set_language(lang_code)

        # Chamar sistema de atualização
        updated = self.update_ui_texts()

        self.update_status.config(
            text=f"Idioma mudado de {old_lang} para {lang_code}! {updated} elementos atualizados.",
            fg='green'
        )

        _safe_print(f"[TEST] Atualizados {updated} elementos")

    def update_ui_texts(self):
        """Sistema de atualização de textos (versão simplificada do main_window.py)"""
        updated_count = 0

        def update_widgets_recursive(parent, depth=0):
            """Varre recursivamente todos os widgets"""
            count = 0

            try:
                for child in parent.winfo_children():
                    widget_updated = False
                    widget_type = type(child).__name__

                    # Estratégia 1: Widget tem _translation_key
                    if hasattr(child, '_translation_key'):
                        try:
                            new_text = i18n.get_text(child._translation_key)
                            if new_text and new_text != child._translation_key:
                                child.config(text=new_text)
                                count += 1
                                widget_updated = True
                                _safe_print(f"  [OK] Atualizado (Estrategia 1): {child._translation_key}")
                        except Exception as e:
                            _safe_print(f"  [WARN] Erro na Estrategia 1: {e}")

                    # Estratégia 2: Detectar automaticamente
                    if not widget_updated and widget_type in ['Label', 'Button', 'Checkbutton', 'LabelFrame']:
                        try:
                            current_text = child.cget('text')

                            if current_text and len(current_text) > 0:
                                translation_key = self._find_translation_key_by_text(current_text)

                                if translation_key:
                                    new_text = i18n.get_text(translation_key)
                                    if new_text and new_text != current_text and new_text != translation_key:
                                        child.config(text=new_text)
                                        child._translation_key = translation_key
                                        count += 1
                                        widget_updated = True
                                        _safe_print(f"  [OK] Atualizado (Estrategia 2): '{current_text}' -> '{new_text}'")
                        except Exception as e:
                            _safe_print(f"  [WARN] Erro na Estrategia 2: {e}")

                    # Recursão
                    count += update_widgets_recursive(child, depth + 1)

            except Exception as e:
                if depth == 0:
                    _safe_print(f"[ERROR] Erro na recursao: {e}")

            return count

        updated_count = update_widgets_recursive(self.root)
        return updated_count

    def _find_translation_key_by_text(self, text):
        """Encontrar chave de tradução pelo texto"""
        try:
            if not text:
                return None

            available_languages = i18n.translations.keys()

            for lang in available_languages:
                if lang in i18n.translations:
                    def search_in_dict(d, target_text, prefix=''):
                        for key, value in d.items():
                            current_key = f"{prefix}.{key}" if prefix else key

                            if isinstance(value, dict):
                                result = search_in_dict(value, target_text, current_key)
                                if result:
                                    return result
                            elif isinstance(value, str) and value == target_text:
                                return current_key

                        return None

                    result = search_in_dict(i18n.translations[lang], text)
                    if result:
                        return result

            return None

        except Exception:
            return None

    def run(self):
        """Executar aplicação de teste"""
        _safe_print("=" * 60)
        _safe_print("TESTE DE TRADUCAO DINAMICA")
        _safe_print("=" * 60)
        _safe_print("Instrucoes:")
        _safe_print("1. Observe os textos atuais (em Portugues)")
        _safe_print("2. Selecione outro idioma no combobox")
        _safe_print("3. Clique em 'Aplicar Traducao'")
        _safe_print("4. Os textos devem atualizar AUTOMATICAMENTE sem reiniciar!")
        _safe_print("=" * 60)
        _safe_print("")

        self.root.mainloop()

if __name__ == '__main__':
    app = TestTranslationWindow()
    app.run()
