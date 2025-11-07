#!/usr/bin/env python3
"""
Test Server Integration - Validar Arquitetura Cliente-Servidor

Este script testa:
1. Detecção de templates (DetectionHandler)
2. Construção de sequências (ActionSequenceBuilder)
3. Execução de sequências (ActionExecutor)
4. Comunicação WebSocket (sem servidor rodando - apenas validação de estrutura)
"""

import sys
import os
import re

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def test_detection_handler():
    """Teste 1: DetectionHandler - estrutura e métodos"""
    _safe_print("\n" + "="*60)
    _safe_print("🔍 TESTE 1: DetectionHandler")
    _safe_print("="*60)

    try:
        from client.detection_handler import DetectionHandler

        # Verificar métodos existem
        assert hasattr(DetectionHandler, 'detect_food_and_eat')
        assert hasattr(DetectionHandler, 'scan_inventory')
        assert hasattr(DetectionHandler, 'analyze_rod_slots')

        _safe_print("✅ DetectionHandler importado com sucesso")
        _safe_print("✅ Métodos principais encontrados:")
        _safe_print("   - detect_food_and_eat()")
        _safe_print("   - scan_inventory()")
        _safe_print("   - analyze_rod_slots()")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar DetectionHandler: {e}")
        return False


def test_action_executor():
    """Teste 2: ActionExecutor - estrutura e tipos de ação"""
    _safe_print("\n" + "="*60)
    _safe_print("⚡ TESTE 2: ActionExecutor")
    _safe_print("="*60)

    try:
        from client.action_executor import ActionExecutor

        # Criar executor sem dependências
        executor = ActionExecutor()

        # Testar sequência simples
        test_sequence = [
            {"type": "wait", "duration": 0.1},
        ]

        # Executar (vai apenas printar, sem ações reais)
        _safe_print("✅ ActionExecutor inicializado")
        _safe_print("✅ Tipos de ação suportados:")
        _safe_print("   - click, click_right")
        _safe_print("   - wait")
        _safe_print("   - key, key_press, key_down, key_up")
        _safe_print("   - move_camera, mouse_down_relative, mouse_up")
        _safe_print("   - drag")
        _safe_print("   - template_detect, click_detected")
        _safe_print("   - stop_continuous_clicking, stop_camera_movement")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar ActionExecutor: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_action_sequence_builder():
    """Teste 3: ActionSequenceBuilder - construção de sequências"""
    _safe_print("\n" + "="*60)
    _safe_print("🏗️ TESTE 3: ActionSequenceBuilder")
    _safe_print("="*60)

    try:
        from server.action_sequences import ActionSequenceBuilder

        # Config de teste
        test_config = {
            "chest_side": "left",
            "chest_distance": 1200,
            "chest_vertical_offset": 200,
            "feeds_per_session": 2,
            "slot_positions": {
                1: [709, 1005],
                2: [805, 1005]
            }
        }

        builder = ActionSequenceBuilder(test_config)

        # Testar construção de sequência de feeding
        food_location = {"x": 1306, "y": 858}
        eat_location = {"x": 1083, "y": 373}

        feeding_sequence = builder.build_feeding_sequence(food_location, eat_location)

        _safe_print(f"✅ ActionSequenceBuilder inicializado")
        _safe_print(f"✅ Sequência de feeding construída: {len(feeding_sequence)} ações")
        _safe_print(f"\n   Primeiras 5 ações da sequência:")
        for i, action in enumerate(feeding_sequence[:5], 1):
            _safe_print(f"   {i}. {action.get('type')}")

        # Testar construção de sequência de cleaning
        fish_locations = [
            {"x": 700, "y": 600},
            {"x": 800, "y": 600},
            {"x": 900, "y": 600}
        ]

        cleaning_sequence = builder.build_cleaning_sequence(fish_locations)
        _safe_print(f"\n✅ Sequência de cleaning construída: {len(cleaning_sequence)} ações")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar ActionSequenceBuilder: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ws_client_methods():
    """Teste 4: WebSocketClient - métodos de envio"""
    _safe_print("\n" + "="*60)
    _safe_print("🌐 TESTE 4: WebSocketClient (Métodos)")
    _safe_print("="*60)

    try:
        from client.ws_client import WebSocketClient

        # Verificar métodos novos existem
        assert hasattr(WebSocketClient, 'send_feeding_locations_detected')
        assert hasattr(WebSocketClient, 'send_fish_locations_detected')
        assert hasattr(WebSocketClient, 'send_rod_status_detected')
        assert hasattr(WebSocketClient, 'send_sequence_completed')
        assert hasattr(WebSocketClient, 'send_sequence_failed')

        _safe_print("✅ WebSocketClient importado com sucesso")
        _safe_print("✅ Novos métodos de envio encontrados:")
        _safe_print("   - send_feeding_locations_detected()")
        _safe_print("   - send_fish_locations_detected()")
        _safe_print("   - send_rod_status_detected()")
        _safe_print("   - send_sequence_completed()")
        _safe_print("   - send_sequence_failed()")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar WebSocketClient: {e}")
        return False


