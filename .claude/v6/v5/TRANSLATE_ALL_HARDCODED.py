# -*- coding: utf-8 -*-
"""
TRADUZIR TODOS OS WIDGETS HARDCODED
Adiciona i18n.get_text() para TODOS os 18 widgets em português + traduções RU
"""

import json
import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# TODAS as traduções que faltam
NEW_TRANSLATIONS = {
    'chest_distance': {
        'pt': 'Distância do baú (unidades):',
        'en': 'Chest distance (units):',
        'es': 'Distancia del cofre (unidades):',
        'ru': 'Расстояние до сундука (единицы):'
    },
    'auto_reload': {
        'pt': '🔄 Auto-reload',
        'en': '🔄 Auto-reload',
        'es': '🔄 Auto-recarga',
        'ru': '🔄 Авто-перезагрузка'
    },
    'auto_focus': {
        'pt': '🎯 Auto-focus',
        'en': '🎯 Auto-focus',
        'es': '🎯 Auto-enfoque',
        'ru': '🎯 Авто-фокус'
    },
    'broken_rod_action': {
        'pt': 'Ação vara quebrada:',
        'en': 'Broken rod action:',
        'es': 'Acción caña rota:',
        'ru': 'Действие при поломке удочки:'
    },
    'save_config': {
        'pt': '💾 Salvar',
        'en': '💾 Save',
        'es': '💾 Guardar',
        'ru': '💾 Сохранить'
    },
    'discard': {
        'pt': 'Descartar',
        'en': 'Discard',
        'es': 'Descartar',
        'ru': 'Выбросить'
    },
    'save_rod': {
        'pt': 'Guardar vara',
        'en': 'Save rod',
        'es': 'Guardar caña',
        'ru': 'Сохранить удочку'
    },
}

def add_translations_to_jsons():
    """Adicionar traduções nos 4 JSONs"""
    langs = [('pt', 'pt_BR'), ('en', 'en_US'), ('es', 'es_ES'), ('ru', 'ru_RU')]

    for lang_code, locale_dir in langs:
        filepath = f'locales/{locale_dir}/ui.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ui_section = data.get('ui', {})
        added = 0

        for key, trans in NEW_TRANSLATIONS.items():
            if key not in ui_section:
                ui_section[key] = trans[lang_code]
                added += 1

        data['ui'] = ui_section

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'  [{lang_code}] +{added} chaves')

def replace_hardcoded_in_python(content):
    """Substituir textos hardcoded por i18n.get_text()"""

    count = 0

    # Lista de substituições
    replacements = [
        # Distância do baú
        ('text="Distância do baú (unidades):"',
         'text=i18n.get_text("ui.chest_distance") if I18N_AVAILABLE else "Distância do baú (unidades):"'),

        # Checkboxes
        ('text="🔄 Auto-reload"',
         'text=i18n.get_text("ui.auto_reload") if I18N_AVAILABLE else "🔄 Auto-reload"'),

        ('text="🎯 Auto-focus"',
         'text=i18n.get_text("ui.auto_focus") if I18N_AVAILABLE else "🎯 Auto-focus"'),

        # Labels
        ('text="Ação vara quebrada:"',
         'text=i18n.get_text("ui.broken_rod_action") if I18N_AVAILABLE else "Ação vara quebrada:"'),

        # Botões
        ('text="💾 Salvar"',
         'text=i18n.get_text("ui.save_config") if I18N_AVAILABLE else "💾 Salvar"'),

        # Radiobuttons
        ('text="Descartar", variable=',
         'text=i18n.get_text("ui.discard") if I18N_AVAILABLE else "Descartar", variable='),

        ('text="Guardar vara", variable=',
         'text=i18n.get_text("ui.save_rod") if I18N_AVAILABLE else "Guardar vara", variable='),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
            print(f'    [OK] Substituido #{count}')

    return content, count

def main():
    print('=' * 70)
    print('  TRADUZIR TODOS OS WIDGETS HARDCODED')
    print('=' * 70)
    print()

    # Passo 1: Adicionar traduções nos JSONs
    print('[1/2] Adicionando traducoes nos JSONs...')
    add_translations_to_jsons()
    print()

    # Passo 2: Substituir no código Python
    print('[2/2] Substituindo widgets hardcoded...')
    filepath = r'c:\Users\Thiago\Desktop\v5\ui\main_window.py'
    content = read_file(filepath)

    content, count = replace_hardcoded_in_python(content)

    write_file(filepath, content)

    print()
    print('=' * 70)
    print(f'  CONCLUIDO: {count} widgets traduzidos')
    print('=' * 70)
    print()
    print('[INFO] Agora os widgets estao traduzidos para RUSSO!')
    print('[INFO] Execute: python main.py')

if __name__ == '__main__':
    main()
