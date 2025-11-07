#!/usr/bin/env python3
"""
🔍 TESTE: Qual Arduino está sendo usado?

Este script testa:
1. Conecta ao Arduino
2. Envia PING
3. Envia RESET_POS:959:539
4. Verifica resposta para identificar MouseTo ou AbsMouse
"""

import serial
import serial.tools.list_ports
import time

def _safe_print(text):
    try:
        print(text)
    except:
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def find_arduino():
    """Encontrar porta COM do Arduino"""
    _safe_print("🔍 Procurando Arduino...")
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.vid in [0x2341, 0x1B4F, 0x2A03]:
            _safe_print(f"✅ Arduino encontrado: {port.device}")
            return port.device

    _safe_print("❌ Arduino não encontrado!")
    _safe_print("\n📋 Portas disponíveis:")
    for port in ports:
        _safe_print(f"   {port.device}: {port.description}")
    return None

def main():
    _safe_print("="*60)
    _safe_print("🔍 TESTE: Identificar Qual Arduino Está Sendo Usado")
    _safe_print("="*60)

    # Encontrar Arduino
    port = find_arduino()
    if not port:
        input("\nPressione Enter para sair...")
        return

    try:
        # Conectar
        _safe_print(f"\n📡 Conectando em {port}...")
        ser = serial.Serial(port, 115200, timeout=2.0)
        time.sleep(2.5)  # Aguardar reset

        # Limpar buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Aguardar READY
        _safe_print("⏳ Aguardando mensagem READY...")
        ready_msg = ""
        for _ in range(10):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                _safe_print(f"   📥 Arduino: {line}")
                if "READY" in line:
                    ready_msg = line
                    break
            time.sleep(0.1)

        # TESTE 1: PING
        _safe_print("\n" + "="*60)
        _safe_print("TESTE 1: PING")
        _safe_print("="*60)
        ser.write(b"PING\n")
        ser.flush()
        time.sleep(0.1)
        response = ser.readline().decode('utf-8').strip()
        _safe_print(f"📤 Enviado: PING")
        _safe_print(f"📥 Resposta: {response}")

        if response != "PONG":
            _safe_print("❌ Arduino não respondeu corretamente!")
            return

        # TESTE 2: RESET_POS
        _safe_print("\n" + "="*60)
        _safe_print("TESTE 2: RESET_POS:959:539")
        _safe_print("="*60)
        ser.write(b"RESET_POS:959:539\n")
        ser.flush()
        time.sleep(0.2)
        response = ser.readline().decode('utf-8').strip()
        _safe_print(f"📤 Enviado: RESET_POS:959:539")
        _safe_print(f"📥 Resposta: {response}")

        # Analisar resposta
        _safe_print("\n" + "="*60)
        _safe_print("📊 ANÁLISE:")
        _safe_print("="*60)

        # Detectar pela mensagem READY
        if "READY:AbsMouse" in ready_msg:
            _safe_print("✅ DETECTADO: AbsMouse (Standalone)")
            _safe_print("   📡 Firmware: READY:AbsMouse")
        elif "READY:HID-Project" in ready_msg:
            _safe_print("✅ DETECTADO: HID-Project (AbsoluteMouse)")
            _safe_print("   📡 Firmware: READY:HID-Project")
        else:
            _safe_print("⚠️ DETECTADO: MouseTo (versão antiga)")
            _safe_print("   📡 Firmware: READY (sem identificador)")

        # Detectar também pela resposta RESET_POS
        if ":NOT_NEEDED" in response:
            _safe_print("   ℹ️  Resposta RESET_POS contém ':NOT_NEEDED'")
            _safe_print("   ✅ Posicionamento absoluto (sem estado interno)!")
            _safe_print("   ✅ Movimentos devem funcionar perfeitamente!")
        elif "OK:RESET_POS" in response:
            _safe_print("   ℹ️  Resposta RESET_POS é apenas 'OK:RESET_POS'")
            _safe_print("   ❌ MouseTo TEM estado interno!")
            _safe_print("   ❌ Este é o problema que causa mouse ir para canto!")
            _safe_print("\n🚨 SOLUÇÃO: Usar AbsMouse ou HID-Project!")
            _safe_print("   📋 Opção 1: GUIA_INSTALACAO_ABSMOUSE.md")
            _safe_print("   📋 Opção 2: arduino_hid_controller_HID_PROJECT_SOLUTION.ino")
        else:
            _safe_print("   ❓ RESPOSTA DESCONHECIDA!")
            _safe_print(f"   Resposta: {response}")

        # TESTE 3: MOVE
        _safe_print("\n" + "="*60)
        _safe_print("TESTE 3: MOVE:1350:750")
        _safe_print("="*60)
        _safe_print("⚠️ ATENÇÃO: O mouse VAI MOVER AGORA!")
        _safe_print("   Você tem 5 segundos para posicionar a janela do jogo...")
        for i in range(5, 0, -1):
            _safe_print(f"   {i}...")
            time.sleep(1)

        ser.write(b"MOVE:1350:750\n")
        ser.flush()
        _safe_print(f"📤 Enviado: MOVE:1350:750")

        # Aguardar resposta (pode demorar se MouseTo)
        time.sleep(2.0)

        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            _safe_print(f"📥 Resposta: {response}")
        else:
            _safe_print("⚠️ Sem resposta (ainda processando...)")
            time.sleep(2.0)
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                _safe_print(f"📥 Resposta (atrasada): {response}")

        # Verificar posição real do mouse
        try:
            import pyautogui
            actual_x, actual_y = pyautogui.position()
            _safe_print(f"\n🔍 Verificação:")
            _safe_print(f"   Esperado: (1350, 750)")
            _safe_print(f"   Real: ({actual_x}, {actual_y})")
            error_x = 1350 - actual_x
            error_y = 750 - actual_y
            _safe_print(f"   Erro: ({error_x:+d}, {error_y:+d})")

            if abs(error_x) < 10 and abs(error_y) < 10:
                _safe_print("\n✅ MOVIMENTO PERFEITO!")
            elif abs(error_x) > 100 or abs(error_y) > 100:
                _safe_print("\n❌ ERRO GRANDE! Mouse foi para lugar errado!")
                _safe_print("   🚨 CONFIRMA: Problema do MouseTo!")
                _safe_print("   📋 SOLUÇÃO: Instalar AbsMouse!")
            else:
                _safe_print("\n⚠️ Pequeno erro (aceitável)")
        except:
            _safe_print("\n⚠️ PyAutoGUI não disponível para verificar posição")

        ser.close()

        _safe_print("\n" + "="*60)
        _safe_print("✅ TESTE CONCLUÍDO!")
        _safe_print("="*60)

    except Exception as e:
        _safe_print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
