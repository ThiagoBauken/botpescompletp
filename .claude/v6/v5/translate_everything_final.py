# -*- coding: utf-8 -*-
"""
SCRIPT FINAL: Adicionar i18n.get_text() e registro para TODOS os widgets hardcoded
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def add_all_hardcoded_translations(content):
    """Adicionar i18n.get_text() para TODOS os texts hardcoded e registrar"""

    count = 0

    # Lista COMPLETA de substituições para ABA 1 (Controle)
    replacements = [
        # Botão Iniciar
        {
            'old': 'self.start_button = tk.Button(button_frame, text="🚀 Iniciar"',
            'new': 'self.start_button = tk.Button(button_frame, text=i18n.get_text("ui.start_bot") if I18N_AVAILABLE else "🚀 Iniciar"',
            'register_after': 'self.start_button.pack',
            'register_line': '        self.register_translatable_widget(\'buttons\', \'start_btn\', self.start_button, \'ui.start_bot\')\n',
            'name': 'start_button'
        },
        # Botão Pausar
        {
            'old': 'self.pause_button = tk.Button(button_frame, text="⏸️ Pausar"',
            'new': 'self.pause_button = tk.Button(button_frame, text=i18n.get_text("ui.pause_bot") if I18N_AVAILABLE else "⏸️ Pausar"',
            'register_after': 'self.pause_button.pack',
            'register_line': '        self.register_translatable_widget(\'buttons\', \'pause_btn\', self.pause_button, \'ui.pause_bot\')\n',
            'name': 'pause_button'
        },
        # Botão Parar
        {
            'old': 'self.stop_button = tk.Button(button_frame, text="🛑 Parar"',
            'new': 'self.stop_button = tk.Button(button_frame, text=i18n.get_text("ui.stop_bot") if I18N_AVAILABLE else "🛑 Parar"',
            'register_after': 'self.stop_button.pack',
            'register_line': '        self.register_translatable_widget(\'buttons\', \'stop_btn\', self.stop_button, \'ui.stop_bot\')\n',
            'name': 'stop_button'
        },
    ]

    for repl in replacements:
        if repl['old'] in content:
            # Step 1: Replace text with i18n
            content = content.replace(repl['old'], repl['new'])
            count += 1
            print(f"  [OK] Added i18n to {repl['name']}")

            # Step 2: Add register call after .pack()
            if repl['register_after'] in content and repl['register_line'] not in content:
                # Find the pack line
                pattern = f"({re.escape(repl['register_after'])}.*?\\))"
                match = re.search(pattern, content)
                if match:
                    insert_pos = match.end()
                    content = content[:insert_pos] + '\n' + repl['register_line'] + content[insert_pos:]
                    print(f"  [OK] Registered {repl['name']}")

    return content, count

def main():
    print("[INFO] ===== TRADUCAO COMPLETA DE TODOS OS WIDGETS =====\n")

    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    print("[STEP 1] Adicionando i18n.get_text() e registros...")
    content, count = add_all_hardcoded_translations(content)

    # Salvar
    write_file(filepath, content)

    print(f"\n[OK] Total processado: {count} widgets")
    print(f"[OK] Arquivo salvo: {filepath}")
    print("\n[INFO] Execute: python main.py para testar!")

if __name__ == '__main__':
    main()
