# -*- coding: utf-8 -*-
"""
Script para aplicar registros de widgets automaticamente
Adiciona calls para self.register_translatable_widget() após criação de cada widget
"""

import re
from complete_translation_map import (
    CONTROL_TAB, CONFIG_TAB, FEEDING_TAB, TEMPLATES_TAB,
    ANTI_DETECTION_TAB, VIEWER_TAB, HOTKEYS_TAB, ARDUINO_TAB, HELP_TAB
)

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def apply_control_tab_registrations(content):
    """Aplicar registros para ABA 1: Controle"""

    # 1. Status Frame
    pattern = r"(status_frame = tk\.LabelFrame\(scrollable_frame,\s*text=i18n\.get_text\('ui\.bot_status'\).*?\))\s*\n(\s*status_frame\.pack)"
    replacement = r"\1\n        self.register_translatable_widget('frames', 'status_frame', status_frame, 'ui.bot_status')\n\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 2. Status Label
    pattern = r"(self\.status_label = tk\.Label\(status_frame,\s*text=i18n\.get_text\('ui\.stopped'\).*?\))\s*\n(\s*self\.status_label\.pack)"
    replacement = r"\1\n        self.register_translatable_widget('labels', 'status_label', self.status_label, 'ui.stopped')\n\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 3. Stats Frame
    pattern = r"(stats_frame = tk\.LabelFrame\(scrollable_frame,\s*text=i18n\.get_text\('ui\.detailed_statistics'\).*?\))\s*\n(\s*stats_frame\.pack)"
    replacement = r"\1\n        self.register_translatable_widget('frames', 'stats_frame', stats_frame, 'ui.detailed_statistics')\n\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 4. Auto Clean Frame
    pattern = r"(auto_frame = tk\.LabelFrame\(scrollable_frame, text=i18n\.get_text\(\"ui\.auto_clean\"\).*?\))\s*\n(\s*auto_frame\.pack)"
    replacement = r"\1\n        self.register_translatable_widget('frames', 'auto_frame', auto_frame, 'ui.auto_clean')\n\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content

# Mapeamento de todos os widgets que precisam ser registrados
# Formato: (tipo_widget, id_unico, chave_traducao, pattern_regex)
CONTROL_TAB_WIDGETS = [
    ('frames', 'status_frame', 'ui.bot_status',
     r"(status_frame = tk\.LabelFrame\(.*?text=i18n\.get_text\('ui\.bot_status'\).*?\))"),

    ('labels', 'status_label', 'ui.stopped',
     r"(self\.status_label = tk\.Label\(.*?text=i18n\.get_text\('ui\.stopped'\).*?\))"),

    ('frames', 'stats_frame', 'ui.detailed_statistics',
     r"(stats_frame = tk\.LabelFrame\(.*?text=i18n\.get_text\('ui\.detailed_statistics'\).*?\))"),

    ('frames', 'auto_frame', 'ui.auto_clean',
     r"(auto_frame = tk\.LabelFrame\(.*?text=i18n\.get_text\(\"ui\.auto_clean\"\).*?\))"),
]

def insert_registration_after_widget(content, widget_type, widget_id, translation_key, widget_var_name):
    """
    Inserir registro de widget logo após sua criação

    Procura por padrão:
        widget_var = tk.Widget(...)
        widget_var.pack()

    E insere:
        widget_var = tk.Widget(...)
        self.register_translatable_widget('type', 'id', widget_var, 'key')
        widget_var.pack()
    """

    # Pattern genérico: captura widget creation + próxima linha (pack/grid)
    pattern = rf"({re.escape(widget_var_name)} = .*?text=.*?\))\s*\n(\s*)({re.escape(widget_var_name)}\.(pack|grid))"

    registration_line = f"self.register_translatable_widget('{widget_type}', '{widget_id}', {widget_var_name}, '{translation_key}')"

    replacement = rf"\1\n\2{registration_line}\n\2\3"

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        print(f"  [OK] Registered {widget_type}: {widget_id}")
        return new_content
    else:
        print(f"  [SKIP] Pattern not found for {widget_id}")
        return content

def main():
    print("[INFO] Aplicando registros de widgets...")

    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    print("\n[INFO] ABA 1 - Controle")

    # Aplicar registros para os principais frames e labels
    registrations = [
        ('frames', 'status_frame', 'ui.bot_status', 'status_frame'),
        ('labels', 'status_label', 'ui.stopped', 'self.status_label'),
        ('frames', 'stats_frame', 'ui.detailed_statistics', 'stats_frame'),
        ('frames', 'auto_frame', 'ui.auto_clean', 'auto_frame'),
    ]

    for widget_type, widget_id, translation_key, widget_var in registrations:
        content = insert_registration_after_widget(content, widget_type, widget_id, translation_key, widget_var)

    # Salvar arquivo modificado
    write_file(filepath, content)
    print("\n[OK] Registros aplicados com sucesso!")

if __name__ == '__main__':
    main()
