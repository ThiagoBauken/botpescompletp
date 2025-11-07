/*
 * Arduino HID Controller for Fishing Bot v5 - VERSÃO COM ABSOLUTE MOUSE
 *
 * Hardware: Arduino Pro Micro (ATmega32U4) ou Leonardo
 * Funcionalidade: Recebe comandos via Serial e executa inputs de teclado/mouse
 *
 * ✅ NOVO: Suporte para posicionamento absoluto do mouse via biblioteca AbsMouse
 *
 * IMPORTANTE: Instale a biblioteca AbsMouse antes de usar:
 * 1. Abra Arduino IDE
 * 2. Sketch → Include Library → Manage Libraries
 * 3. Procure por "AbsMouse" (por Jonathan Edgecombe)
 * 4. Clique em "Install"
 *
 * OU instale manualmente:
 * 1. Baixe: https://github.com/jonathanedgecombe/absmouse/releases
 * 2. Extraia para: Documents/Arduino/libraries/AbsMouse/
 *
 * Protocolo Serial (115200 baud):
 * - PING              - Teste de conexão (responde PONG)
 * - KEYDOWN:<key>     - Pressionar tecla (ex: KEYDOWN:a)
 * - KEYUP:<key>       - Soltar tecla
 * - KEYPRESS:<key>    - Press + Release
 * - MOUSEDOWN:<L|R>   - Pressionar botão mouse (L=esquerdo, R=direito)
 * - MOUSEUP:<L|R>     - Soltar botão mouse
 * - MOUSECLICK:<L|R>  - Click completo
 * - MOUSEMOVE:<x>:<y> - Mover mouse (x,y relativos)
 * - MOUSEABS:<x>:<y>  - ✅ NOVO: Mover mouse para posição absoluta (x,y na tela)
 */

#include <Keyboard.h>
#include <Mouse.h>
#include <AbsMouse.h>

// Resolução da tela (configurar de acordo com sua tela)
#define SCREEN_WIDTH 1920
#define SCREEN_HEIGHT 1080

void setup() {
  // Inicializar Serial (115200 baud = ~10x mais rápido que 9600)
  Serial.begin(115200);
  while (!Serial) {
    ; // Aguardar porta serial conectar (necessário para Leonardo/Pro Micro)
  }

  // Inicializar bibliotecas HID
  Keyboard.begin();
  Mouse.begin();

  // ✅ Inicializar AbsMouse com resolução da tela
  AbsMouse.init(SCREEN_WIDTH, SCREEN_HEIGHT);

  // Sinalizar pronto
  Serial.println("READY");
  Serial.flush();
}

void loop() {
  // ⚡ MUDANÇA: Ler comandos DIRETAMENTE no loop()
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remover \r\n e espaços

    if (command.length() > 0) {
      processCommand(command);
    }
  }
}

// Processar comando recebido
void processCommand(String cmd) {
  // PING - Teste de conexão
  if (cmd == "PING") {
    Serial.println("PONG");
    Serial.flush();
    return;
  }

  // Separar comando e argumentos
  int colonIndex = cmd.indexOf(':');

  // Comandos sem argumentos
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_FORMAT");
    Serial.flush();
    return;
  }

  String command = cmd.substring(0, colonIndex);
  String args = cmd.substring(colonIndex + 1);

  // ===== COMANDOS DE TECLADO =====
  if (command == "KEYDOWN") {
    handleKeyDown(args);
  }
  else if (command == "KEYUP") {
    handleKeyUp(args);
  }
  else if (command == "KEYPRESS") {
    handleKeyPress(args);
  }

  // ===== COMANDOS DE MOUSE =====
  else if (command == "MOUSEDOWN") {
    handleMouseDown(args);
  }
  else if (command == "MOUSEUP") {
    handleMouseUp(args);
  }
  else if (command == "MOUSECLICK") {
    handleMouseClick(args);
  }
  else if (command == "MOUSEMOVE") {
    handleMouseMove(args);
  }
  // ✅ NOVO: Comando para movimento absoluto
  else if (command == "MOUSEABS") {
    handleMouseAbsolute(args);
  }

  else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
    Serial.flush();
  }
}

