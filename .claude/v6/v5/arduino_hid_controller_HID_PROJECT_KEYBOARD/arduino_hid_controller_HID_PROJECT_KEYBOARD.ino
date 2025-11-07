/*
 * ============================================================================
 * 🎮 ULTIMATE FISHING BOT - ARDUINO HID CONTROLLER v5.2 - NKRO FIX
 * ============================================================================
 *
 * ✅ CORREÇÃO: Usando NKROKeyboard para suportar KEY_LEFT_ALT!
 *
 * BIBLIOTECA USADA: HID-Project (NicoHood)
 * - AbsoluteMouse: Mouse absoluto
 * - NKROKeyboard: Teclado com N-Key Rollover (múltiplas teclas simultâneas)
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
    NKROKeyboard.release(KEY_TAB);
    tabPressed = false;
  }

  // ✅ DESABILITADO: ALT failsafe removido porque operações de baú demoram >5s
  // O Python controla o ALT corretamente via KEY_UP:alt
  // if (altPressed && (millis() - altPressTime > ALT_AUTO_RELEASE_TIMEOUT)) {
  //   Serial.println("[FAILSAFE] ALT preso por >5s, liberando automaticamente!");
  //   NKROKeyboard.release(KEY_LEFT_ALT);
  //   altPressed = false;
  // }
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);

  // Inicializar AbsoluteMouse (movimento absoluto)
  AbsoluteMouse.begin();

  // ✅ Inicializar Mouse (movimento relativo para câmera)
  Mouse.begin();

  // ✅ USAR NKROKEYBOARD PARA SUPORTAR KEY_LEFT_ALT!
  NKROKeyboard.begin();

  // Aguardar conexão serial
  delay(2000);

  // Enviar mensagem READY
  Serial.println("READY:HID-NKRO-MOUSE");
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
    // ⚠️ Comando sem ":" - pode ser comando simples ou erro
    Serial.print("ERROR:MISSING_COLON:");
    Serial.println(command);
    Serial.flush();
    return;
  }

  String cmd = command.substring(0, firstColon);
  String params = command.substring(firstColon + 1);  // Pode ser vazio (OK!)

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
  } else if (cmd.equals("MOUSE_DOWN_REL")) {
    handleMouseDownRelative(params);
  } else if (cmd.equals("MOUSE_UP_REL")) {
    handleMouseUpRelative(params);
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

  // ✅ IMPLEMENTADO: Movimento RELATIVO usando Mouse.move()
  // Replica exatamente o comportamento da API Windows (SendInput com MOUSEEVENTF_MOVE)
  // ✅ CORRIGIDO: Inverter sinal de DX (biblioteca HID-Project tem eixo X invertido)
  Mouse.move(-dx, dy);

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

  // ✅ CORREÇÃO CRÍTICA: HID-Project PRECISA de moveTo() para sincronizar!
  // Sem isso, AbsoluteMouse não sabe onde o cursor está
  // e causa movimento indesejado ao pressionar botões!
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  AbsoluteMouse.moveTo(hidX, hidY);  // ← MOVE DE VERDADE!
  delay(20);  // Pequeno delay para garantir sincronização

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");  // ← Removido :NOT_NEEDED
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

  // ✅ CORREÇÃO: Delays adequados para HID-Project
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(50);  // ✅ AUMENTADO: 10ms → 50ms (espera movimento completar)

  AbsoluteMouse.click();
  delay(30);  // ✅ NOVO: Delay após clicar

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

  // ✅ CORREÇÃO: Delays adequados para HID-Project
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(50);  // ✅ AUMENTADO: 10ms → 50ms (espera movimento)

  AbsoluteMouse.press(MOUSE_RIGHT);
  delay(80);  // ✅ AUMENTADO: 50ms → 80ms (clique mais estável)

  AbsoluteMouse.release(MOUSE_RIGHT);
  delay(30);  // ✅ NOVO: Delay após soltar

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

// ✅ SOLUÇÃO DEFINITIVA: Press/Release RELATIVO para fishing cycle!
// Usa Mouse.press() ao invés de AbsoluteMouse.press()
// Isso ELIMINA drift porque Mouse.press() NÃO requer coordenadas!
void handleMouseDownRelative(String button) {
  if (button.equals("left")) {
    Mouse.press(MOUSE_LEFT);
    Serial.println("OK:MOUSE_DOWN_REL:left");
  } else if (button.equals("right")) {
    Mouse.press(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_DOWN_REL:right");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseUpRelative(String button) {
  if (button.equals("left")) {
    Mouse.release(MOUSE_LEFT);
    Serial.println("OK:MOUSE_UP_REL:left");
  } else if (button.equals("right")) {
    Mouse.release(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_UP_REL:right");
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

  // ✅ TECLAS ESPECIAIS COM NKROKEYBOARD
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    NKROKeyboard.press(KEY_LEFT_ALT);
    altPressed = true;           // ✅ RASTREAR: ALT foi pressionado
    altPressTime = millis();     // ✅ TIMESTAMP: Quando foi pressionado
  }
  else if (key.equalsIgnoreCase("ralt")) {
    NKROKeyboard.press(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    NKROKeyboard.press(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    NKROKeyboard.press(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    NKROKeyboard.press(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    NKROKeyboard.press(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    NKROKeyboard.press(KEY_TAB);
    tabPressed = true;
    tabPressTime = millis();
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
  else {
    // Tecla normal (letra ou número)
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

  // ✅ SOLTAR TECLAS COM NKROKEYBOARD
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    NKROKeyboard.release(KEY_LEFT_ALT);
    altPressed = false;          // ✅ LIMPAR: ALT foi solto
  }
  else if (key.equalsIgnoreCase("ralt")) {
    NKROKeyboard.release(KEY_RIGHT_ALT);
  }
  else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    NKROKeyboard.release(KEY_LEFT_CTRL);
  }
  else if (key.equalsIgnoreCase("rctrl")) {
    NKROKeyboard.release(KEY_RIGHT_CTRL);
  }
  else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    NKROKeyboard.release(KEY_LEFT_SHIFT);
  }
  else if (key.equalsIgnoreCase("rshift")) {
    NKROKeyboard.release(KEY_RIGHT_SHIFT);
  }
  else if (key.equalsIgnoreCase("tab")) {
    NKROKeyboard.release(KEY_TAB);
    tabPressed = false;          // ✅ LIMPAR: TAB foi solto
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
  else {
    // Tecla normal
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
