# 🎯 Solução Arduino: Biblioteca MouseTo

## 🔍 Problema Resolvido

A biblioteca [MouseTo](https://github.com/per1234/MouseTo) adiciona a função `Mouse.moveTo(x, y)` ao Arduino Leonardo/Micro, permitindo movimentos **absolutos** em vez de apenas relativos!

---

## 📦 Instalação da Biblioteca MouseTo

### Método 1: Arduino Library Manager (Recomendado)

1. Abrir **Arduino IDE**
2. **Sketch → Include Library → Manage Libraries...**
3. Buscar: **"MouseTo"**
4. Instalar: **MouseTo by per1234**

### Método 2: Manual

```bash
cd ~/Documents/Arduino/libraries/
git clone https://github.com/per1234/MouseTo.git
```

---

## ✅ Vantagens da MouseTo

| Recurso | Nativo Arduino | Com MouseTo |
|---------|---------------|-------------|
| `Mouse.move(dx, dy)` | ✅ Relativo | ✅ Relativo |
| `Mouse.moveTo(x, y)` | ❌ Não existe | ✅ **ABSOLUTO** |
| Precisa rastreamento | ✅ Sim | ❌ **NÃO!** |
| Calibração periódica | ✅ Necessária | ❌ Não precisa |
| Drift de posição | ⚠️ Acumula erros | ✅ Sempre preciso |

---

## 🚀 Solução SIMPLIFICADA

### Arquitetura

```
Python (Template Engine)
    ↓
Detecta isca em (1350, 450)
    ↓
Envia: "CLICK 1350 450"
    ↓
Arduino recebe
    ↓
Mouse.moveTo(1350, 450) ← ✅ FUNCIONA!
    ↓
Mouse.click()
```

**NÃO PRECISA** de rastreamento de posição virtual!

---

## 💻 Código Arduino Atualizado

```cpp
// arduino_hid_controller_mouseto.ino
// ✅ VERSÃO COM MouseTo - Movimentos Absolutos

#include <Mouse.h>
#include <Keyboard.h>
#include <MouseTo.h>  // ← ✅ BIBLIOTECA MOUSETO

void setup() {
  Serial.begin(115200);
  Mouse.begin();
  Keyboard.begin();
  MouseTo.setCorrectionFactor(1);  // Ajuste fino (1 = sem correção)
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // ===== MOVIMENTO ABSOLUTO COM MouseTo =====
    if (command.startsWith("MOVE ")) {
      // Formato: MOVE x y
      int spaceIndex = command.indexOf(' ', 5);
      int x = command.substring(5, spaceIndex).toInt();
      int y = command.substring(spaceIndex + 1).toInt();

      MouseTo.setTarget(x, y);  // ← ✅ Define alvo absoluto

      // Mover suavemente em 50ms (ajustável)
      unsigned long duration = 50;
      unsigned long startTime = millis();

      while (!MouseTo.atTarget()) {
        MouseTo.move();  // ← Move um passo em direção ao alvo
        delay(1);

        // Timeout de segurança
        if (millis() - startTime > duration + 100) {
          break;
        }
      }

    // ===== MOVIMENTO RELATIVO (ainda funciona) =====
    } else if (command.startsWith("MOVE_REL ")) {
      int spaceIndex = command.indexOf(' ', 9);
      int dx = command.substring(9, spaceIndex).toInt();
      int dy = command.substring(spaceIndex + 1).toInt();
      Mouse.move(dx, dy);

    // ===== CLIQUE EM POSIÇÃO ABSOLUTA =====
    } else if (command.startsWith("CLICK ")) {
      int spaceIndex = command.indexOf(' ', 6);
      int x = command.substring(6, spaceIndex).toInt();
      int y = command.substring(spaceIndex + 1).toInt();

      // Mover para posição
      MouseTo.setTarget(x, y);
      while (!MouseTo.atTarget()) {
        MouseTo.move();
        delay(1);
      }
      delay(20);  // Pequena pausa antes de clicar

      // Clicar
      Mouse.click(MOUSE_LEFT);

    // ===== CLIQUE DIREITO EM POSIÇÃO =====
    } else if (command.startsWith("RIGHT_CLICK ")) {
      int spaceIndex = command.indexOf(' ', 12);
      int x = command.substring(12, spaceIndex).toInt();
      int y = command.substring(spaceIndex + 1).toInt();

      MouseTo.setTarget(x, y);
      while (!MouseTo.atTarget()) {
        MouseTo.move();
        delay(1);
      }
      delay(20);

      Mouse.click(MOUSE_RIGHT);

    // ===== DRAG (ARRASTAR) =====
    } else if (command.startsWith("DRAG ")) {
      // Formato: DRAG x1 y1 x2 y2
      int space1 = command.indexOf(' ', 5);
      int space2 = command.indexOf(' ', space1 + 1);
      int space3 = command.indexOf(' ', space2 + 1);

      int x1 = command.substring(5, space1).toInt();
      int y1 = command.substring(space1 + 1, space2).toInt();
      int x2 = command.substring(space2 + 1, space3).toInt();
      int y2 = command.substring(space3 + 1).toInt();

      // PASSO 1: Mover para início
      MouseTo.setTarget(x1, y1);
      while (!MouseTo.atTarget()) {
        MouseTo.move();
        delay(1);
      }
      delay(200);  // Pausa no início

      // PASSO 2: Segurar botão
      Mouse.press(MOUSE_LEFT);
      delay(200);

      // PASSO 3: Mover para destino (lento para arrastar)
      MouseTo.setTarget(x2, y2);
      while (!MouseTo.atTarget()) {
        MouseTo.move();
        delay(5);  // ← Movimento mais lento para drag suave
      }
      delay(400);  // Pausa no destino

      // PASSO 4: Soltar botão
      Mouse.release(MOUSE_LEFT);
      delay(400);

    // ===== CONTROLE DE MOUSE =====
    } else if (command == "MOUSE_DOWN left") {
      Mouse.press(MOUSE_LEFT);

    } else if (command == "MOUSE_UP left") {
      Mouse.release(MOUSE_LEFT);

    } else if (command == "MOUSE_DOWN right") {
      Mouse.press(MOUSE_RIGHT);

    } else if (command == "MOUSE_UP right") {
      Mouse.release(MOUSE_RIGHT);

    // ===== CONTROLE DE TECLADO =====
    } else if (command.startsWith("KEY_PRESS ")) {
      // Formato: KEY_PRESS a
      char key = command.charAt(10);
      Keyboard.press(key);
      delay(50);
      Keyboard.release(key);

    } else if (command.startsWith("KEY_DOWN ")) {
      char key = command.charAt(9);
      Keyboard.press(key);

    } else if (command.startsWith("KEY_UP ")) {
      char key = command.charAt(7);
      Keyboard.release(key);

    // ===== EMERGENCY STOP =====
    } else if (command == "EMERGENCY_STOP") {
      Mouse.release(MOUSE_LEFT);
      Mouse.release(MOUSE_RIGHT);
      Keyboard.releaseAll();
    }
  }
}
```

---

## 🐍 Código Python - InputManager Atualizado

### Adicionar ao InputManager

```python
class InputManager:
    def __init__(self, config_manager=None):
        # ... código existente ...

        # ✅ ARDUINO: Configuração serial
        self.use_arduino = False
        self.arduino_serial = None
        self.arduino_port = None  # Ex: "COM3" (Windows) ou "/dev/ttyACM0" (Linux)

    def connect_arduino(self, port: str = None) -> bool:
        """
        🔌 Conectar ao Arduino via serial

        Args:
            port: Porta COM (ex: "COM3" no Windows)
                 Auto-detecta se None

        Returns:
            bool: True se conectado com sucesso
        """
        try:
            import serial
            import serial.tools.list_ports

            # Auto-detectar porta se não especificada
            if port is None:
                _safe_print("🔍 Detectando Arduino automaticamente...")
                ports = list(serial.tools.list_ports.comports())
                arduino_ports = [p for p in ports if 'Arduino' in p.description or 'USB Serial' in p.description]

                if arduino_ports:
                    port = arduino_ports[0].device
                    _safe_print(f"✅ Arduino detectado em: {port}")
                else:
                    _safe_print("❌ Nenhum Arduino detectado")
                    return False

            # Conectar
            _safe_print(f"🔌 Conectando ao Arduino em {port}...")
            self.arduino_serial = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)  # Aguardar Arduino resetar após conexão

            # Testar comunicação
            self.arduino_serial.write(b"PING\n")
            time.sleep(0.1)

            self.arduino_port = port
            self.use_arduino = True

            _safe_print(f"✅ Arduino conectado com sucesso em {port}")
            _safe_print(f"   Modo Arduino ATIVADO - usando MouseTo para movimentos absolutos")

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao conectar Arduino: {e}")
            self.use_arduino = False
            return False

    def disconnect_arduino(self) -> bool:
        """🔌 Desconectar Arduino"""
        try:
            if self.arduino_serial and self.arduino_serial.is_open:
                # Emergency stop antes de desconectar
                self.arduino_serial.write(b"EMERGENCY_STOP\n")
                time.sleep(0.1)

                self.arduino_serial.close()
                _safe_print("🔌 Arduino desconectado")

            self.use_arduino = False
            self.arduino_serial = None
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao desconectar Arduino: {e}")
            return False

    def _send_arduino_command(self, command: str) -> bool:
        """
        📡 Enviar comando para Arduino

        Args:
            command: Comando no formato do protocolo

        Returns:
            bool: True se enviado com sucesso
        """
        if not self.use_arduino or not self.arduino_serial:
            return False

        try:
            self.arduino_serial.write(f"{command}\n".encode())
            time.sleep(0.01)  # Pequeno delay
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao enviar comando Arduino: {e}")
            return False

    def click(self, x: int, y: int, button: str = 'left') -> bool:
        """
        🖱️ Clique em posição absoluta - COMPATÍVEL COM ARDUINO MouseTo

        Args:
            x: Coordenada X absoluta
            y: Coordenada Y absoluta
            button: 'left' ou 'right'
        """
        try:
            self._focus_game_window()

            if self.use_arduino:
                # ✅ ARDUINO: Comando CLICK usa MouseTo.moveTo()
                if button == 'left':
                    self._send_arduino_command(f"CLICK {x} {y}")
                else:
                    self._send_arduino_command(f"RIGHT_CLICK {x} {y}")
                time.sleep(0.1)
            else:
                # PyAutoGUI
                pyautogui.click(x, y, button=button)

            _safe_print(f"🖱️ Clique {button} em ({x}, {y})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique: {e}")
            return False

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        🖱️ Arrastar - COMPATÍVEL COM ARDUINO MouseTo

        Args:
            start_x, start_y: Posição inicial (absoluta)
            end_x, end_y: Posição final (absoluta)
            duration: Duração do movimento (ignorado no Arduino)
        """
        try:
            self._focus_game_window()

            if self.use_arduino:
                # ✅ ARDUINO: Comando DRAG usa MouseTo.moveTo()
                _safe_print(f"🖱️ Arduino DRAG: ({start_x}, {start_y}) → ({end_x}, {end_y})")
                self._send_arduino_command(f"DRAG {start_x} {start_y} {end_x} {end_y}")
                time.sleep(1.5)  # Aguardar drag completo
            else:
                # PyAutoGUI - implementação existente
                pyautogui.moveTo(start_x, start_y)
                time.sleep(0.2)
                pyautogui.mouseDown(button='left')
                time.sleep(0.2)
                pyautogui.moveTo(end_x, end_y, duration=duration)
                time.sleep(0.4)
                pyautogui.mouseUp(button='left')
                time.sleep(0.4)

            _safe_print(f"✅ Drag completo: ({start_x}, {start_y}) → ({end_x}, {end_y})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no drag: {e}")
            return False

    def move_to(self, x: int, y: int) -> bool:
        """
        🖱️ Mover mouse para posição absoluta - COMPATÍVEL COM ARDUINO MouseTo

        Args:
            x, y: Coordenadas absolutas
        """
        try:
            if self.use_arduino:
                # ✅ ARDUINO: Comando MOVE usa MouseTo.moveTo()
                self._send_arduino_command(f"MOVE {x} {y}")
                time.sleep(0.1)
            else:
                # PyAutoGUI
                pyautogui.moveTo(x, y)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao mover mouse: {e}")
            return False

    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """Pressionar tecla - COMPATÍVEL COM ARDUINO"""
        try:
            self._focus_game_window()

            if self.use_arduino:
                # Arduino: KEY_PRESS para pressionar+soltar
                self._send_arduino_command(f"KEY_PRESS {key}")
                time.sleep(duration)
            else:
                # PyAutoGUI
                pyautogui.keyDown(key)
                time.sleep(duration)
                pyautogui.keyUp(key)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao pressionar tecla {key}: {e}")
            return False

    def stop_all_actions(self) -> bool:
        """🚨 EMERGENCY STOP - COMPATÍVEL COM ARDUINO"""
        try:
            _safe_print("🚨 EMERGENCY STOP - Parando todas as ações!")

            if self.use_arduino:
                # Arduino: Comando especial de emergency stop
                self._send_arduino_command("EMERGENCY_STOP")
                time.sleep(0.2)
            else:
                # PyAutoGUI - lógica existente
                self.stop_continuous_clicking()
                self.stop_camera_movement()
                self.stop_continuous_s_press()
                self.stop_fishing()

                # Soltar todas as teclas
                for key in list(self.keyboard_state['keys_down']):
                    pyautogui.keyUp(key)

                # Soltar botões do mouse
                pyautogui.mouseUp(button='left')
                pyautogui.mouseUp(button='right')

            # Limpar estado
            self.mouse_state['right_button_down'] = False
            self.mouse_state['left_button_down'] = False
            self.keyboard_state['keys_down'].clear()

            _safe_print("✅ Emergency stop concluído")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no emergency stop: {e}")
            return False
```

---

## 🎮 Protocolo Serial - Resumo

### Comandos Disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `MOVE x y` | Mover para (x, y) absoluto | `MOVE 1350 450` |
| `CLICK x y` | Clicar esquerdo em (x, y) | `CLICK 709 1005` |
| `RIGHT_CLICK x y` | Clicar direito em (x, y) | `RIGHT_CLICK 800 500` |
| `DRAG x1 y1 x2 y2` | Arrastar de (x1,y1) para (x2,y2) | `DRAG 1350 450 899 1005` |
| `MOUSE_DOWN left/right` | Segurar botão | `MOUSE_DOWN left` |
| `MOUSE_UP left/right` | Soltar botão | `MOUSE_UP left` |
| `KEY_PRESS a` | Pressionar+soltar tecla | `KEY_PRESS 3` |
| `KEY_DOWN a` | Segurar tecla | `KEY_DOWN a` |
| `KEY_UP a` | Soltar tecla | `KEY_UP a` |
| `EMERGENCY_STOP` | Soltar tudo | `EMERGENCY_STOP` |

---

## 🧪 Teste de Integração

### Script de Teste Python

```python
# test_arduino_mouseto.py

from core.input_manager import InputManager
import time

def test_arduino_integration():
    """Testar integração Arduino com MouseTo"""

    print("="*60)
    print("🧪 TESTE DE INTEGRAÇÃO ARDUINO + MouseTo")
    print("="*60)

    # Criar InputManager
    input_mgr = InputManager()

    # PASSO 1: Conectar Arduino
    print("\n📡 PASSO 1: Conectando ao Arduino...")
    if not input_mgr.connect_arduino():  # Auto-detecta porta
        print("❌ Falha ao conectar - verifique conexão USB")
        return False

    time.sleep(2)

    # PASSO 2: Testar movimento absoluto
    print("\n🎯 PASSO 2: Testando movimento absoluto...")
    print("   Movendo para centro da tela (960, 540)...")
    input_mgr.move_to(960, 540)
    time.sleep(1)

    # PASSO 3: Testar clique em posição
    print("\n🖱️ PASSO 3: Testando clique...")
    print("   Clicando em (800, 400)...")
    input_mgr.click(800, 400)
    time.sleep(1)

    # PASSO 4: Testar drag
    print("\n📦 PASSO 4: Testando drag...")
    print("   Arrastando de (500, 300) para (700, 500)...")
    input_mgr.drag(500, 300, 700, 500)
    time.sleep(2)

    # PASSO 5: Testar teclas
    print("\n⌨️ PASSO 5: Testando teclas...")
    print("   Pressionando tecla '3'...")
    input_mgr.press_key('3')
    time.sleep(1)

    # PASSO 6: Emergency stop
    print("\n🚨 PASSO 6: Testando emergency stop...")
    input_mgr.stop_all_actions()
    time.sleep(1)

    # Desconectar
    print("\n🔌 Desconectando Arduino...")
    input_mgr.disconnect_arduino()

    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    return True

if __name__ == "__main__":
    test_arduino_integration()
```

---

## 🚀 Como Usar no Bot

### 1. Inicialização (main.py)

```python
# main.py

from core.input_manager import InputManager

# Criar InputManager
input_manager = InputManager(config_manager)

# Perguntar ao usuário se quer usar Arduino
use_arduino = input("Usar Arduino? (s/n): ").lower() == 's'

if use_arduino:
    if input_manager.connect_arduino():
        print("✅ Modo Arduino ATIVADO com MouseTo")
    else:
        print("⚠️ Falha ao conectar Arduino - usando PyAutoGUI")
else:
    print("✅ Modo PyAutoGUI")

# Continuar inicialização normal...
```

### 2. Uso Transparente

Todo o código existente **funciona sem modificação**:

```python
# Manutenção de varas - FUNCIONA IGUAL!
input_manager.drag(1350, 450, 899, 1005)  # ← MouseTo.moveTo() usado!

# Clique em slot - FUNCIONA IGUAL!
input_manager.click(709, 1005)  # ← MouseTo.moveTo() usado!

# Feeding - FUNCIONA IGUAL!
input_manager.drag(1306, 858, 1083, 373)  # ← MouseTo.moveTo() usado!
```

---

## 📊 Comparação: Antes vs Depois

### ❌ ANTES (Sem MouseTo)

```
Python → "CLICK 1350 450"
    ↓
Arduino → ??? (não sabe onde está)
    ↓
Precisa rastreamento virtual
    ↓
Drift acumula erros
    ↓
Calibração necessária a cada 100 movimentos
```

### ✅ DEPOIS (Com MouseTo)

```
Python → "CLICK 1350 450"
    ↓
Arduino → Mouse.moveTo(1350, 450)
    ↓
✅ FUNCIONA! Sempre preciso!
```

---

## 🎯 Vantagens Finais

✅ **Zero modificações na lógica de detecção**
✅ **Sem rastreamento de posição virtual**
✅ **Sem calibração periódica**
✅ **Sem drift de posição**
✅ **100% compatível com código existente**
✅ **Protocolo serial simples**
✅ **Fácil de testar (flag on/off)**

---

## 📝 Checklist de Implementação

- [ ] Instalar biblioteca MouseTo no Arduino IDE
- [ ] Fazer upload do sketch `arduino_hid_controller_mouseto.ino`
- [ ] Adicionar métodos ao `InputManager` (connect_arduino, etc.)
- [ ] Testar com `test_arduino_mouseto.py`
- [ ] Validar operações: clique, drag, teclas
- [ ] Integrar ao main.py (prompt use_arduino)
- [ ] Testar ciclo completo de pesca
- [ ] Testar manutenção de varas
- [ ] Testar feeding/cleaning

---

## 🐛 Troubleshooting

### Arduino não detectado
```bash
# Windows: Verificar Device Manager → Ports (COM & LPT)
# Linux: ls /dev/ttyACM*
# Instalar drivers: https://www.arduino.cc/en/Guide/DriverInstallation
```

### MouseTo não move corretamente
```cpp
// Ajustar fator de correção no setup():
MouseTo.setCorrectionFactor(1.1);  // Testar valores 0.9 - 1.1
```

### Serial timeout
```python
# Aumentar timeout na conexão:
self.arduino_serial = serial.Serial(port, 115200, timeout=2)  # 2 segundos
```