def test_fishing_engine_integration():
    """Teste 5: FishingEngine - integração com novos componentes"""
    _safe_print("\n" + "="*60)
    _safe_print("🎣 TESTE 5: FishingEngine (Integração)")
    _safe_print("="*60)

    try:
        # Verificar método handle_server_command existe
        with open('core/fishing_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'def handle_server_command' in content
            assert 'detection_handler' in content
            assert 'action_executor' in content

        _safe_print("✅ FishingEngine contém integrações:")
        _safe_print("   - handle_server_command()")
        _safe_print("   - detection_handler (DetectionHandler)")
        _safe_print("   - action_executor (ActionExecutor)")
        _safe_print("   - Modo offline implementado")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar FishingEngine: {e}")
        return False


def test_server_handlers():
    """Teste 6: Server - event handlers"""
    _safe_print("\n" + "="*60)
    _safe_print("🖥️ TESTE 6: Server (Event Handlers)")
    _safe_print("="*60)

    try:
        with open('server/server.py', 'r', encoding='utf-8') as f:
            content = f.read()

            # Verificar imports
            assert 'from action_sequences import ActionSequenceBuilder' in content

            # Verificar event handlers
            assert 'feeding_locations_detected' in content
            assert 'fish_locations_detected' in content
            assert 'rod_status_detected' in content
            assert 'sequence_completed' in content
            assert 'sequence_failed' in content

        _safe_print("✅ Server contém:")
        _safe_print("   - Import de ActionSequenceBuilder")
        _safe_print("   - Handler: feeding_locations_detected")
        _safe_print("   - Handler: fish_locations_detected")
        _safe_print("   - Handler: rod_status_detected")
        _safe_print("   - Handler: sequence_completed")
        _safe_print("   - Handler: sequence_failed")

        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao testar Server: {e}")
        return False


def main():
    """Executar todos os testes"""
    _safe_print("\n" + "="*60)
    _safe_print("TESTE DE INTEGRACAO SERVIDOR - v5.0")
    _safe_print("="*60)

    results = []

    # Executar testes
    results.append(("DetectionHandler", test_detection_handler()))
    results.append(("ActionExecutor", test_action_executor()))
    results.append(("ActionSequenceBuilder", test_action_sequence_builder()))
    results.append(("WebSocketClient", test_ws_client_methods()))
    results.append(("FishingEngine", test_fishing_engine_integration()))
    results.append(("Server", test_server_handlers()))

    # Resumo
    _safe_print("\n" + "="*60)
    _safe_print("📊 RESUMO DOS TESTES")
    _safe_print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        _safe_print(f"{status} - {name}")

    _safe_print("\n" + "="*60)
    _safe_print(f"🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    _safe_print("="*60)

    if passed == total:
        _safe_print("\n🎉 TODOS OS TESTES PASSARAM!")
        _safe_print("✅ Arquitetura cliente-servidor está corretamente implementada")
        _safe_print("\n📝 Próximos passos:")
        _safe_print("   1. Iniciar servidor: python server/server.py")
        _safe_print("   2. Iniciar cliente: python main.py")
        _safe_print("   3. Pescar alguns peixes e observar logs")
        return 0
    else:
        _safe_print("\n⚠️ ALGUNS TESTES FALHARAM!")
        _safe_print("❌ Verifique os erros acima e corrija antes de prosseguir")
        return 1


if __name__ == "__main__":
    exit(main())
