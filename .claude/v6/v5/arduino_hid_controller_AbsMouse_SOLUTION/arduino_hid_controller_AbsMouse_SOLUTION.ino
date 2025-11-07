/*
 * ============================================================================
 * 🎮 ULTIMATE FISHING BOT - ARDUINO HID CONTROLLER v5.0 - AbsMouse Edition
 * ============================================================================
 *
 * ✅ SOLUÇÃO DEFINITIVA: AbsMouse (Sem Estado Interno)
 *
 * MUDANÇAS DA VERSÃO MouseTo:
 * - Removido: MouseTo library (tinha estado interno que desincronizava)
 * - Adicionado: AbsMouse library (posicionamento absoluto direto)
 * - Resultado: 100% confiável, sem movimento visível, código mais simples
 *
 * INSTALAÇÃO NECESSÁRIA:
 * 1. Arduino IDE → Tools → Manage Libraries
 * 2. Buscar: "AbsMouse"
 * 3. Instalar: "AbsMouse by jonathanedgecombe"
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

#include <AbsMouse.h>
#include <Mouse.h>     // Necessário para cliques e movimento relativo
#include <Keyboard.h>

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

  // Inicializar AbsMouse com resolução da tela
  AbsMouse.init(SCREEN_WIDTH, SCREEN_HEIGHT);

  // Inicializar Mouse padrão (para cliques e movimento relativo)
  Mouse.begin();

  // Inicializar Keyboard
  Keyboard.begin();

  // Aguardar conexão serial
  delay(1000);

  // Enviar mensagem READY
  Serial.println("READY:AbsMouse");
  Serial.flush();
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
// COMANDOS DE MOUSE - AbsMouse (Posicionamento Absoluto)
// ============================================================================

/**
 * MOVE - Movimento ABSOLUTO do mouse
 *
 * ✅ AbsMouse move DIRETAMENTE para coordenadas absolutas
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

  // ✅ MOVIMENTO DIRETO - SEM cálculo de delta!
  // AbsMouse envia coordenadas absolutas via HID
  AbsMouse.move(x, y);

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

  // AbsMouse não tem método relativo nativo
  // Usar Mouse.move() padrão do Arduino
  Mouse.move(dx, dy, 0);

  Serial.print("OK:MOVE_REL:(");
  Serial.print(dx);
  Serial.print(",");
  Serial.print(dy);
  Serial.println(")");
  Serial.flush();
}

/**
 * RESET_POS - Calibração (NÃO NECESSÁRIA com AbsMouse!)
 *
 * ✅ AbsMouse não tem estado interno!
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

  // ✅ AbsMouse não precisa de calibração!
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

  // Mover para posição
  AbsMouse.move(x, y);
  delay(10);

  // Clicar
  Mouse.click(MOUSE_LEFT);

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

  // Mover para posição
  AbsMouse.move(x, y);
  delay(10);

  // Clicar direito
  Mouse.click(MOUSE_RIGHT);

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
    Mouse.press(MOUSE_LEFT);
    Serial.println("OK:MOUSE_DOWN:left");
  } else if (button.equals("right")) {
    Mouse.press(MOUSE_RIGHT);
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
    Mouse.release(MOUSE_LEFT);
    Serial.println("OK:MOUSE_UP:left");
  } else if (button.equals("right")) {
    Mouse.release(MOUSE_RIGHT);
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
  Keyboard.press(keyChar);
  delay(50);
  Keyboard.release(keyChar);

  Serial.print("OK:KEY_PRESS:");
  Serial.println(key);
  Serial.flush();
}

/**
 * KEY_DOWN - Pressionar tecla (manter pressionada)
 * Formato: KEY_DOWN:a
 */
void handleKeyDown(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  char keyChar = key.charAt(0);
  Keyboard.press(keyChar);

  Serial.print("OK:KEY_DOWN:");
  Serial.println(key);
  Serial.flush();
}

/**
 * KEY_UP - Soltar tecla
 * Formato: KEY_UP:a
 */
void handleKeyUp(String key) {
  if (key.length() == 0) {
    Serial.println("ERROR:INVALID_KEY");
    Serial.flush();
    return;
  }

  char keyChar = key.charAt(0);
  Keyboard.release(keyChar);

  Serial.print("OK:KEY_UP:");
  Serial.println(key);
  Serial.flush();
}

// ============================================================================
// FIM DO CÓDIGO
// ============================================================================
