# -*- coding: utf-8 -*-
"""
Teste para verificar cobertura das traduções dinâmicas
"""
import re

def _safe_print(text):
    """Print seguro para Windows (evita erro com emojis)"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def analyze_translation_coverage():
    """Analisar quantos widgets têm tradução mas não estão registrados"""

    with open('ui/main_window.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Contar widgets criados com tradução
    widgets_with_i18n = len(re.findall(r'i18n\.get_text\(|_\(\"', content))

    # Contar registros de widgets
    registered_widgets = len(re.findall(r'register_translatable_widget', content))

    # Contar widgets criados
    total_widgets = len(re.findall(r'tk\.(Label|Button|Checkbutton|LabelFrame)\(|ttk\.(Label|Button|Checkbutton|LabelFrame)\(', content))

    _safe_print("=" * 60)
    _safe_print("ANALISE DE COBERTURA DE TRADUCOES")
    _safe_print("=" * 60)
    _safe_print(f"Widgets criados com i18n/_(..):  {widgets_with_i18n}")
    _safe_print(f"Widgets registrados p/ atualizacao: {registered_widgets}")
    _safe_print(f"Total de widgets criados:         {total_widgets}")
    _safe_print("")
    _safe_print(f"PROBLEMA: {widgets_with_i18n - registered_widgets} widgets com traducao")
    _safe_print(f"   NAO estao registrados para atualizacao dinamica!")
    _safe_print("")
    _safe_print("Isso significa que quando o idioma muda:")
    _safe_print(f"   - {registered_widgets} widgets serao atualizados")
    _safe_print(f"   - {widgets_with_i18n - registered_widgets} widgets NAO serao atualizados")
    _safe_print("=" * 60)

    return {
        'widgets_with_i18n': widgets_with_i18n,
        'registered': registered_widgets,
        'total_widgets': total_widgets,
        'coverage_percent': (registered_widgets / widgets_with_i18n * 100) if widgets_with_i18n > 0 else 0
    }

if __name__ == '__main__':
    result = analyze_translation_coverage()
    _safe_print(f"\nTaxa de cobertura: {result['coverage_percent']:.1f}%")

    if result['coverage_percent'] < 50:
        _safe_print("CRITICO: Menos de 50% dos widgets com traducao estao registrados!")
        _safe_print("   A troca de idioma NAO funcionara corretamente.")
    elif result['coverage_percent'] < 80:
        _safe_print("ATENCAO: Cobertura insuficiente de traducoes dinamicas.")
    else:
        _safe_print("Boa cobertura de traducoes dinamicas!")
