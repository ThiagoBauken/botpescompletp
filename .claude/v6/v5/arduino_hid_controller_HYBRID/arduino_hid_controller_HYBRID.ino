/*
 * ============================================================================
 * 🎮 ULTIMATE FISHING BOT - ARDUINO HID CONTROLLER v5.3 - HYBRID FIX
 * ============================================================================
 *
 * ✅ SOLUÇÃO HÍBRIDA: AbsoluteMouse (HID-Project) + Keyboard.h (Nativo)
 *
 * BIBLIOTECAS USADAS:
 * - HID-Project: AbsoluteMouse (movimento absoluto) + Mouse (movimento relativo)
 * - Keyboard.h: Teclado NATIVO do Arduino (sem conflitos!)
 *
 * POR QUÊ ESSA COMBINAÇÃO?
 * - AbsoluteMouse do HID-Project: Movimento preciso do mouse
 * - Keyboard.h nativo: Compatibilidade perfeita, sem conflitos HID
 * - Usuário confirmou que "funcionava mouse e keyboard ao mesmo tempo"
 *
 * INSTALAÇÃO:
 * 1. Arduino IDE → Tools → Manage Libraries
 * 2. Buscar: "HID-Project"
 * 3. Instalar: "HID-Project by NicoHood"
 * 4. Upload deste sketch (Keyboard.h já é nativo, não precisa instalar)
 *
 * ============================================================================
 */

#include <HID-Project.h>   // Para AbsoluteMouse e Mouse (movimento relativo)
#include <HID-Settings.h>
#include <Keyboard.h>      // ← NATIVO! Sem conflitos com mouse

// ============================================================================
// CONFIGURAÇÕES
// ============================================================================

#define SCREEN_WIDTH 1920
#define SCREEN_HEIGHT 1080
#define SERIAL_BAUD 115200
#define COMMAND_BUFFER_SIZE 128

// ============================================================================
// ESTADO GLOBAL
// ============================================================================

String inputBuffer = "";
bool readyMessageSent = false;

// ============================================================================
// FAILSAFE ANTI-STUCK PARA TAB E ALT
// ============================================================================
bool tabPressed = false;
unsigned long tabPressTime = 0;
bool altPressed = false;
unsigned long altPressTime = 0;
#define TAB_AUTO_RELEASE_TIMEOUT 2000  // 2 segundos
#define ALT_AUTO_RELEASE_TIMEOUT 5000  // 5 segundos

// ============================================================================
// VERIFICAR E AUTO-LIBERAR TAB/ALT SE FICAREM PRESOS
// ============================================================================
void checkKeysStuck() {
  // Verificar TAB
  if (tabPressed && (millis() - tabPressTime > TAB_AUTO_RELEASE_TIMEOUT)) {
    Serial.println("[FAILSAFE] TAB preso por >2s, liberando automaticamente!");
    Keyboard.release(KEY_TAB);  // ← KEYBOARD NATIVO
    tabPressed = false;
  }

  // Verificar ALT
  if (altPressed && (millis() - altPressTime > ALT_AUTO_RELEASE_TIMEOUT)) {
    Serial.println("[FAILSAFE] ALT preso por >5s, liberando automaticamente!");
    Keyboard.release(KEY_LEFT_ALT);  // ← KEYBOARD NATIVO
    altPressed = false;
  }
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);

  // Inicializar AbsoluteMouse (movimento absoluto) do HID-Project
  AbsoluteMouse.begin();

  // Inicializar Mouse (movimento relativo para câmera) do HID-Project
  Mouse.begin();

  // ✅ NOVO: Inicializar Keyboard NATIVO!
  Keyboard.begin();

  // Aguardar conexão serial
  delay(2000);

  // Enviar mensagem READY
  Serial.println("READY:HYBRID-KEYBOARD-ABSOLUTEMOUSE");
  Serial.flush();

  readyMessageSent = true;
}

// ============================================================================
// LOOP PRINCIPAL
// ============================================================================

void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();

    if (inChar == '\n' || inChar == '\r') {
      if (inputBuffer.length() > 0) {
        processCommand(inputBuffer);
        inputBuffer = "";
      }
    } else if (inputBuffer.length() < COMMAND_BUFFER_SIZE - 1) {
      inputBuffer += inChar;
    }
  }

  // ✅ VERIFICAR: Auto-release de TAB/ALT se ficarem presos
  checkKeysStuck();

  delay(1);
}

// ============================================================================
// PROCESSAMENTO DE COMANDOS
// ============================================================================

void processCommand(String command) {
  command.trim();

  if (command.length() == 0) {
    return;
  }

  // PING
  if (command.equals("PING")) {
    Serial.println("PONG");
    Serial.flush();
    return;
  }

  // Comandos com parâmetros
  int firstColon = command.indexOf(':');
  if (firstColon == -1) {
    Serial.println("ERROR:INVALID_COMMAND");
    Serial.flush();
    return;
  }

  String cmd = command.substring(0, firstColon);
  String params = command.substring(firstColon + 1);

  // Executar comando
  if (cmd.equals("MOVE")) {
    handleMove(params);
  } else if (cmd.equals("MOVE_REL")) {
    handleMoveRelative(params);
  } else if (cmd.equals("RESET_POS")) {
    handleResetPosition(params);
  } else if (cmd.equals("CLICK")) {
    handleClick(params);
  } else if (cmd.equals("CLICK_RIGHT")) {
    handleClickRight(params);
  } else if (cmd.equals("KEY_PRESS")) {
    handleKeyPress(params);
  } else if (cmd.equals("KEY_DOWN")) {
    handleKeyDown(params);
  } else if (cmd.equals("KEY_UP")) {
    handleKeyUp(params);
  } else if (cmd.equals("MOUSE_DOWN")) {
    handleMouseDown(params);
  } else if (cmd.equals("MOUSE_UP")) {
    handleMouseUp(params);
  } else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
    Serial.flush();
  }
}

