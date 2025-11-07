/*
 * ============================================================================
 * 🎮 ULTIMATE FISHING BOT - ARDUINO HID CONTROLLER v5.2 - NKRO KEYBOARD
 * ============================================================================
 *
 * ✅ SOLUÇÃO: NKROKeyboard para suportar ALT + outras teclas simultaneamente!
 *
 * BIBLIOTECA USADA: HID-Project (NicoHood)
 * - AbsoluteMouse: Mouse absoluto
 * - NKROKeyboard: Teclado com suporte a múltiplas teclas simultâneas
 *
 * INSTALAÇÃO:
 * 1. Arduino IDE → Tools → Manage Libraries
 * 2. Buscar: "HID-Project"
 * 3. Instalar: "HID-Project by NicoHood"
 * 4. Upload deste sketch
 *
 * ============================================================================
 */

#include <HID-Project.h>
#include <HID-Settings.h>

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
// SETUP
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);

  // Inicializar AbsoluteMouse
  AbsoluteMouse.begin();

  // ✅ USAR NKROKEYBOARD EM VEZ DE KEYBOARD OU BOOTKEYBOARD!
  // NKRO = N-Key Rollover = Suporta múltiplas teclas ao mesmo tempo
  NKROKeyboard.begin();

  // Aguardar conexão serial
  delay(2000);

  // Enviar mensagem READY
  Serial.println("READY:HID-NKRO");
  Serial.flush();

  // ===== TESTE AUTOMÁTICO =====
  Serial.println(">>> TESTE: Movendo mouse...");
  delay(1000);

  // Centro da tela
  AbsoluteMouse.moveTo(map(960, 0, SCREEN_WIDTH, -32768, 32767),
                       map(540, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Centro (960, 540)");
  delay(1000);

  // Canto superior esquerdo
  AbsoluteMouse.moveTo(map(100, 0, SCREEN_WIDTH, -32768, 32767),
                       map(100, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Canto (100, 100)");
  delay(1000);

  // Voltar ao centro
  AbsoluteMouse.moveTo(map(960, 0, SCREEN_WIDTH, -32768, 32767),
                       map(540, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Voltou ao centro");
  Serial.println(">>> TESTE CONCLUIDO!");
  Serial.println("");

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
// COMANDOS DE TECLADO - USANDO NKROKEYBOARD!
// ============================================================================

void handleKeyPress(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  char keyChar = key.charAt(0);
  NKROKeyboard.write(keyChar);

  Serial.print("OK:KEY_PRESS:");
  Serial.println(key);
  Serial.flush();
}

/**
 * ✅ KEY_DOWN - USANDO NKROKEYBOARD COM KEY_LEFT_ALT!
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

  // ✅ TECLAS ESPECIAIS COM NKROKEYBOARD
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Pressionando KEY_LEFT_ALT");
    NKROKeyboard.press(KEY_LEFT_ALT);
  }
  else if (key.equalsIgnoreCase("ralt")) {
    Serial.println("[DEBUG] Pressionando KEY_RIGHT_ALT");
    NKROKeyboard.press(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    Serial.println("[DEBUG] Pressionando KEY_LEFT_CTRL");
    NKROKeyboard.press(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    NKROKeyboard.press(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    Serial.println("[DEBUG] Pressionando KEY_LEFT_SHIFT");
    NKROKeyboard.press(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    NKROKeyboard.press(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    NKROKeyboard.press(KEY_TAB);
  }
  else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    NKROKeyboard.press(KEY_ESC);
  }
  else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    NKROKeyboard.press(KEY_RETURN);
  }
  else if (key.equalsIgnoreCase("space")) {
    NKROKeyboard.press(' ');
  }
  else if (key.equalsIgnoreCase("pgdn") || key.equalsIgnoreCase("pagedown")) {
    Serial.println("[DEBUG] Pressionando KEY_PAGE_DOWN");
    NKROKeyboard.press(KEY_PAGE_DOWN);
  }
  else {
    // Tecla normal (letra ou número)
    Serial.print("[DEBUG] Pressionando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    NKROKeyboard.press(keyChar);
  }

  Serial.print("OK:KEY_DOWN:");
  Serial.println(key);
  Serial.flush();
}

/**
 * ✅ KEY_UP - USANDO NKROKEYBOARD!
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

  // ✅ SOLTAR TECLAS COM NKROKEYBOARD
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Soltando KEY_LEFT_ALT");
    NKROKeyboard.release(KEY_LEFT_ALT);
  }
  else if (key.equalsIgnoreCase("ralt")) {
    Serial.println("[DEBUG] Soltando KEY_RIGHT_ALT");
    NKROKeyboard.release(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    Serial.println("[DEBUG] Soltando KEY_LEFT_CTRL");
    NKROKeyboard.release(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    NKROKeyboard.release(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    Serial.println("[DEBUG] Soltando KEY_LEFT_SHIFT");
    NKROKeyboard.release(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    NKROKeyboard.release(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    NKROKeyboard.release(KEY_TAB);
  }
  else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    NKROKeyboard.release(KEY_ESC);
  }
  else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    NKROKeyboard.release(KEY_RETURN);
  }
  else if (key.equalsIgnoreCase("space")) {
    NKROKeyboard.release(' ');
  }
  else if (key.equalsIgnoreCase("pgdn") || key.equalsIgnoreCase("pagedown")) {
    Serial.println("[DEBUG] Soltando KEY_PAGE_DOWN");
    NKROKeyboard.release(KEY_PAGE_DOWN);
  }
  else {
    // Tecla normal
    Serial.print("[DEBUG] Soltando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    NKROKeyboard.release(keyChar);
  }

  Serial.print("OK:KEY_UP:");
  Serial.println(key);
  Serial.flush();
}

// ============================================================================
// FIM DO CÓDIGO
// ============================================================================
