# -*- coding: utf-8 -*-
"""
🌍 AUTO-REGISTER ALL TRANSLATABLE WIDGETS
Automatically inserts self.register_translatable_widget() calls for all widgets
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Lista COMPLETA de todos os labels a serem registrados (aqueles que já têm i18n.get_text())
LABEL_PATTERNS = [
    # Control Tab (ABA 1)
    ('labels', 'fish_caught_label', 'ui.fish_caught',
     r"(tk\.Label\(fish_frame,\s*text=i18n\.get_text\('ui\.fish_caught'\).*?width=20, anchor='w'\))"),

    ('labels', 'session_time_label', 'ui.session_time',
     r"(tk\.Label\(time_frame,\s*text=i18n\.get_text\('ui\.session_time'\).*?width=20, anchor='w'\))"),

    ('labels', 'fish_per_hour_label', 'ui.fish_per_hour',
     r"(tk\.Label\(rate_frame,\s*text=i18n\.get_text\(\"ui\.fish_per_hour\"\).*?width=20, anchor='w'\))"),

    ('labels', 'success_rate_label', 'ui.success_rate',
     r"(tk\.Label\(success_frame,\s*text=i18n\.get_text\(\"ui\.success_rate\"\).*?width=20, anchor='w'\))"),

    ('labels', 'feedings_label', 'ui.feedings',
     r"(tk\.Label\(feed_frame,\s*text=i18n\.get_text\(\"ui\.feedings\"\).*?width=20, anchor='w'\))"),

    ('labels', 'cleanings_label', 'ui.cleanings',
     r"(tk\.Label\(clean_frame,\s*text=i18n\.get_text\(\"ui\.cleanings\"\).*?width=20, anchor='w'\))"),

    ('labels', 'broken_rods_label', 'ui.broken_rods',
     r"(tk\.Label\(broken_frame,\s*text=i18n\.get_text\(\"ui\.broken_rods\"\).*?width=20, anchor='w'\))"),

    ('labels', 'timeouts_label', 'ui.timeouts',
     r"(tk\.Label\(timeout_frame,\s*text=i18n\.get_text\(\"ui\.timeouts\"\).*?width=20, anchor='w'\))"),

    ('labels', 'last_rod_label', 'ui.last_rod',
     r"(tk\.Label\(rod_timeout_frame,\s*text=i18n\.get_text\(\"ui\.last_rod\"\).*?width=20, anchor='w'\))"),

    ('labels', 'clean_every_label', 'ui.clean_every',
     r"(tk\.Label\(fish_frame,\s*text=i18n\.get_text\(\"ui\.clean_every\"\).*?\))"),

    ('labels', 'catches_label', 'ui.catches',
     r"(tk\.Label\(fish_frame,\s*text=i18n\.get_text\(\"ui\.catches\"\).*?\))"),
]

FRAME_PATTERNS = [
    ('frames', 'auto_frame', 'ui.auto_clean',
     r"(auto_frame = tk\.LabelFrame\(scrollable_frame,\s*text=i18n\.get_text\(\"ui\.auto_clean\"\).*?\))"),
]

def insert_registration_generic(content, widget_type, widget_id, translation_key, pattern):
    """
    Inserir linha de registro logo após a criação do widget

    Busca: widget_creation = tk.Widget(...)
    Adiciona após: self.register_translatable_widget('type', 'id', widget, 'key')
    """
    try:
        # Find the widget creation
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print(f"  [SKIP] Pattern not found for {widget_id}")
            return content

        widget_creation = match.group(1)
        end_pos = match.end(1)

        # Encontrar a próxima linha após a criação do widget
        next_line_match = re.search(r'\n(\s*)', content[end_pos:])
        if not next_line_match:
            print(f"  [SKIP] No next line for {widget_id}")
            return content

        indent = next_line_match.group(1)

        # Criar a variável de widget para o registro
        # Extrair nome da variável do pattern (último termo antes do =)
        if 'tk.Label(' in widget_creation:
            if widget_id.endswith('_label'):
                widget_var = widget_id
            else:
                widget_var = widget_id
        elif 'LabelFrame' in widget_creation:
            # Extrair nome da variável: "auto_frame = tk.LabelFrame..."
            var_match = re.search(r'(\w+)\s*=\s*tk\.LabelFrame', widget_creation)
            widget_var = var_match.group(1) if var_match else widget_id

        # Criar linha de registro
        registration_line = f"\n{indent}self.register_translatable_widget('{widget_type}', '{widget_id}', {widget_var}, '{translation_key}')"

        # Inserir após o widget creation
        new_content = content[:end_pos] + ")" + registration_line + content[end_pos+1:]  # +1 para pular o parêntese final

        if new_content != content:
            print(f"  [OK] Registered {widget_type}: {widget_id}")
            return new_content
        else:
            print(f"  [NO CHANGE] {widget_id}")
            return content

    except Exception as e:
        print(f"  [ERROR] Failed to register {widget_id}: {e}")
        return content

def apply_simple_insertions(content):
    """
    Abordagem simples: inserir registros usando replace direto

    Procura por linhas que já têm i18n.get_text() e adiciona registro logo após
    """

    count = 0

    # AUTO FRAME já foi adicionado manualmente
    # Vamos adicionar os labels de estatísticas

    # 1. fish_caught label
    old = """tk.Label(fish_frame,
                text=i18n.get_text('ui.fish_caught') if I18N_AVAILABLE else "🐟 Peixes capturados:",
                fg=self.theme_colors['text_accent'], bg=self.theme_colors['bg_secondary'],
                font=('Segoe UI', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """fish_caught_lbl = tk.Label(fish_frame,
                text=i18n.get_text('ui.fish_caught') if I18N_AVAILABLE else "🐟 Peixes capturados:",
                fg=self.theme_colors['text_accent'], bg=self.theme_colors['bg_secondary'],
                font=('Segoe UI', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'fish_caught_label', fish_caught_lbl, 'ui.fish_caught')
        fish_caught_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered fish_caught_label")

    # 2. session_time label
    old = """tk.Label(time_frame,
                text=i18n.get_text('ui.session_time') if I18N_AVAILABLE else "⏱️ Tempo de sessão:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """session_time_lbl = tk.Label(time_frame,
                text=i18n.get_text('ui.session_time') if I18N_AVAILABLE else "⏱️ Tempo de sessão:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'session_time_label', session_time_lbl, 'ui.session_time')
        session_time_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered session_time_label")

    # 3. fish_per_hour label
    old = """tk.Label(rate_frame, text=i18n.get_text("ui.fish_per_hour") if I18N_AVAILABLE else "⚡ Peixes/hora:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """fish_per_hour_lbl = tk.Label(rate_frame, text=i18n.get_text("ui.fish_per_hour") if I18N_AVAILABLE else "⚡ Peixes/hora:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'fish_per_hour_label', fish_per_hour_lbl, 'ui.fish_per_hour')
        fish_per_hour_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered fish_per_hour_label")

    # 4. success_rate label
    old = """tk.Label(success_frame, text=i18n.get_text("ui.success_rate") if I18N_AVAILABLE else "🎯 Taxa de sucesso:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """success_rate_lbl = tk.Label(success_frame, text=i18n.get_text("ui.success_rate") if I18N_AVAILABLE else "🎯 Taxa de sucesso:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'success_rate_label', success_rate_lbl, 'ui.success_rate')
        success_rate_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered success_rate_label")

    # 5. feedings label
    old = """tk.Label(feed_frame, text=i18n.get_text("ui.feedings") if I18N_AVAILABLE else "🍖 Alimentações:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """feedings_lbl = tk.Label(feed_frame, text=i18n.get_text("ui.feedings") if I18N_AVAILABLE else "🍖 Alimentações:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'feedings_label', feedings_lbl, 'ui.feedings')
        feedings_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered feedings_label")

    # 6. cleanings label
    old = """tk.Label(clean_frame, text=i18n.get_text("ui.cleanings") if I18N_AVAILABLE else "🧹 Limpezas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """cleanings_lbl = tk.Label(clean_frame, text=i18n.get_text("ui.cleanings") if I18N_AVAILABLE else "🧹 Limpezas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'cleanings_label', cleanings_lbl, 'ui.cleanings')
        cleanings_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered cleanings_label")

    # 7. broken_rods label
    old = """tk.Label(broken_frame, text=i18n.get_text("ui.broken_rods") if I18N_AVAILABLE else "🔧 Varas quebradas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """broken_rods_lbl = tk.Label(broken_frame, text=i18n.get_text("ui.broken_rods") if I18N_AVAILABLE else "🔧 Varas quebradas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'broken_rods_label', broken_rods_lbl, 'ui.broken_rods')
        broken_rods_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered broken_rods_label")

    # 8. timeouts label
    old = """tk.Label(timeout_frame, text=i18n.get_text("ui.timeouts") if I18N_AVAILABLE else "⏱️ Timeouts:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """timeouts_lbl = tk.Label(timeout_frame, text=i18n.get_text("ui.timeouts") if I18N_AVAILABLE else "⏱️ Timeouts:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'timeouts_label', timeouts_lbl, 'ui.timeouts')
        timeouts_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered timeouts_label")

    # 9. last_rod label
    old = """tk.Label(rod_timeout_frame, text=i18n.get_text("ui.last_rod") if I18N_AVAILABLE else "🎣 Vara (último timeout):",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')"""

    new = """last_rod_lbl = tk.Label(rod_timeout_frame, text=i18n.get_text("ui.last_rod") if I18N_AVAILABLE else "🎣 Vara (último timeout):",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'last_rod_label', last_rod_lbl, 'ui.last_rod')
        last_rod_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered last_rod_label")

    # 10. auto_frame (já foi adicionado manualmente, mas vamos garantir)
    old = """auto_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.auto_clean") if I18N_AVAILABLE else "🔄 Limpeza Automática",
                                 fg='white', bg='#1a1a1a',
                                 font=('Arial', 12, 'bold'))
        auto_frame.pack(fill='x', pady=10, padx=10)"""

    new = """auto_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.auto_clean") if I18N_AVAILABLE else "🔄 Limpeza Automática",
                                 fg='white', bg='#1a1a1a',
                                 font=('Arial', 12, 'bold'))
        self.register_translatable_widget('frames', 'auto_frame', auto_frame, 'ui.auto_clean')
        auto_frame.pack(fill='x', pady=10, padx=10)"""

    if old in content and 'self.register_translatable_widget' not in content[content.find(old):content.find(old)+500]:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered auto_frame")

    # 11. clean_every label
    old = """tk.Label(fish_frame, text=i18n.get_text("ui.clean_every") if I18N_AVAILABLE else "🐟 Limpar inventário a cada:",
                fg='white', bg='#1a1a1a', font=('Arial', 10)).pack(side='left')"""

    new = """clean_every_lbl = tk.Label(fish_frame, text=i18n.get_text("ui.clean_every") if I18N_AVAILABLE else "🐟 Limpar inventário a cada:",
                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.register_translatable_widget('labels', 'clean_every_label', clean_every_lbl, 'ui.clean_every')
        clean_every_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered clean_every_label")

    # 12. catches label
    old = """tk.Label(fish_frame, text=i18n.get_text("ui.catches") if I18N_AVAILABLE else "pescas",
                fg='white', bg='#1a1a1a', font=('Arial', 10)).pack(side='left')"""

    new = """catches_lbl = tk.Label(fish_frame, text=i18n.get_text("ui.catches") if I18N_AVAILABLE else "pescas",
                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.register_translatable_widget('labels', 'catches_label', catches_lbl, 'ui.catches')
        catches_lbl.pack(side='left')"""

    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  [OK] Registered catches_label")

    print(f"\n[SUMMARY] Applied {count} registrations")
    return content

def main():
    print("[INFO] Auto-registering ALL translatable widgets...")
    print("[INFO] This will modify ui/main_window.py\n")

    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    print("[INFO] Applying simple insertions for Control Tab labels...")
    content = apply_simple_insertions(content)

    # Salvar arquivo modificado
    write_file(filepath, content)
    print("\n[OK] Widget registrations completed!")
    print("[INFO] Run the bot to test: python main.py")

if __name__ == '__main__':
    main()
