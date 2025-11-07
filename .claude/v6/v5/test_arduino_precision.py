"""
Script de teste de precisão do Arduino

Testa múltiplos pontos e calcula o fator de correção necessário
"""

import serial
import time
import pyautogui

# Configurar porta serial (ajuste COM10 se necessário)
SERIAL_PORT = 'COM10'
BAUD_RATE = 115200

# Pontos de teste (coordenadas importantes do jogo)
test_points = [
    (960, 540, "Centro da tela"),
    (709, 1005, "Slot 1"),
    (805, 1005, "Slot 2"),
    (1304, 577, "Vara no baú (exemplo)"),
    (1306, 858, "Isca no baú (exemplo)"),
    (0, 0, "Canto superior esquerdo"),
    (1920, 1080, "Canto inferior direito"),
]

print("=" * 70)
print("🎯 TESTE DE PRECISÃO DO ARDUINO")
print("=" * 70)

try:
    # Conectar ao Arduino
    print(f"\n📡 Conectando ao Arduino em {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    time.sleep(2)  # Aguardar reset do Arduino

    # Limpar buffer
    ser.reset_input_buffer()

    print("✅ Arduino conectado!\n")

    # Verificar conexão
    ser.write(b"PING\n")
    response = ser.readline().decode().strip()
    if response == "PONG":
        print("✅ Arduino respondeu: PONG\n")
    else:
        print(f"⚠️ Resposta inesperada: {response}\n")

    print("=" * 70)
    print("📋 INSTRUÇÕES:")
    print("1. Para cada ponto, o Arduino vai mover o mouse")
    print("2. Observe onde o mouse REALMENTE foi")
    print("3. Anote as coordenadas REAIS (use X-Mouse ou pyautogui)")
    print("=" * 70)

    input("\nPressione ENTER para iniciar os testes...")

    results = []

    for target_x, target_y, description in test_points:
        print(f"\n{'='*70}")
        print(f"🎯 TESTE: {description}")
        print(f"   Coordenada alvo: ({target_x}, {target_y})")
        print(f"{'='*70}")

        # Reset para centro
        print(f"   🔄 Resetando posição para centro (960, 540)...")
        ser.write(b"RESETPOS:960:540\n")
        time.sleep(0.5)

        # Ler resposta do reset
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:
                print(f"   [ARDUINO] {line}")

        # Mover para o alvo
        print(f"\n   ➡️ Movendo para ({target_x}, {target_y})...")
        command = f"MOUSEABS:{target_x}:{target_y}\n"
        ser.write(command.encode())

        # Aguardar movimento completar
        time.sleep(3)

        # Ler todas as respostas
        print(f"\n   📡 Respostas do Arduino:")
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:
                print(f"      {line}")

        # Ler posição REAL do mouse
        time.sleep(0.5)
        real_x, real_y = pyautogui.position()

        print(f"\n   ✅ RESULTADO:")
        print(f"      Alvo:  ({target_x}, {target_y})")
        print(f"      Real:  ({real_x}, {real_y})")
        print(f"      Erro X: {real_x - target_x} pixels")
        print(f"      Erro Y: {real_y - target_y} pixels")

        # Salvar resultado
        results.append({
            'description': description,
            'target': (target_x, target_y),
            'real': (real_x, real_y),
            'error': (real_x - target_x, real_y - target_y)
        })

        input(f"\n   Pressione ENTER para próximo teste...")

    # Calcular médias de erro
    print(f"\n{'='*70}")
    print("📊 ANÁLISE DE PRECISÃO")
    print(f"{'='*70}\n")

    total_error_x = sum(r['error'][0] for r in results)
    total_error_y = sum(r['error'][1] for r in results)
    avg_error_x = total_error_x / len(results)
    avg_error_y = total_error_y / len(results)

    print("📋 Resultados individuais:")
    for r in results:
        print(f"\n   {r['description']}:")
        print(f"      Alvo:  {r['target']}")
        print(f"      Real:  {r['real']}")
        print(f"      Erro:  {r['error']}")

    print(f"\n{'='*70}")
    print(f"📊 ERRO MÉDIO:")
    print(f"   X: {avg_error_x:.2f} pixels")
    print(f"   Y: {avg_error_y:.2f} pixels")
    print(f"{'='*70}\n")

    # Calcular fator de correção
    if avg_error_x != 0 or avg_error_y != 0:
        print("💡 SUGESTÃO DE CORREÇÃO:")
        print(f"\nAdicione no Arduino (linhas 41-42):")
        print(f"   #define CALIBRATION_OFFSET_X {int(-avg_error_x)}")
        print(f"   #define CALIBRATION_OFFSET_Y {int(-avg_error_y)}")
        print(f"\nIsso vai compensar o erro médio!")
    else:
        print("✅ Precisão perfeita! Não precisa de correção!")

    ser.close()

except serial.SerialException as e:
    print(f"\n❌ Erro ao conectar ao Arduino: {e}")
    print(f"   Verifique se a porta {SERIAL_PORT} está correta")
    print(f"   Use 'mode' no CMD para ver as portas COM disponíveis")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("✅ TESTE CONCLUÍDO!")
print(f"{'='*70}\n")
