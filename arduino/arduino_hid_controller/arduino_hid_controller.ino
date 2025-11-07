/*
 * Arduino HID Controller for Fishing Bot v5
 *
 * Hardware: Arduino Pro Micro (ATmega32U4) ou Leonardo
 * Funcionalidade: Recebe comandos via Serial e executa inputs de teclado/mouse
 *
 * Protocolo Serial (9600 baud):
 * - KEYDOWN:<key>     - Pressionar tecla (ex: KEYDOWN:1)
 * - KEYUP:<key>       - Soltar tecla
 * - KEYPRESS:<key>    - Press + Release
 * - MOUSEDOWN:<L|R>   - Pressionar botão mouse (L=esquerdo, R=direito)
 * - MOUSEUP:<L|R>     - Soltar botão mouse
 * - MOUSECLICK:<L|R>  - Click completo
 * - MOUSEMOVE:<x>:<y> - Mover mouse (x,y relativos)
 * - MOUSETO:<x>:<y>   - Mover mouse (x,y absolutos)
 * - PING              - Teste de conexão (responde PONG)
 *
 * Instalação:
 * 1. Abrir Arduino IDE
 * 2. Tools → Board → Arduino Leonardo (Pro Micro é compatível)
 * 3. Tools → Port → Selecionar porta COM do Arduino
 * 4. Upload do sketch
 * 5. Verificar porta COM no Windows Device Manager
 */

#include <Keyboard.h>
#include <Mouse.h>

// Buffer para comandos seriais
String inputBuffer = "";
bool commandComplete = false;

void setup() {
  // Inicializar Serial
  Serial.begin(9600);
  while (!Serial) {
    ; // Aguardar porta serial conectar (necessário para Leonardo/Pro Micro)
  }

  // Inicializar bibliotecas HID
  Keyboard.begin();
  Mouse.begin();

  // Sinalizar pronto
  Serial.println("READY");
  Serial.flush();
}

void loop() {
  // Processar comandos seriais
  if (commandComplete) {
    processCommand(inputBuffer);
    inputBuffer = "";
    commandComplete = false;
  }
}

// Event handler para dados seriais
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      commandComplete = true;
    } else {
      inputBuffer += inChar;
    }
  }
}

// Processar comando recebido
void processCommand(String cmd) {
  cmd.trim(); // Remover espaços em branco

  // PING - Teste de conexão
  if (cmd == "PING") {
    Serial.println("PONG");
    Serial.flush();
    return;
  }

  // Separar comando e argumentos
  int colonIndex = cmd.indexOf(':');
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
  else if (command == "MOUSETO") {
    handleMouseTo(args);
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

void handleMouseTo(String coords) {
  // Formato: x:y (absoluto - precisa de cálculo externo no Python)
  // Arduino não suporta movimento absoluto nativamente
  // Este comando é tratado pelo Python side que calcula delta

  Serial.println("ERROR:ABSOLUTE_MOVE_NOT_SUPPORTED");
  Serial.println("HINT:Use MOUSEMOVE with calculated delta from Python");
  Serial.flush();
}
