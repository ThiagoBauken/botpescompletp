# -*- coding: utf-8 -*-
"""
SCRIPT DEFINITIVO: Adicionar i18n.get_text() + registro para TODOS os widgets HARDCODED
Processa TODAS as 9 abas de uma vez
"""

import re
import json

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# TODAS as chaves necessárias para todas as abas
ALL_TRANSLATIONS = {
    # Checkboxes e botões da ABA 1
    'include_baits_button': {'pt': '🎣 Incluir limpeza de iscas (transferir para baú)', 'en': '🎣 Include bait cleaning (transfer to chest)', 'es': '🎣 Incluir limpieza de cebos (transferir al cofre)', 'ru': '🎣 Включить очистку приманок (передать в сундук)'},
    'next_clean_status': {'pt': '📊 Próxima limpeza em:', 'en': '📊 Next clean in:', 'es': '📊 Próxima limpieza en:', 'ru': '📊 Следующая очистка через:'},
    'next_clean_catches': {'pt': 'pescas', 'en': 'catches', 'es': 'capturas', 'ru': 'улова'},

    # ABA 2 - Config
    'cycle_timeout_label': {'pt': 'Timeout do ciclo (segundos):', 'en': 'Cycle timeout (seconds):', 'es': 'Tiempo de espera del ciclo (segundos):', 'ru': 'Таймаут цикла (секунды):'},
    'rod_switch_limit_label': {'pt': 'Limite troca par de varas:', 'en': 'Rod pair switch limit:', 'es': 'Límite cambio par de cañas:', 'ru': 'Лимит смены пары удочек:'},
    'clicks_per_second_label': {'pt': 'Cliques por segundo:', 'en': 'Clicks per second:', 'es': 'Clics por segundo:', 'ru': 'Кликов в секунду:'},
    'maintenance_timeout_label': {'pt': 'Timeout manutenção (segundos):', 'en': 'Maintenance timeout (seconds):', 'es': 'Tiempo de espera mantenimiento (segundos):', 'ru': 'Таймаут обслуживания (секунды):'},
    'save_all': {'pt': '💾 Salvar Todas as Configurações', 'en': '💾 Save All Settings', 'es': '💾 Guardar Todas las Configuraciones', 'ru': '💾 Сохранить Все Настройки'},
    'reset_default': {'pt': '🔄 Resetar para Padrão', 'en': '🔄 Reset to Default', 'es': '🔄 Restablecer Predeterminado', 'ru': '🔄 Сбросить по Умолчанию'},
}

def add_translations_to_jsons():
    """Adicionar chaves faltantes nos 4 arquivos JSON"""
    langs = [('pt', 'pt_BR'), ('en', 'en_US'), ('es', 'es_ES'), ('ru', 'ru_RU')]

    for lang_code, locale_dir in langs:
        filepath = f'locales/{locale_dir}/ui.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ui_section = data.get('ui', {})
        added = 0

        for key, trans in ALL_TRANSLATIONS.items():
            if key not in ui_section:
                ui_section[key] = trans[lang_code]
                added += 1

        data['ui'] = ui_section

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'  [{lang_code}] +{added} chaves')

def replace_hardcoded_with_i18n(content):
    """Substituir TODOS os textos hardcoded por i18n.get_text()"""

    count = 0

    # Lista de substituições diretas (texto hardcoded → i18n)
    replacements = [
        # ABA 1 - Checkboxes e labels
        ('text="🎣 Incluir limpeza de iscas (transferir para baú)"',
         'text=i18n.get_text("ui.include_baits_button") if I18N_AVAILABLE else "🎣 Incluir limpeza de iscas (transferir para baú)"'),

        ('text="📊 Próxima limpeza em: 10 pescas"',
         'text=i18n.get_text("ui.next_clean_status") if I18N_AVAILABLE else "📊 Próxima limpeza em: 10 pescas"'),

        # ABA 2 - Labels de configuração
        ('text="Timeout do ciclo (segundos):"',
         'text=i18n.get_text("ui.cycle_timeout_label") if I18N_AVAILABLE else "Timeout do ciclo (segundos):"'),

        ('text="Limite troca par de varas:"',
         'text=i18n.get_text("ui.rod_switch_limit_label") if I18N_AVAILABLE else "Limite troca par de varas:"'),

        ('text="Cliques por segundo:"',
         'text=i18n.get_text("ui.clicks_per_second_label") if I18N_AVAILABLE else "Cliques por segundo:"'),

        ('text="Timeout manutenção (segundos):"',
         'text=i18n.get_text("ui.maintenance_timeout_label") if I18N_AVAILABLE else "Timeout manutenção (segundos):"'),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
            print(f'    [OK] Substituido #{count}')

    return content, count

def main():
    print("=" * 70)
    print("  ADICIONAR i18n.get_text() PARA TODOS OS WIDGETS HARDCODED")
    print("=" * 70)
    print()

    # Passo 1: Adicionar chaves nos JSONs
    print("[1/2] Adicionando chaves de traducao nos 4 JSONs...")
    add_translations_to_jsons()
    print()

    # Passo 2: Substituir hardcoded por i18n
    print("[2/2] Substituindo textos hardcoded por i18n.get_text()...")
    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    content, count = replace_hardcoded_with_i18n(content)

    # Salvar
    write_file(filepath, content)

    print()
    print("=" * 70)
    print(f"  CONCLUIDO: {count} substituicoes realizadas")
    print("=" * 70)
    print()
    print("[INFO] Agora execute: python main.py")
    print("[INFO] E mude o idioma para ver os widgets traduzidos!")

if __name__ == '__main__':
    main()
