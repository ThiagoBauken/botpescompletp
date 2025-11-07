"""
Teste Manual Simplificado - Arduino
"""
import sys
sys.path.insert(0, r'C:\Users\Thiago\Desktop\v5')

from core.arduino_input_manager import ArduinoInputManager
import time

print("="*60)
print("🧪 TESTE MANUAL ARDUINO")
print("="*60)

# Criar conexão
arduino = ArduinoInputManager()

if not arduino.connected:
    print("\n❌ FALHA: Arduino não conectado!")
    print("Verifique:")
    print("  1. Arduino conectado via USB")
    print("  2. Sketch carregado")
    print("  3. Porta COM correta")
    exit(1)

print("\n✅ Arduino conectado com sucesso!\n")

# Teste 1: PING
print("📡 Teste 1: PING/PONG")
response = arduino._send_command("PING")
print(f"   Resposta: {response}")
if response == "PONG":
    print("   ✅ PASSOU!\n")
else:
    print("   ❌ FALHOU!\n")

# Teste 2: Pressionar tecla (em 2 segundos)
print("⌨️ Teste 2: Pressionar tecla '1' em 2 segundos...")
time.sleep(2)
response = arduino._send_command("KEYPRESS:1")
print(f"   Resposta: {response}")
if response and response.startswith("OK"):
    print("   ✅ PASSOU!\n")
else:
    print("   ❌ FALHOU!\n")

# Teste 3: Click esquerdo (em 2 segundos)
print("🖱️ Teste 3: Click esquerdo em 2 segundos...")
time.sleep(2)
response = arduino._send_command("MOUSECLICK:L")
print(f"   Resposta: {response}")
if response and response.startswith("OK"):
    print("   ✅ PASSOU!\n")
else:
    print("   ❌ FALHOU!\n")

# Teste 4: Movimento de mouse (em 1 segundo)
print("🖱️ Teste 4: Movimento de mouse em 1 segundo...")
time.sleep(1)
response = arduino._send_command("MOUSEMOVE:50:50")
print(f"   Resposta: {response}")
if response and response.startswith("OK"):
    print("   ✅ PASSOU!\n")
else:
    print("   ❌ FALHOU!\n")

print("="*60)
print("✅ TESTE CONCLUÍDO!")
print("="*60)

arduino.cleanup()
