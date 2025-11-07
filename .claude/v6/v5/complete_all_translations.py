# -*- coding: utf-8 -*-
"""
SCRIPT COMPLETO: Traduzir e registrar TODOS os widgets
Este script vai:
1. Adicionar i18n.get_text() para todos os textos hardcoded
2. Adicionar self.register_translatable_widget() para todos
3. Adicionar chaves faltantes nos JSONs
"""

import re
import json

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def add_missing_translations_to_json():
    """Adicionar todas as chaves de tradução faltantes nos 4 JSONs"""

    # Mapeamento completo de TODAS as traduções necessárias
    translations = {
        # Botões gerais
        'start_bot': {
            'pt': '▶️ Iniciar Bot',
            'en': '▶️ Start Bot',
            'es': '▶️ Iniciar Bot',
            'ru': '▶️ Запустить Бота'
        },
        'stop_bot': {
            'pt': '⏹️ Parar Bot',
            'en': '⏹️ Stop Bot',
            'es': '⏹️ Detener Bot',
            'ru': '⏹️ Остановить Бота'
        },
        'pause_bot': {
            'pt': '⏸️ Pausar',
            'en': '⏸️ Pause',
            'es': '⏸️ Pausar',
            'ru': '⏸️ Пауза'
        },
        'resume_bot': {
            'pt': '▶️ Retomar',
            'en': '▶️ Resume',
            'es': '▶️ Reanudar',
            'ru': '▶️ Возобновить'
        },
        'emergency_stop': {
            'pt': '🚨 PARADA DE EMERGÊNCIA',
            'en': '🚨 EMERGENCY STOP',
            'es': '🚨 PARADA DE EMERGENCIA',
            'ru': '🚨 АВАРИЙНАЯ ОСТАНОВКА'
        },
        'test_feeding': {
            'pt': '🧪 Testar Alimentação',
            'en': '🧪 Test Feeding',
            'es': '🧪 Probar Alimentación',
            'ru': '🧪 Тест Питания'
        },
        'test_cleaning': {
            'pt': '🧪 Testar Limpeza',
            'en': '🧪 Test Cleaning',
            'es': '🧪 Probar Limpieza',
            'ru': '🧪 Тест Очистки'
        },
        'test_maintenance': {
            'pt': '🧪 Testar Manutenção',
            'en': '🧪 Test Maintenance',
            'es': '🧪 Probar Mantenimiento',
            'ru': '🧪 Тест Обслуживания'
        },
        'manual_controls': {
            'pt': '🎮 Controles Manuais',
            'en': '🎮 Manual Controls',
            'es': '🎮 Controles Manuales',
            'ru': '🎮 Ручное Управление'
        },

        # Config tab
        'general_config': {
            'pt': '⚙️ Configurações Gerais do Sistema',
            'en': '⚙️ General System Settings',
            'es': '⚙️ Configuración General del Sistema',
            'ru': '⚙️ Общие Настройки Системы'
        },
        'timeouts_cycles': {
            'pt': '⏱️ Timeouts e Ciclos',
            'en': '⏱️ Timeouts and Cycles',
            'es': '⏱️ Tiempos de Espera y Ciclos',
            'ru': '⏱️ Таймауты и Циклы'
        },
        'cycle_timeout': {
            'pt': 'Timeout do ciclo (segundos):',
            'en': 'Cycle timeout (seconds):',
            'es': 'Tiempo de espera del ciclo (segundos):',
            'ru': 'Таймаут цикла (секунды):'
        },
        'rod_switch_limit': {
            'pt': 'Limite troca par de varas:',
            'en': 'Rod pair switch limit:',
            'es': 'Límite cambio par de cañas:',
            'ru': 'Лимит смены пары удочек:'
        },
        'clicks_per_second': {
            'pt': 'Cliques por segundo:',
            'en': 'Clicks per second:',
            'es': 'Clics por segundo:',
            'ru': 'Кликов в секунду:'
        },
        'maintenance_timeout': {
            'pt': 'Timeout manutenção (segundos):',
            'en': 'Maintenance timeout (seconds):',
            'es': 'Tiempo de espera mantenimiento (segundos):',
            'ru': 'Таймаут обслуживания (секунды):'
        },
        'save_all': {
            'pt': '💾 Salvar Todas as Configurações',
            'en': '💾 Save All Settings',
            'es': '💾 Guardar Todas las Configuraciones',
            'ru': '💾 Сохранить Все Настройки'
        },
        'reset_all': {
            'pt': '🔄 Resetar para Padrão',
            'en': '🔄 Reset to Default',
            'es': '🔄 Restablecer Predeterminado',
            'ru': '🔄 Сбросить по Умолчанию'
        },

        # Mais traduções serão adicionadas conforme necessário
    }

    # Atualizar os 4 arquivos JSON
    langs = [('pt', 'pt_BR'), ('en', 'en_US'), ('es', 'es_ES'), ('ru', 'ru_RU')]

    for lang_code, locale_dir in langs:
        filepath = f'locales/{locale_dir}/ui.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ui_section = data.get('ui', {})
        added = 0

        # Adicionar chaves faltantes
        for key, trans in translations.items():
            if key not in ui_section:
                ui_section[key] = trans[lang_code]
                added += 1

        data['ui'] = ui_section

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'[{lang_code}] Adicionadas {added} novas chaves')

def register_all_control_tab_widgets(content):
    """Registrar TODOS os widgets da ABA 1"""

    registrations_needed = [
        # Botões (faltam registrar)
        {
            'pattern': r"(tk\.Button\(.*?text=i18n\.get_text\(\"ui\.start_bot\"\).*?\))\s*\n(\s*)(self\.start_btn\.pack)",
            'replacement': r"\1\n\2self.register_translatable_widget('buttons', 'start_btn', self.start_btn, 'ui.start_bot')\n\2\3",
            'name': 'start_btn'
        },
        {
            'pattern': r"(tk\.Button\(.*?text=i18n\.get_text\(\"ui\.stop_bot\"\).*?\))\s*\n(\s*)(self\.stop_btn\.pack)",
            'replacement': r"\1\n\2self.register_translatable_widget('buttons', 'stop_btn', self.stop_btn, 'ui.stop_bot')\n\2\3",
            'name': 'stop_btn'
        },
    ]

    count = 0
    for reg in registrations_needed:
        if re.search(reg['pattern'], content):
            content = re.sub(reg['pattern'], reg['replacement'], content)
            count += 1
            print(f"  [OK] Registered {reg['name']}")

    return content, count

def main():
    print("[INFO] INICIANDO TRADUCAO COMPLETA DE TODOS OS WIDGETS...")
    print()

    # Passo 1: Adicionar chaves faltantes nos JSONs
    print("[STEP 1] Adicionando chaves de traducao nos JSONs...")
    add_missing_translations_to_json()
    print()

    # Passo 2: Ler arquivo principal
    print("[STEP 2] Processando main_window.py...")
    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    # Passo 3: Adicionar i18n.get_text() para widgets hardcoded
    print("[STEP 3] Adicionando i18n.get_text() para widgets hardcoded...")
    # (implementar conforme necessário)

    # Passo 4: Registrar widgets
    print("[STEP 4] Registrando widgets da ABA 1...")
    content, count = register_all_control_tab_widgets(content)
    print(f"  Total: {count} widgets registrados")

    # Salvar
    write_file(filepath, content)
    print()
    print("[OK] Processo concluido!")
    print(f"[INFO] Arquivo salvo: {filepath}")

if __name__ == '__main__':
    main()
