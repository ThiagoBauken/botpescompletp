# -*- coding: utf-8 -*-
"""Script para traduzir ABA 1 - CONTROLE automaticamente"""

import re

# Mapeamento de strings para traduzir
translations = {
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
}

# Ler arquivo
with open(r'c:\Users\Thiago\Desktop\v5\ui\main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Aplicar todas as traduções
for old, new in translations.items():
    content = re.sub(old, new, content)

# Salvar arquivo
with open(r'c:\Users\Thiago\Desktop\v5\ui\main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] ABA 1 - CONTROLE traduzida com sucesso!")
print(f"Total de substituicoes: {len(translations)}")
