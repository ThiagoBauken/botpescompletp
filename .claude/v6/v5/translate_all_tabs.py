# -*- coding: utf-8 -*-
"""Script MASTER para traduzir TODAS as abas automaticamente"""

import re

# MAPEAMENTO COMPLETO DE TRADUÇÕES (strings mais importantes)
translations = {
    # === ABA 1: CONTROLE ===
    r'text="🎯 Taxa de sucesso:"': r'text=i18n.get_text("ui.success_rate") if I18N_AVAILABLE else "🎯 Taxa de sucesso:"',
    r'text="🍖 Alimentações:"': r'text=i18n.get_text("ui.feedings") if I18N_AVAILABLE else "🍖 Alimentações:"',
    r'text="🧹 Limpezas:"': r'text=i18n.get_text("ui.cleanings") if I18N_AVAILABLE else "🧹 Limpezas:"',
    r'text="🔧 Varas quebradas:"': r'text=i18n.get_text("ui.broken_rods") if I18N_AVAILABLE else "🔧 Varas quebradas:"',
    r'text="⏱️ Timeouts:"': r'text=i18n.get_text("ui.timeouts") if I18N_AVAILABLE else "⏱️ Timeouts:"',
    r'text="🎣 Vara \(último timeout\):"': r'text=i18n.get_text("ui.last_rod") if I18N_AVAILABLE else "🎣 Vara (último timeout):"',
    r'text="🔄 Limpeza Automática"': r'text=i18n.get_text("ui.auto_clean") if I18N_AVAILABLE else "🔄 Limpeza Automática"',
    r'text="🐟 Limpar inventário a cada:"': r'text=i18n.get_text("ui.clean_every") if I18N_AVAILABLE else "🐟 Limpar inventário a cada:"',
    r'text="pescas"': r'text=i18n.get_text("ui.catches") if I18N_AVAILABLE else "pescas"',
    r'text="✅ Ativar limpeza automática"': r'text=i18n.get_text("ui.enable_auto_clean") if I18N_AVAILABLE else "✅ Ativar limpeza automática"',
    r'text="💾 Salvar Config de Limpeza"': r'text=i18n.get_text("ui.save_clean_config") if I18N_AVAILABLE else "💾 Salvar Config de Limpeza"',
    r'text="🚀 Iniciar Bot"': r'text=i18n.get_text("ui.start_bot") if I18N_AVAILABLE else "🚀 Iniciar Bot"',
    r'text="🛑 Parar Bot"': r'text=i18n.get_text("ui.stop_bot") if I18N_AVAILABLE else "🛑 Parar Bot"',
    r'text="⏸️ Pausar"': r'text=i18n.get_text("ui.pause_bot") if I18N_AVAILABLE else "⏸️ Pausar"',
    r'text="▶️ Continuar"': r'text=i18n.get_text("ui.resume_bot") if I18N_AVAILABLE else "▶️ Continuar"',
    r'text="🚨 PARADA DE EMERGÊNCIA"': r'text=i18n.get_text("ui.emergency_stop") if I18N_AVAILABLE else "🚨 PARADA DE EMERGÊNCIA"',

    # === ABA 2: CONFIGURAÇÃO ===
    r'text="⚙️ Configurações Gerais do Sistema"': r'text=i18n.get_text("ui.general_config") if I18N_AVAILABLE else "⚙️ Configurações Gerais do Sistema"',
    r'text="💾 Salvar"': r'text=i18n.get_text("ui.save") if I18N_AVAILABLE else "💾 Salvar"',
    r'text="🗑️ Descartar"': r'text=i18n.get_text("ui.discard") if I18N_AVAILABLE else "🗑️ Descartar"',

    # === ABA 3: ALIMENTAÇÃO ===
    r'text="🍖 Sistema de Alimentação Inteligente"': r'text=i18n.get_text("ui.smart_feeding_system") if I18N_AVAILABLE else "🍖 Sistema de Alimentação Inteligente"',
    r'text="⚡ Quando Alimentar"': r'text=i18n.get_text("ui.when_to_feed") if I18N_AVAILABLE else "⚡ Quando Alimentar"',
    r'text="🐟 Por capturas \(recomendado\)"': r'text=i18n.get_text("ui.trigger_by_catches") if I18N_AVAILABLE else "🐟 Por capturas (recomendado)"',
    r'text="⏰ Por tempo"': r'text=i18n.get_text("ui.trigger_by_time") if I18N_AVAILABLE else "⏰ Por tempo"',
    r'text="🐟 Alimentar a cada:"': r'text=i18n.get_text("ui.feed_every") if I18N_AVAILABLE else "🐟 Alimentar a cada:"',
    r'text="minutos"': r'text=i18n.get_text("ui.minutes") if I18N_AVAILABLE else "minutos"',
    r'text="🍽️ Configurações de Alimentação"': r'text=i18n.get_text("ui.feeding_config") if I18N_AVAILABLE else "🍽️ Configurações de Alimentação"',
    r'text="💾 Salvar Configurações"': r'text=i18n.get_text("ui.save_feeding_config") if I18N_AVAILABLE else "💾 Salvar Configurações"',
    r'text="🔄 Restaurar Padrão"': r'text=i18n.get_text("ui.reset_defaults") if I18N_AVAILABLE else "🔄 Restaurar Padrão"',

    # === ABA 4: TEMPLATES ===
    r'text="🎯 Configuração de Confiança por Template"': r'text=i18n.get_text("ui.templates_confidence") if I18N_AVAILABLE else "🎯 Configuração de Confiança por Template"',
    r'text="📂 Categoria"': r'text=i18n.get_text("ui.category") if I18N_AVAILABLE else "📂 Categoria"',
    r'text="📋 Template"': r'text=i18n.get_text("ui.template") if I18N_AVAILABLE else "📋 Template"',
    r'text="🎯 Confiança"': r'text=i18n.get_text("ui.confidence") if I18N_AVAILABLE else "🎯 Confiança"',
    r'text="💾 Salvar Tudo"': r'text=i18n.get_text("ui.save_all_confidence") if I18N_AVAILABLE else "💾 Salvar Tudo"',

    # === ABA 5: ANTI-DETECÇÃO ===
    r'text="🛡️ Sistema Anti-Detecção Avançado"': r'text=i18n.get_text("ui.anti_detection") if I18N_AVAILABLE else "🛡️ Sistema Anti-Detecção Avançado"',
    r'text="🖱️ Variação de Cliques"': r'text=i18n.get_text("ui.click_variation") if I18N_AVAILABLE else "🖱️ Variação de Cliques"',
    r'text="🏃 Variação de Movimentos"': r'text=i18n.get_text("ui.movement_variation") if I18N_AVAILABLE else "🏃 Variação de Movimentos"',
    r'text="😴 Pausas Naturais"': r'text=i18n.get_text("ui.natural_breaks") if I18N_AVAILABLE else "😴 Pausas Naturais"',
    r'text="💾 Salvar Configurações Anti-Detecção"': r'text=i18n.get_text("ui.save_anti_detection") if I18N_AVAILABLE else "💾 Salvar Configurações Anti-Detecção"',

    # === ABA 6: VISUALIZADOR ===
    r'text="🐟 Visualizador Template Matching - CATCH"': r'text=i18n.get_text("ui.template_viewer") if I18N_AVAILABLE else "🐟 Visualizador Template Matching - CATCH"',
    r'text="📊 Status do Visualizador"': r'text=i18n.get_text("ui.viewer_status") if I18N_AVAILABLE else "📊 Status do Visualizador"',
    r'text="📊 Status: Parado"': r'text=i18n.get_text("ui.status_stopped") if I18N_AVAILABLE else "📊 Status: Parado"',
    r'text="🎯 Estatísticas de Detecção"': r'text=i18n.get_text("ui.detection_stats") if I18N_AVAILABLE else "🎯 Estatísticas de Detecção"',
    r'text="▶️ Iniciar Visualizador"': r'text=i18n.get_text("ui.start_viewer") if I18N_AVAILABLE else "▶️ Iniciar Visualizador"',
    r'text="⏹️ Parar Visualizador"': r'text=i18n.get_text("ui.stop_viewer") if I18N_AVAILABLE else "⏹️ Parar Visualizador"',

    # === ABA 7: HOTKEYS ===
    r'text="⌨️ Configuração de Hotkeys"': r'text=i18n.get_text("ui.hotkeys_config") if I18N_AVAILABLE else "⌨️ Configuração de Hotkeys"',
    r'text="⌨️ Hotkey"': r'text=i18n.get_text("ui.hotkey") if I18N_AVAILABLE else "⌨️ Hotkey"',
    r'text="🎯 Ação"': r'text=i18n.get_text("ui.action") if I18N_AVAILABLE else "🎯 Ação"',
    r'text="📋 Tecla Atual"': r'text=i18n.get_text("ui.current_key") if I18N_AVAILABLE else "📋 Tecla Atual"',
    r'text="🎯 Capturar"': r'text=i18n.get_text("ui.capture") if I18N_AVAILABLE else "🎯 Capturar"',

    # === ABA 8: ARDUINO ===
    r'text="🔌 Arduino Leonardo - Controle de Hardware"': r'text=i18n.get_text("ui.arduino_leonardo") if I18N_AVAILABLE else "🔌 Arduino Leonardo - Controle de Hardware"',
    r'text="🔗 Status da Conexão"': r'text=i18n.get_text("ui.connection_status") if I18N_AVAILABLE else "🔗 Status da Conexão"',
    r'text="Arduino não conectado"': r'text=i18n.get_text("ui.not_connected") if I18N_AVAILABLE else "Arduino não conectado"',
    r'text="🧪 Testar"': r'text=i18n.get_text("ui.test_connection") if I18N_AVAILABLE else "🧪 Testar"',
    r'text="🔌 Conectar"': r'text=i18n.get_text("ui.connect") if I18N_AVAILABLE else "🔌 Conectar"',
    r'text="📴 Desconectar"': r'text=i18n.get_text("ui.disconnect") if I18N_AVAILABLE else "📴 Desconectar"',
    r'text="📤 Enviar"': r'text=i18n.get_text("ui.send") if I18N_AVAILABLE else "📤 Enviar"',
    r'text="🗑️ Limpar"': r'text=i18n.get_text("ui.clear_log") if I18N_AVAILABLE else "🗑️ Limpar"',

    # === ABA 9: AJUDA ===
    r'text="❓ Ajuda & Documentação"': r'text=i18n.get_text("ui.help_documentation") if I18N_AVAILABLE else "❓ Ajuda & Documentação"',
    r'text="⌨️ Hotkeys Principais"': r'text=i18n.get_text("ui.main_hotkeys") if I18N_AVAILABLE else "⌨️ Hotkeys Principais"',
    r'text="⚙️ Configuração Inicial"': r'text=i18n.get_text("ui.initial_config") if I18N_AVAILABLE else "⚙️ Configuração Inicial"',
    r'text="🔧 Solução de Problemas"': r'text=i18n.get_text("ui.troubleshooting") if I18N_AVAILABLE else "🔧 Solução de Problemas"',
    r'text="💬 Suporte"': r'text=i18n.get_text("ui.support") if I18N_AVAILABLE else "💬 Suporte"',
}

print(f"[INFO] Iniciando traducao de {len(translations)} strings...")

# Ler arquivo
try:
    with open(r'c:\Users\Thiago\Desktop\v5\ui\main_window.py', 'r', encoding='utf-8') as f:
        content = f.read()
    print("[OK] Arquivo lido com sucesso")
except Exception as e:
    print(f"[ERROR] Erro ao ler arquivo: {e}")
    exit(1)

# Aplicar todas as traduções
count = 0
for old, new in translations.items():
    matches = len(re.findall(old, content))
    if matches > 0:
        content = re.sub(old, new, content)
        count += matches
        print(f"[OK] Substituido: {matches}x")

# Salvar arquivo
try:
    with open(r'c:\Users\Thiago\Desktop\v5\ui\main_window.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Arquivo salvo com sucesso!")
    print(f"[INFO] Total de substituicoes: {count}")
except Exception as e:
    print(f"[ERROR] Erro ao salvar arquivo: {e}")
    exit(1)

print("[SUCCESS] TODAS as abas traduzidas com sucesso!")
