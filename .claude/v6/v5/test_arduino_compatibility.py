"""
Teste de Compatibilidade - ArduinoInputManager vs InputManager

Este script compara os métodos disponíveis em ambas as classes
para garantir 100% de compatibilidade.
"""

import inspect
from core.input_manager import InputManager
from core.arduino_input_manager import ArduinoInputManager


def get_public_methods(cls):
    """Obter todos os métodos públicos de uma classe"""
    methods = set()
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):  # Ignorar métodos privados
            methods.add(name)
    return methods


def compare_interfaces():
    """Comparar interfaces das duas classes"""
    print("="*70)
    print("TESTE DE COMPATIBILIDADE: ArduinoInputManager vs InputManager")
    print("="*70)
    print()

    # Obter métodos de cada classe
    input_methods = get_public_methods(InputManager)
    arduino_methods = get_public_methods(ArduinoInputManager)

    # Métodos no InputManager mas não no ArduinoInputManager
    missing_in_arduino = input_methods - arduino_methods

    # Métodos no ArduinoInputManager mas não no InputManager
    extra_in_arduino = arduino_methods - input_methods

    # Métodos em comum
    common_methods = input_methods & arduino_methods

    print(f"📊 ESTATÍSTICAS:")
    print(f"   - Métodos no InputManager:         {len(input_methods)}")
    print(f"   - Métodos no ArduinoInputManager:  {len(arduino_methods)}")
    print(f"   - Métodos em comum:                {len(common_methods)}")
    print()

    # Mostrar métodos faltantes (se houver)
    if missing_in_arduino:
        print(f"❌ MÉTODOS FALTANDO NO ARDUINO ({len(missing_in_arduino)}):")
        for method in sorted(missing_in_arduino):
            print(f"   - {method}()")
        print()
    else:
        print("✅ TODOS os métodos do InputManager estão no ArduinoInputManager!")
        print()

    # Mostrar métodos extras (informativo)
    if extra_in_arduino:
        print(f"ℹ️  MÉTODOS EXTRAS NO ARDUINO ({len(extra_in_arduino)}):")
        for method in sorted(extra_in_arduino):
            print(f"   - {method}()")
        print()

    # Lista de métodos críticos que DEVEM estar implementados
    critical_methods = [
        'press_key', 'key_down', 'key_up',
        'click', 'click_left', 'click_right', 'right_click',
        'mouse_down', 'mouse_up',
        'move_to', 'move_mouse', 'drag',
        'start_fishing', 'stop_fishing', 'catch_fish',
        'move_camera_a', 'move_camera_d', 'camera_turn_in_game', 'center_camera',
        'start_continuous_clicking', 'stop_continuous_clicking',
        'start_camera_movement_cycle', 'stop_camera_movement',
        'capture_initial_position', 'release_mouse_buttons',
        'stop_all_actions', 'emergency_stop',
        'get_state', 'set_callbacks', 'get_click_delay', 'reload_timing_config'
    ]

    print(f"🔍 VERIFICAÇÃO DE MÉTODOS CRÍTICOS ({len(critical_methods)}):")
    all_critical_present = True
    for method in critical_methods:
        if method in arduino_methods:
            print(f"   ✅ {method}()")
        else:
            print(f"   ❌ {method}() - FALTANDO!")
            all_critical_present = False

    print()
    print("="*70)

    if not missing_in_arduino and all_critical_present:
        print("✅ COMPATIBILIDADE 100% - Arduino pode substituir InputManager!")
        print("="*70)
        return True
    else:
        print("❌ INCOMPATIBILIDADE DETECTADA - Ajustes necessários!")
        print("="*70)
        return False


def test_method_signatures():
    """Testar se as assinaturas dos métodos críticos são compatíveis"""
    print("\n🔬 TESTE DE ASSINATURAS DE MÉTODOS:")
    print("="*70)

    critical_methods = ['drag', 'move_to', 'click', 'start_continuous_clicking']

    for method_name in critical_methods:
        if hasattr(InputManager, method_name) and hasattr(ArduinoInputManager, method_name):
            input_sig = inspect.signature(getattr(InputManager, method_name))
            arduino_sig = inspect.signature(getattr(ArduinoInputManager, method_name))

            print(f"\n{method_name}:")
            print(f"   InputManager:        {input_sig}")
            print(f"   ArduinoInputManager: {arduino_sig}")

            if str(input_sig) == str(arduino_sig):
                print(f"   ✅ Assinaturas idênticas")
            else:
                print(f"   ⚠️ Assinaturas diferentes (pode ser OK se compatível)")

    print("\n" + "="*70)


if __name__ == "__main__":
    # Executar testes
    compatible = compare_interfaces()

    # Testar assinaturas
    test_method_signatures()

    # Resultado final
    print("\n" + "="*70)
    if compatible:
        print("✅ RESULTADO: ArduinoInputManager está 100% compatível!")
        print("   Pode ser usado como drop-in replacement para InputManager")
    else:
        print("❌ RESULTADO: Ajustes necessários antes de usar em produção")

    print("="*70)