// ===== HANDLERS DE TECLADO =====

void handleKeyDown(String key) {
  char keyChar = parseKey(key);
  if (keyChar != 0) {
    Keyboard.press(keyChar);
    Serial.println("OK:KEYDOWN");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

void handleKeyUp(String key) {
  char keyChar = parseKey(key);
  if (keyChar != 0) {
    Keyboard.release(keyChar);
    Serial.println("OK:KEYUP");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

void handleKeyPress(String key) {
  char keyChar = parseKey(key);
  if (keyChar != 0) {
    Keyboard.press(keyChar);
    delay(50); // 50ms press duration
    Keyboard.release(keyChar);
    Serial.println("OK:KEYPRESS");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

// Converter string para código de tecla
char parseKey(String key) {
  key.trim();

  // Teclas numéricas (1-6 para varas)
  if (key.length() == 1 && key[0] >= '0' && key[0] <= '9') {
    return key[0];
  }

  // Teclas de letra (A, D, W, S)
  if (key.length() == 1 && ((key[0] >= 'a' && key[0] <= 'z') || (key[0] >= 'A' && key[0] <= 'Z'))) {
    return key[0];
  }

  // Teclas especiais
  if (key == "SPACE") return ' ';
  if (key == "ESC") return KEY_ESC;
  if (key == "TAB") return KEY_TAB;
  if (key == "RETURN" || key == "ENTER") return KEY_RETURN;
  if (key == "SHIFT") return KEY_LEFT_SHIFT;
  if (key == "CTRL") return KEY_LEFT_CTRL;
  if (key == "ALT") return KEY_LEFT_ALT;
  if (key == "F1") return KEY_F1;
  if (key == "F2") return KEY_F2;
  if (key == "F3") return KEY_F3;
  if (key == "F4") return KEY_F4;
  if (key == "F5") return KEY_F5;
  if (key == "F6") return KEY_F6;
  if (key == "F7") return KEY_F7;
  if (key == "F8") return KEY_F8;
  if (key == "F9") return KEY_F9;
  if (key == "F10") return KEY_F10;
  if (key == "F11") return KEY_F11;
  if (key == "F12") return KEY_F12;

  return 0; // Tecla inválida
}

// ===== HANDLERS DE MOUSE =====

void handleMouseDown(String button) {
  button.trim();
  if (button == "L") {
    Mouse.press(MOUSE_LEFT);
    Serial.println("OK:MOUSEDOWN:L");
  } else if (button == "R") {
    Mouse.press(MOUSE_RIGHT);
    Serial.println("OK:MOUSEDOWN:R");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseUp(String button) {
  button.trim();
  if (button == "L") {
    Mouse.release(MOUSE_LEFT);
    Serial.println("OK:MOUSEUP:L");
  } else if (button == "R") {
    Mouse.release(MOUSE_RIGHT);
    Serial.println("OK:MOUSEUP:R");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseClick(String button) {
  button.trim();
  if (button == "L") {
    Mouse.click(MOUSE_LEFT);
    Serial.println("OK:MOUSECLICK:L");
  } else if (button == "R") {
    Mouse.click(MOUSE_RIGHT);
    Serial.println("OK:MOUSECLICK:R");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseMove(String coords) {
  // Formato: x:y (movimento relativo)
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  Mouse.move(x, y, 0);
  Serial.println("OK:MOUSEMOVE");
  Serial.flush();
}

// ✅ NOVO: Handler para movimento absoluto do mouse
void handleMouseAbsolute(String coords) {
  // Formato: x:y (posição absoluta na tela)
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Validar coordenadas (dentro da tela)
  if (x < 0 || x > SCREEN_WIDTH || y < 0 || y > SCREEN_HEIGHT) {
    Serial.println("ERROR:COORDS_OUT_OF_BOUNDS");
    Serial.flush();
    return;
  }

  // Mover mouse para posição absoluta
  AbsMouse.move(x, y);

  Serial.println("OK:MOUSEABS");
  Serial.flush();
}
