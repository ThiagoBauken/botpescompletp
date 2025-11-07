"""
Teste Manual de Posicionamento Arduino

Este script testa se o Arduino está movendo o mouse para as posições corretas.
Útil para diagnosticar problemas de coordenadas.
"""

import sys
import time
import pyautogui

# Importar ArduinoInputManager
try:
    from core.arduino_input_manager import ArduinoInputManager
except ImportError:
    print("❌ Erro: Não foi possível importar ArduinoInputManager")
    print("   Certifique-se de estar executando no diretório correto")
    sys.exit(1)


def test_position(arduino, x, y, description):
    """
    Testa uma posição específica

    Args:
        arduino: Instância do ArduinoInputManager
        x, y: Coordenadas alvo
        description: Descrição do ponto

    Returns:
        bool: True se posição está correta (erro < 15 pixels)
    """
    print(f"\n{'='*70}")
    print(f"🎯 TESTE: {description}")
    print(f"   Coordenada alvo: ({x}, {y})")
    print(f"{'='*70}")

    input(f"   Pressione ENTER para mover para ({x}, {y})...")

    # Mover mouse
    print(f"   ➡️ Movendo...")
    success = arduino.move_to(x, y)

    if not success:
        print(f"   ❌ Falha ao enviar comando MOVE")
        return False

    # Aguardar movimento completar
    time.sleep(1.5)

    # Ler posição REAL do mouse
    real_x, real_y = pyautogui.position()

    # Calcular erro
    error_x = abs(real_x - x)
    error_y = abs(real_y - y)
    total_error = (error_x**2 + error_y**2)**0.5

    print(f"\n   📊 RESULTADO:")
    print(f"      Alvo:       ({x}, {y})")
    print(f"      Real:       ({real_x}, {real_y})")
    print(f"      Erro X:     {real_x - x:+d} pixels")
    print(f"      Erro Y:     {real_y - y:+d} pixels")
    print(f"      Erro total: {total_error:.1f} pixels")

    # Verificar se está dentro da tolerância
    if total_error < 15:
        print(f"   ✅ PRECISÃO BOA (erro < 15px)")
        return True
    elif total_error < 30:
        print(f"   ⚠️ PRECISÃO MÉDIA (erro < 30px) - pode funcionar mas recomenda-se ajuste")
        return True
    else:
        print(f"   ❌ PRECISÃO RUIM (erro > 30px) - PRECISA CORREÇÃO!")
        return False


def main():
    """Função principal do teste"""
    print("="*70)
    print("🧪 TESTE MANUAL DE POSICIONAMENTO ARDUINO")
    print("="*70)
    print()
    print("Este teste vai mover o mouse para várias posições importantes")
    print("do jogo e verificar se o Arduino está posicionando corretamente.")
    print()

    # Verificar resolução da tela
    screen_width, screen_height = pyautogui.size()
    print(f"📺 Resolução detectada: {screen_width}x{screen_height}")

    if screen_width != 1920 or screen_height != 1080:
        print(f"⚠️ ATENÇÃO: Resolução diferente de 1920x1080!")
        print(f"   O Arduino precisa ser reconfigurado para {screen_width}x{screen_height}")
        print(f"   Edite o arquivo Arduino e mude:")
        print(f"   #define SCREEN_WIDTH {screen_width}")
        print(f"   #define SCREEN_HEIGHT {screen_height}")
        print()
        continuar = input("Continuar mesmo assim? (s/n): ")
        if continuar.lower() != 's':
            return

    print()

    # Conectar ao Arduino
    print("📡 Conectando ao Arduino...")
    print("   (detectando porta automaticamente...)")
    print()

    arduino = ArduinoInputManager(baudrate=115200)

    if not arduino.connect():
        print()
        print("❌ Falha ao conectar ao Arduino!")
        print()
        print("Verifique:")
        print("   1. Arduino está conectado via USB")
        print("   2. Sketch arduino_hid_controller_HID.ino está carregado")
        print("   3. Driver do Arduino está instalado")
        print()
        return

    print("✅ Arduino conectado com sucesso!")
    print()

    # Aguardar antes de começar testes
    print("="*70)
    print("📋 INSTRUÇÕES:")
    print("   1. Abra o jogo em tela cheia (1920x1080)")
    print("   2. Para cada teste, observe onde o mouse vai")
    print("   3. O script vai comparar a posição real com a esperada")
    print("="*70)
    print()
    input("Pressione ENTER quando estiver pronto...")

    # Definir pontos de teste
    test_points = [
        (960, 540, "Centro da tela"),
        (709, 1005, "Slot 1 (vara inferior esquerda)"),
        (805, 1005, "Slot 2 (vara inferior centro-esquerda)"),
        (899, 1005, "Slot 3 (vara inferior centro)"),
        (992, 1005, "Slot 4 (vara inferior centro-direita)"),
        (1092, 1005, "Slot 5 (vara inferior direita)"),
        (1188, 1005, "Slot 6 (vara inferior extrema direita)"),
        (1350, 450, "Área de iscas no baú (exemplo)"),
        (1304, 577, "Área de varas no baú (exemplo)"),
    ]

    # Executar testes
    results = []
    for x, y, description in test_points:
        success = test_position(arduino, x, y, description)
        results.append({
            'description': description,
            'target': (x, y),
            'success': success
        })

        # Pequena pausa entre testes
        time.sleep(0.5)

    # Resumo final
    print(f"\n{'='*70}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*70}\n")

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"✅ Testes bem sucedidos: {successful}/{total}")
    print(f"❌ Testes com problema:  {total - successful}/{total}")
    print()

    if successful == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   Arduino está posicionando corretamente!")
        print("   ✅ Pronto para usar no bot!")
    elif successful >= total * 0.7:
        print("⚠️ MAIORIA DOS TESTES PASSOU")
        print("   Pode funcionar mas recomenda-se ajustar CorrectionFactor")
        print("   Edite arduino_hid_controller_HID.ino linha 83:")
        print("   MouseTo.setCorrectionFactor(0.97);  // Ajuste entre 0.95-1.05")
    else:
        print("❌ MUITOS TESTES FALHARAM!")
        print()
        print("Possíveis causas:")
        print("   1. Conversão de coordenadas incorreta (int16_t vs uint16_t)")
        print("   2. Range errado (-32768,32767 vs 0,32767)")
        print("   3. Resolução da tela diferente de 1920x1080")
        print("   4. CorrectionFactor muito longe de 1.0")
        print()
        print("Leia DIAGNOSTICO_PROBLEMA_MOUSE_ARDUINO.md para detalhes!")

    # Limpar
    print()
    print("🔌 Desconectando Arduino...")
    arduino.cleanup()

    print()
    print("="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
