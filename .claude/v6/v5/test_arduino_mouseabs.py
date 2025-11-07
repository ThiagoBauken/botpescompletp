"""
🧪 TESTE SIMPLES: Verificar se MOUSEABS funciona no Arduino

Testa movimento do mouse para coordenadas específicas das varas
"""
import time
import sys

def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def main():
    _safe_print("\n" + "="*70)
    _safe_print("🧪 TESTE: Arduino MOUSEABS - Movimento para Slots de Varas")
    _safe_print("="*70 + "\n")

    # Importar Arduino Input Manager
    from core.arduino_input_manager import ArduinoInputManager
    from core.config_manager import ConfigManager

    _safe_print("📋 Inicializando componentes...")
    config = ConfigManager()

    # Pegar porta do config
    arduino_port = config.get('arduino.port', 'COM8')
    arduino_baudrate = config.get('arduino.baudrate', 115200)

    _safe_print(f"   Porta: {arduino_port}")
    _safe_print(f"   Baudrate: {arduino_baudrate}")

    arduino = ArduinoInputManager(port=arduino_port, baudrate=arduino_baudrate, config_manager=config)

    if not arduino.connect():
        _safe_print("❌ FALHA: Não foi possível conectar ao Arduino!")
        _safe_print("   Verifique se o Arduino está conectado e o sketch foi enviado.")
        return False

    _safe_print("✅ Arduino conectado!\n")

    # Coordenadas dos slots das varas (EXATAS do v3)
    slot_positions = {
        1: (709, 1005),
        2: (805, 1005),
        3: (899, 1005),
        4: (992, 1005),
        5: (1092, 1005),
        6: (1188, 1005)
    }

    _safe_print("🎯 TESTE 1: Mover para centro da tela (960, 540)")
    _safe_print("-" * 70)
    success = arduino.move_to(960, 540)
    if success:
        _safe_print("✅ Comando MOUSEABS enviado com sucesso!")
    else:
        _safe_print("❌ FALHA ao enviar MOUSEABS!")

    time.sleep(2)

    _safe_print("\n🎯 TESTE 2: Mover para cada slot de vara (1-6)")
    _safe_print("-" * 70)

    for slot, (x, y) in slot_positions.items():
        _safe_print(f"\n📍 Slot {slot}: ({x}, {y})")
        success = arduino.move_to(x, y)

        if success:
            _safe_print(f"   ✅ Mouse movido para slot {slot}")
        else:
            _safe_print(f"   ❌ FALHA ao mover para slot {slot}")

        time.sleep(1.5)

    _safe_print("\n🎯 TESTE 3: Voltar para centro")
    _safe_print("-" * 70)
    arduino.move_to(960, 540)
    time.sleep(1)

    _safe_print("\n" + "="*70)
    _safe_print("✅ TESTE COMPLETO!")
    _safe_print("="*70)
    _safe_print("\n📊 ANÁLISE:")
    _safe_print("   • Se o mouse se moveu: Arduino está funcionando corretamente")
    _safe_print("   • Se o mouse ficou parado: Problema no Arduino ou comunicação")
    _safe_print("   • Se o mouse foi para posições erradas: Problema de coordenadas")

    arduino.disconnect()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        _safe_print("\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        _safe_print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
