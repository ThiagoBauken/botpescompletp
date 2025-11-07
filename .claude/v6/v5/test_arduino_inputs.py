#!/usr/bin/env python3
"""
🧪 Teste de Inputs do Arduino
Testa se Arduino está enviando teclas/mouse corretamente
"""

import serial
import time

def test_arduino():
    """Testar Arduino inputs"""
    print("="*60)
    print("🧪 TESTE DE INPUTS DO ARDUINO")
    print("="*60)

    # Conectar Arduino
    PORT = 'COM8'  # Ajuste se necessário
    print(f"\n📡 Conectando ao Arduino em {PORT}...")

    try:
        ser = serial.Serial(PORT, 115200, timeout=2)
        time.sleep(2)  # Aguardar inicialização

        # Limpar buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("✅ Conectado!")

        # Teste 1: PING
        print("\n" + "-"*60)
        print("📍 TESTE 1: PING")
        print("-"*60)
        ser.write(b'PING\n')
        response = ser.readline().decode().strip()
        print(f"Enviado: PING")
        print(f"Recebido: {response}")
        if response == "PONG":
            print("✅ PING-PONG funcionando!")
        else:
            print("❌ FALHA no PING-PONG")
            return

        # Teste 2: KEYDOWN ALT
        print("\n" + "-"*60)
        print("📍 TESTE 2: KEYDOWN ALT")
        print("-"*60)
        print("🔍 Abra o NOTEPAD agora e dê foco nele!")
        print("   Você tem 5 segundos...")
        for i in range(5, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        print("\n📤 Enviando: KEYDOWN:ALT")
        ser.write(b'KEYDOWN:ALT\n')
        response = ser.readline().decode().strip()
        print(f"📥 Recebido: {response}")

        time.sleep(2)

        print("\n📤 Enviando: KEYUP:ALT")
        ser.write(b'KEYUP:ALT\n')
        response = ser.readline().decode().strip()
        print(f"📥 Recebido: {response}")

        # Teste 3: KEYPRESS E
        print("\n" + "-"*60)
        print("📍 TESTE 3: KEYPRESS e")
        print("-"*60)
        print("🔍 O Notepad deve digitar 'eee'...")

        for i in range(3):
            print(f"\n📤 Enviando: KEYPRESS:e (tentativa {i+1})")
            ser.write(b'KEYPRESS:e\n')
            response = ser.readline().decode().strip()
            print(f"📥 Recebido: {response}")
            time.sleep(0.5)

        print("\n❓ Você viu 'eee' no Notepad?")

        # Teste 4: KEYPRESS TAB
        print("\n" + "-"*60)
        print("📍 TESTE 4: KEYPRESS TAB")
        print("-"*60)
        print("📤 Enviando: KEYPRESS:TAB")
        ser.write(b'KEYPRESS:TAB\n')
        response = ser.readline().decode().strip()
        print(f"📥 Recebido: {response}")

        # Teste 5: MOUSEABS
        print("\n" + "-"*60)
        print("📍 TESTE 5: MOUSEABS (movimento absoluto)")
        print("-"*60)
        print("🔍 O mouse deve pular para centro da tela...")

        print("\n📤 Enviando: MOUSEABS:960:540")
        ser.write(b'MOUSEABS:960:540\n')
        response = ser.readline().decode().strip()
        print(f"📥 Recebido: {response}")

        time.sleep(1)

        print("\n📤 Enviando: MOUSEABS:100:100")
        ser.write(b'MOUSEABS:100:100\n')
        response = ser.readline().decode().strip()
        print(f"📥 Recebido: {response}")

        print("\n❓ O mouse pulou para posições diferentes?")

        # Fechar conexão
        ser.close()

        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("="*60)

        print("\n📊 ANÁLISE:")
        print("   Se você viu:")
        print("   ✅ 'eee' no Notepad → Arduino está funcionando!")
        print("   ✅ Mouse pulando → MOUSEABS funciona!")
        print("")
        print("   Se NÃO viu:")
        print("   ❌ Arduino não está enviando inputs para Windows")
        print("   ❌ Problema pode ser:")
        print("      1. Sketch errado carregado")
        print("      2. Biblioteca HID-Project não instalada")
        print("      3. Arduino não é Pro Micro/Leonardo (precisa ATmega32U4)")

    except serial.SerialException as e:
        print(f"❌ Erro ao conectar: {e}")
        print(f"\n💡 Verifique:")
        print(f"   1. Porta COM correta? (Arduino IDE → Tools → Port)")
        print(f"   2. Arduino conectado?")
        print(f"   3. Drivers instalados?")

    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arduino()

    print("\n\n" + "="*60)
    input("Pressione ENTER para fechar...")
