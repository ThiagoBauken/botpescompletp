#!/usr/bin/env python3
"""
🐟 TEST FISH DETECTION - Testar detecção de peixes
"""

import time
import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.template_engine import TemplateEngine
from core.config_manager import ConfigManager

def _safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('ascii', 'ignore').decode())

def test_fish_templates():
    """Testar quais templates de peixe estão funcionando"""

    print("="*70)
    print("🐟 TESTE DE DETECÇÃO DE PEIXES")
    print("="*70)
    print()

    # 1. Inicializar config e template engine
    print("📋 Carregando configurações...")
    config = ConfigManager()
    template_engine = TemplateEngine(config)
    print(f"✅ Config carregada: {len(template_engine.template_cache)} templates")
    print()

    # 2. Lista de peixes que DEVEM ser detectados
    fish_list = [
        'SALMONN',    # Salmão
        'TROUTT',     # Truta
        'sardine',    # Sardinha
        'anchovy',    # Anchova
        'yellowperch', # Perca amarela
        'herring',    # Arenque
        'peixecru',   # Peixe cru
        'shark',      # Tubarão
        'catfish',    # Bagre
        'roughy'      # Roughy
    ]

    print("🔍 Testando templates de peixes...")
    print("-"*70)

    templates_ok = []
    templates_missing = []
    templates_low_confidence = []

    for fish_name in fish_list:
        # Verificar se template existe
        has_template = template_engine.has_template(fish_name)

        if not has_template:
            templates_missing.append(fish_name)
            print(f"❌ {fish_name:15s} - TEMPLATE FALTANDO")
            continue

        # Verificar confiança
        confidence = template_engine.get_template_confidence(fish_name)

        if confidence >= 0.9:
            status = "⚠️ MUITO ALTA"
            templates_low_confidence.append((fish_name, confidence))
        elif confidence >= 0.8:
            status = "✅ OK"
            templates_ok.append((fish_name, confidence))
        else:
            status = "✅ BOA"
            templates_ok.append((fish_name, confidence))

        print(f"{'✅' if confidence < 0.9 else '⚠️'} {fish_name:15s} - Confiança: {confidence:.2f} {status}")

    print("-"*70)
    print()

    # 3. Resumo
    print("📊 RESUMO:")
    print(f"   ✅ Templates OK: {len(templates_ok)}")
    print(f"   ⚠️  Confiança muito alta: {len(templates_low_confidence)}")
    print(f"   ❌ Templates faltando: {len(templates_missing)}")
    print()

    # 4. Recomendações
    if templates_missing:
        print("🔧 PROBLEMA 1: Templates faltando")
        print("   Solução: Copiar templates do seu PC para o dele:")
        print(f"   Arquivos faltando em templates/:")
        for fish in templates_missing:
            print(f"      - {fish}.png")
        print()

    if templates_low_confidence:
        print("🔧 PROBLEMA 2: Confiança muito alta (pode não detectar)")
        print("   Solução: Reduzir confiança na config:")
        print()
        print("   Edite config/default_config.json ou data/config.json:")
        print("   {")
        print("     \"template_confidence\": {")
        for fish, conf in templates_low_confidence:
            new_conf = 0.75  # Reduzir para 0.75
            print(f"       \"{fish}\": {new_conf},  // Era {conf:.2f}")
        print("     }")
        print("   }")
        print()

    # 5. Teste prático
    print("="*70)
    print("🎮 TESTE PRÁTICO")
    print("="*70)
    print()
    print("Para testar a detecção:")
    print("1. Abra o jogo")
    print("2. Abra seu INVENTÁRIO (deve ter peixes)")
    print("3. Pressione ENTER aqui para capturar tela e detectar peixes")
    print()

    input("Pressione ENTER quando estiver pronto...")

    print()
    print("📸 Capturando tela...")
    screenshot = template_engine.capture_screen()

    if screenshot is None:
        print("❌ Falha ao capturar tela!")
        return

    print(f"✅ Tela capturada: {screenshot.shape[1]}x{screenshot.shape[0]}")
    print()

    print("🔍 Detectando peixes na tela...")
    print("-"*70)

    detected = []

    for fish_name in fish_list:
        if not template_engine.has_template(fish_name):
            continue

        # Tentar detectar
        result = template_engine.detect_template(fish_name, confidence=None)

        if result.found:
            detected.append((fish_name, result.confidence, result.location))
            print(f"✅ {fish_name:15s} - DETECTADO! Confiança: {result.confidence:.3f} em {result.location}")
        else:
            print(f"❌ {fish_name:15s} - Não detectado")

    print("-"*70)
    print()

    if detected:
        print(f"🎯 Total detectado: {len(detected)} peixes")
        print()
        print("✅ SUCESSO! O sistema está detectando peixes!")
    else:
        print("❌ NENHUM PEIXE DETECTADO!")
        print()
        print("Possíveis causas:")
        print("1. Inventário não está aberto")
        print("2. Não tem peixes no inventário")
        print("3. Templates não correspondem às imagens do jogo")
        print("4. Confiança muito alta")
        print()
        print("Recomendações:")
        print("1. Abaixar todas as confianças para 0.70")
        print("2. Verificar se templates são do mesmo jogo/versão")
        print("3. Capturar novos templates do jogo dele")

    print()
    print("="*70)
    print("Teste concluído!")
    print("="*70)

if __name__ == "__main__":
    try:
        test_fish_templates()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

    print("\nPressione ENTER para sair...")
    input()