// ============================================================================
// COMANDOS DE MOUSE
// ============================================================================

void handleMove(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Validar
  if (x < 0 || x > SCREEN_WIDTH || y < 0 || y > SCREEN_HEIGHT) {
    Serial.print("ERROR:OUT_OF_BOUNDS:");
    Serial.print(x);
    Serial.print(":");
    Serial.println(y);
    Serial.flush();
    return;
  }

  // Converter pixel → HID coords
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  AbsoluteMouse.moveTo(hidX, hidY);

  Serial.print("OK:MOVE:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleMoveRelative(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int dx = coords.substring(0, colonIndex).toInt();
  int dy = coords.substring(colonIndex + 1).toInt();

  // ✅ Movimento RELATIVO usando Mouse.move() do HID-Project
  Mouse.move(dx, dy);

  Serial.print("OK:MOVE_REL:(");
  Serial.print(dx);
  Serial.print(",");
  Serial.print(dy);
  Serial.println(")");
  Serial.flush();
}

void handleResetPosition(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println("):NOT_NEEDED");
  Serial.flush();
}

// ============================================================================
// COMANDOS DE CLIQUE
// ============================================================================

void handleClick(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Converter coords
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  // Mover e clicar
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(10);
  AbsoluteMouse.click();

  Serial.print("OK:CLICK:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleClickRight(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Converter coords
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  // Mover e clicar direito
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(10);
  AbsoluteMouse.press(MOUSE_RIGHT);
  delay(50);
  AbsoluteMouse.release(MOUSE_RIGHT);

  Serial.print("OK:CLICK_RIGHT:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleMouseDown(String button) {
  if (button.equals("left")) {
    AbsoluteMouse.press(MOUSE_LEFT);
    Serial.println("OK:MOUSE_DOWN:left");
  } else if (button.equals("right")) {
    AbsoluteMouse.press(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_DOWN:right");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseUp(String button) {
  if (button.equals("left")) {
    AbsoluteMouse.release(MOUSE_LEFT);
    Serial.println("OK:MOUSE_UP:left");
  } else if (button.equals("right")) {
    AbsoluteMouse.release(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_UP:right");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

// ============================================================================
// COMANDOS DE TECLADO - USANDO KEYBOARD.H NATIVO!
// ============================================================================

void handleKeyPress(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  char keyChar = key.charAt(0);
  Keyboard.write(keyChar);  // ← KEYBOARD NATIVO

  Serial.print("OK:KEY_PRESS:");
  Serial.println(key);
  Serial.flush();
}

/**
 * ✅ KEY_DOWN - USANDO KEYBOARD.H NATIVO!
 */
void handleKeyDown(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  // Debug
  Serial.print("[DEBUG_KEY_DOWN] Tecla recebida: '");
  Serial.print(key);
  Serial.println("'");

  // ✅ TECLAS ESPECIAIS COM KEYBOARD NATIVO
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Pressionando KEY_LEFT_ALT");
    Keyboard.press(KEY_LEFT_ALT);  // ← KEYBOARD NATIVO
    altPressed = true;
    altPressTime = millis();
  }
  else if (key.equalsIgnoreCase("ralt")) {
    Keyboard.press(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    Keyboard.press(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    Keyboard.press(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    Keyboard.press(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    Keyboard.press(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    Serial.println("[DEBUG] Pressionando KEY_TAB");
    Keyboard.press(KEY_TAB);
    tabPressed = true;
    tabPressTime = millis();
    Serial.println("[DEBUG] KEY_TAB PRESSIONADO!");
  }
  else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    Keyboard.press(KEY_ESC);
  }
  else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    Keyboard.press(KEY_RETURN);
  }
  else if (key.equalsIgnoreCase("space")) {
    Keyboard.press(' ');
  }
  else {
    // Tecla normal (letra ou número)
    Serial.print("[DEBUG] Pressionando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    Keyboard.press(keyChar);  // ← KEYBOARD NATIVO
  }

  Serial.print("OK:KEY_DOWN:");
  Serial.println(key);
  Serial.flush();
}

/**
 * ✅ KEY_UP - USANDO KEYBOARD.H NATIVO!
 */
void handleKeyUp(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  // Debug
  Serial.print("[DEBUG_KEY_UP] Tecla recebida: '");
  Serial.print(key);
  Serial.println("'");

  // ✅ SOLTAR TECLAS COM KEYBOARD NATIVO
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Soltando KEY_LEFT_ALT");
    Keyboard.release(KEY_LEFT_ALT);
    altPressed = false;
  }
  else if (key.equalsIgnoreCase("ralt")) {
    Keyboard.release(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    Keyboard.release(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    Keyboard.release(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    Keyboard.release(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    Keyboard.release(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    Serial.println("[DEBUG] Soltando KEY_TAB");
    Keyboard.release(KEY_TAB);
    tabPressed = false;
    Serial.println("[DEBUG] KEY_TAB LIBERADO!");
  }
  else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    Keyboard.release(KEY_ESC);
  }
  else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    Keyboard.release(KEY_RETURN);
  }
  else if (key.equalsIgnoreCase("space")) {
    Keyboard.release(' ');
  }
  else {
    // Tecla normal
    Serial.print("[DEBUG] Soltando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    Keyboard.release(keyChar);  // ← KEYBOARD NATIVO
  }

  Serial.print("OK:KEY_UP:");
  Serial.println(key);
  Serial.flush();
}

// ============================================================================
// FIM DO CÓDIGO
// ============================================================================
