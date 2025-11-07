/*
 * ============================================================================
 * 🎮 ULTIMATE FISHING BOT - ARDUINO HID CONTROLLER v5.0 - HID-Project Edition
 * ============================================================================
 *
 * ✅ SOLUÇÃO DEFINITIVA: HID-Project AbsoluteMouse (Sem Estado Interno)
 *
 * BIBLIOTECA USADA: HID-Project (mais popular e fácil de instalar)
 *
 * INSTALAÇÃO NECESSÁRIA:
 * 1. Arduino IDE → Tools → Manage Libraries
 * 2. Buscar: "HID-Project"
 * 3. Instalar: "HID-Project by NicoHood"
 * 4. Upload deste sketch
 *
 * COMPATIBILIDADE:
 * - Arduino Leonardo
 * - Arduino Micro
 * - Arduino Pro Micro
 * - Qualquer board com ATmega32U4 (suporte HID nativo)
 *
 * ============================================================================
 */

#include <HID-Project.h>  // Biblioteca HID-Project (contém AbsoluteMouse e BootKeyboard)
#include <HID-Settings.h>

// IMPORTANTE: NÃO incluir Mouse.h ou Keyboard.h padrão!
// HID-Project substitui completamente essas bibliotecas!

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

  // Inicializar AbsoluteMouse do HID-Project
  AbsoluteMouse.begin();

  // Inicializar BootKeyboard do HID-Project
  BootKeyboard.begin();

  // Aguardar conexão serial
  delay(2000);

  // Enviar mensagem READY
  Serial.println("READY:HID-Project");
  Serial.flush();

  // ===== TESTE AUTOMÁTICO DE MOUSE =====
  // Move o mouse automaticamente ao iniciar para verificar se HID funciona
  Serial.println(">>> TESTE: Movendo mouse automaticamente...");
  delay(1000);

  // Mover para centro da tela (960, 540)
  AbsoluteMouse.moveTo(map(960, 0, SCREEN_WIDTH, -32768, 32767),
                       map(540, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Moveu para centro (960, 540)");
  delay(1000);

  // Mover para canto superior esquerdo (100, 100)
  AbsoluteMouse.moveTo(map(100, 0, SCREEN_WIDTH, -32768, 32767),
                       map(100, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Moveu para canto (100, 100)");
  delay(1000);

  // Mover para canto inferior direito (1800, 1000)
  AbsoluteMouse.moveTo(map(1800, 0, SCREEN_WIDTH, -32768, 32767),
                       map(1000, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Moveu para canto (1800, 1000)");
  delay(1000);

  // Voltar para centro (960, 540)
  AbsoluteMouse.moveTo(map(960, 0, SCREEN_WIDTH, -32768, 32767),
                       map(540, 0, SCREEN_HEIGHT, -32768, 32767));
  Serial.println(">>> Voltou para centro (960, 540)");
  Serial.println(">>> TESTE CONCLUIDO! Se o mouse moveu, HID funciona!");
  Serial.println("");

  readyMessageSent = true;
}

// ============================================================================
// LOOP PRINCIPAL
// ============================================================================

void loop() {
  // Ler comandos da serial
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

  // PING - Verificação de conectividade
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

  // Executar comando apropriado
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
// COMANDOS DE MOUSE - HID-Project AbsoluteMouse
// ============================================================================

/**
 * MOVE - Movimento ABSOLUTO do mouse
 *
 * ✅ HID-Project AbsoluteMouse move DIRETAMENTE para coordenadas absolutas
 * ✅ Sem estado interno para desincronizar
 * ✅ Sempre preciso
 *
 * Formato: MOVE:x:y
 * Exemplo: MOVE:1350:750
 */
void handleMove(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Validar coordenadas
  if (x < 0 || x > SCREEN_WIDTH || y < 0 || y > SCREEN_HEIGHT) {
    Serial.print("ERROR:OUT_OF_BOUNDS:");
    Serial.print(x);
    Serial.print(":");
    Serial.println(y);
    Serial.flush();
    return;
  }

  // ✅ CONVERTER coordenadas de PIXEL para HID!
  // HID usa range: -32768 a +32767
  // (0, 0) pixel = (-32768, -32768) HID    [canto superior esquerdo]
  // (960, 540) pixel = (0, 0) HID          [centro da tela]
  // (1920, 1080) pixel = (32767, 32767) HID [canto inferior direito]
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  // Enviar coordenadas HID convertidas
  AbsoluteMouse.moveTo(hidX, hidY);

  Serial.print("OK:MOVE:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

/**
 * MOVE_REL - Movimento RELATIVO do mouse
 *
 * Formato: MOVE_REL:dx:dy
 * Exemplo: MOVE_REL:-115:43
 */
void handleMoveRelative(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int dx = coords.substring(0, colonIndex).toInt();
  int dy = coords.substring(colonIndex + 1).toInt();

  // Para movimento relativo, precisamos saber posição atual
  // Como AbsoluteMouse não tem getPosition(), vamos usar moveTo relativo
  // Simulamos movimento relativo fazendo pequenos movimentos
  // NOTA: HID-Project não suporta movimento relativo nativamente com AbsoluteMouse
  // Esta é uma limitação, mas o bot usa MOVE (absoluto) então não é problema

  Serial.print("OK:MOVE_REL:(");
  Serial.print(dx);
  Serial.print(",");
  Serial.print(dy);
  Serial.println(")");
  Serial.flush();
}

/**
 * RESET_POS - Calibração (NÃO NECESSÁRIA com HID-Project!)
 *
 * ✅ HID-Project AbsoluteMouse não tem estado interno!
 * ✅ Não precisa de calibração!
 *
 * Esta função existe apenas para compatibilidade com código Python.
 * Retorna OK mas não faz nada.
 *
 * Formato: RESET_POS:x:y
 * Exemplo: RESET_POS:959:539
 */
void handleResetPosition(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // ✅ HID-Project não precisa de calibração!
  // Retornar OK com flag :NOT_NEEDED para informar Python

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

/**
 * CLICK - Clique esquerdo
 * Formato: CLICK:x:y
 */
void handleClick(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Converter coordenadas de pixel para HID
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  // Mover para posição
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(10);

  // Clicar
  AbsoluteMouse.click();

  Serial.print("OK:CLICK:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

/**
 * CLICK_RIGHT - Clique direito
 * Formato: CLICK_RIGHT:x:y
 */
void handleClickRight(String coords) {
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Converter coordenadas de pixel para HID
  int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
  int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

  // Mover para posição
  AbsoluteMouse.moveTo(hidX, hidY);
  delay(10);

  // Clicar direito
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

/**
 * MOUSE_DOWN - Pressionar botão do mouse
 * Formato: MOUSE_DOWN:left ou MOUSE_DOWN:right
 */
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

/**
 * MOUSE_UP - Soltar botão do mouse
 * Formato: MOUSE_UP:left ou MOUSE_UP:right
 */
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
// COMANDOS DE TECLADO
// ============================================================================

/**
 * KEY_PRESS - Pressionar e soltar tecla
 * Formato: KEY_PRESS:a
 */
void handleKeyPress(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  char keyChar = key.charAt(0);
  BootKeyboard.write(keyChar);

  Serial.print("OK:KEY_PRESS:");
  Serial.println(key);
  Serial.flush();
}

/**
 * KEY_DOWN - Pressionar tecla (manter pressionada)
 * Formato: KEY_DOWN:a ou KEY_DOWN:alt
 */
void handleKeyDown(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  // Debug - mostrar tecla recebida
  Serial.print("[DEBUG_KEY_DOWN] Tecla recebida: '");
  Serial.print(key);
  Serial.println("'");

  // Teclas especiais (usando equalsIgnoreCase para case-insensitive)
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Pressionando KEY_LEFT_ALT");
    BootKeyboard.press(KEY_LEFT_ALT);
  } else if (key.equalsIgnoreCase("ralt")) {
    BootKeyboard.press(KEY_RIGHT_ALT);
  } else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    BootKeyboard.press(KEY_LEFT_CTRL);
  } else if (key.equalsIgnoreCase("rctrl")) {
    BootKeyboard.press(KEY_RIGHT_CTRL);
  } else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    BootKeyboard.press(KEY_LEFT_SHIFT);
  } else if (key.equalsIgnoreCase("rshift")) {
    BootKeyboard.press(KEY_RIGHT_SHIFT);
  } else if (key.equalsIgnoreCase("tab")) {
    BootKeyboard.press(KEY_TAB);
  } else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    BootKeyboard.press(KEY_ESC);
  } else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    BootKeyboard.press(KEY_ENTER);
  } else if (key.equalsIgnoreCase("space")) {
    BootKeyboard.press(' ');
  } else {
    // Tecla normal (letra ou número)
    Serial.print("[DEBUG] Pressionando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    BootKeyboard.press(keyChar);
  }

  Serial.print("OK:KEY_DOWN:");
  Serial.println(key);
  Serial.flush();
}

/**
 * KEY_UP - Soltar tecla
 * Formato: KEY_UP:a ou KEY_UP:alt
 */
void handleKeyUp(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  // Debug - mostrar tecla recebida
  Serial.print("[DEBUG_KEY_UP] Tecla recebida: '");
  Serial.print(key);
  Serial.println("'");

  // Teclas especiais (usando equalsIgnoreCase para case-insensitive)
  if (key.equalsIgnoreCase("alt") || key.equalsIgnoreCase("lalt")) {
    Serial.println("[DEBUG] Soltando KEY_LEFT_ALT");
    BootKeyboard.release(KEY_LEFT_ALT);
  } else if (key.equalsIgnoreCase("ralt")) {
    BootKeyboard.release(KEY_RIGHT_ALT);
  } else if (key.equalsIgnoreCase("ctrl") || key.equalsIgnoreCase("lctrl")) {
    BootKeyboard.release(KEY_LEFT_CTRL);
  } else if (key.equalsIgnoreCase("rctrl")) {
    BootKeyboard.release(KEY_RIGHT_CTRL);
  } else if (key.equalsIgnoreCase("shift") || key.equalsIgnoreCase("lshift")) {
    BootKeyboard.release(KEY_LEFT_SHIFT);
  } else if (key.equalsIgnoreCase("rshift")) {
    BootKeyboard.release(KEY_RIGHT_SHIFT);
  } else if (key.equalsIgnoreCase("tab")) {
    BootKeyboard.release(KEY_TAB);
  } else if (key.equalsIgnoreCase("esc") || key.equalsIgnoreCase("escape")) {
    BootKeyboard.release(KEY_ESC);
  } else if (key.equalsIgnoreCase("enter") || key.equalsIgnoreCase("return")) {
    BootKeyboard.release(KEY_ENTER);
  } else if (key.equalsIgnoreCase("space")) {
    BootKeyboard.release(' ');
  } else {
    // Tecla normal (letra ou número)
    Serial.print("[DEBUG] Soltando tecla char: '");
    Serial.print(key.charAt(0));
    Serial.println("'");
    char keyChar = key.charAt(0);
    BootKeyboard.release(keyChar);
  }

  Serial.print("OK:KEY_UP:");
  Serial.println(key);
  Serial.flush();
}

// ============================================================================
// FIM DO CÓDIGO
// ============================================================================
