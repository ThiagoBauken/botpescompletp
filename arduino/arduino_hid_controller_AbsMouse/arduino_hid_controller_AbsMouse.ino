/*
 * Arduino HID Controller for Fishing Bot v5 - AbsMouse Edition
 *
 * ✅ SOLUÇÃO PARA PROBLEMA DE POSICIONAMENTO DE MOUSE!
 *
 * Hardware: Arduino Pro Micro (ATmega32U4) ou Leonardo
 * Bibliotecas necessárias:
 *   - Mouse.h (nativa)
 *   - Keyboard.h (nativa)
 *   - HID-Project (contém AbsMouse)
 *
 * ✅ INSTALAÇÃO AbsMouse:
 *   Arduino IDE → Sketch → Include Library → Manage Libraries
 *   Buscar "HID-Project" → Instalar "HID-Project by NicoHood"
 *
 *   OU baixar manualmente:
 *   https://github.com/NicoHood/HID/archive/refs/heads/master.zip
 *   Arduino IDE → Sketch → Include Library → Add .ZIP Library
 *
 * ========================================
 * VANTAGENS DO AbsMouse vs MouseTo
 * ========================================
 *
 * ✅ SEM estado interno - sem problemas de dessincronização!
 * ✅ SEM necessidade de RESET_POS - comando removido!
 * ✅ Movimento INSTANTÂNEO - sem loops de movimento!
 * ✅ SEMPRE preciso - vai direto para (x, y)!
 * ✅ Código MUITO mais simples e confiável!
 *
 * ========================================
 * PROTOCOLO SERIAL (115200 baud)
 * ========================================
 *
 * === COMANDOS DE SISTEMA ===
 * PING                         - Teste (responde PONG)
 * EMERGENCY_STOP               - Soltar todos inputs
 *
 * === MOUSE - COMANDOS LONGOS (com AbsMouse - absoluto direto) ===
 * MOVE:<x>:<y>                 - Mover absoluto DIRETO (sem loops!)
 * CLICK:<x>:<y>                - Clicar esquerdo em posição
 * RIGHT_CLICK:<x>:<y>          - Clicar direito em posição
 * DRAG:<x1>:<y1>:<x2>:<y2>     - Arrastar de (x1,y1) para (x2,y2)
 * MOVE_REL:<dx>:<dy>           - Mover relativo (para câmera no ALT)
 * MOVE_REL_LOOP:<dx>:<dy>:<count>:<delay_ms> - Movimento relativo repetido
 *
 * === MOUSE - COMANDOS CURTOS (compatibilidade) ===
 * MLD                          - Mouse Left Down
 * MLU                          - Mouse Left Up
 * MRD                          - Mouse Right Down
 * MRU                          - Mouse Right Up
 * MOUSE_DOWN:<L|R>             - Segurar botão (formato longo)
 * MOUSE_UP:<L|R>               - Soltar botão (formato longo)
 *
 * === TECLADO - COMANDOS LONGOS ===
 * KEY_PRESS:<key>              - Pressionar+soltar tecla
 * KEY_DOWN:<key>               - Segurar tecla
 * KEY_UP:<key>                 - Soltar tecla
 *
 * === TECLADO - COMANDOS CURTOS (1-6 caracteres) ===
 * Tecla única para PRESS: w, a, s, d, e, tab, 1, 2, 3, 4, 5, 6, alt
 * Tecla + "0" para RELEASE: w0, a0, s0, d0, e0, tab0, 10, 20, 30, 40, 50, 60, alt0
 *
 * === EXEMPLOS ===
 * MOVE:960:540                 - Move para centro da tela (DIRETO!)
 * CLICK:1350:450               - Clica em (1350, 450)
 * DRAG:1350:450:899:1005       - Arrasta isca para slot vara
 * MOVE_REL:100:-50             - Move +100px direita, -50px cima (câmera)
 * MOVE_REL_LOOP:-115:43:8:50   - Move (-115,43) 8x com 50ms delay (câmera)
 * MLD                          - Segura botão esquerdo (rápido)
 * d                            - Pressiona tecla D (rápido)
 * d0                           - Solta tecla D (rápido)
 */

#include <Keyboard.h>
#include "HID-Project.h"  // Contém AbsMouse, SingleAbsMouse, Mouse, etc.

// Configurações de movimento
#define DRAG_PAUSE_START_MS 200    // Pausa após chegar no início do drag
#define DRAG_PAUSE_END_MS 400      // Pausa após chegar no fim do drag

void setup() {
  // Inicializar Serial
  Serial.begin(115200);
  while (!Serial) { ; }

  // Inicializar HID
  Keyboard.begin();
  Mouse.begin();  // Mouse relativo (para MOVE_REL)

  // ✅ Inicializar AbsMouse (movimento absoluto)
  AbsMouse.init(1920, 1080);  // Resolução da tela

  // ✅ NOTA: AbsMouse NÃO precisa de calibração!
  // Movimento é sempre absoluto e direto, sem estado interno.

  // Sinalizar pronto
  Serial.println("READY:AbsMouse");
  Serial.flush();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() > 0) {
      processCommand(command);
    }
  }
}

void processCommand(String cmd) {
  // PING - Teste de conexão
  if (cmd == "PING") {
    Serial.println("PONG");
    Serial.flush();
    return;
  }

  // EMERGENCY_STOP - Soltar tudo
  if (cmd == "EMERGENCY_STOP") {
    Mouse.release(MOUSE_LEFT);
    Mouse.release(MOUSE_RIGHT);
    Keyboard.releaseAll();
    Serial.println("OK:EMERGENCY_STOP");
    Serial.flush();
    return;
  }

  // ✅ RESET_POS não é mais necessário com AbsMouse!
  // AbsMouse sempre move para posição absoluta sem tracking interno.
  // Mantido para compatibilidade, mas não faz nada.
  if (cmd.startsWith("RESET_POS:")) {
    String coords = cmd.substring(10);
    int colonIndex = coords.indexOf(':');
    if (colonIndex != -1) {
      int x = coords.substring(0, colonIndex).toInt();
      int y = coords.substring(colonIndex + 1).toInt();
      Serial.print("OK:RESET_POS:(");
      Serial.print(x);
      Serial.print(",");
      Serial.print(y);
      Serial.println("):NOT_NEEDED");
    } else {
      Serial.println("OK:RESET_POS:NOT_NEEDED");
    }
    Serial.flush();
    return;
  }

  // ===== COMANDOS CURTOS (compatibilidade com código antigo) =====
  // Vantagem: Menos bytes via serial, mais rápido

  // Mouse buttons (curtos)
  if (cmd == "MLD") { Mouse.press(MOUSE_LEFT); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "MLU") { Mouse.release(MOUSE_LEFT); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "MRD") { Mouse.press(MOUSE_RIGHT); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "MRU") { Mouse.release(MOUSE_RIGHT); Serial.println("OK"); Serial.flush(); return; }

  // Keyboard press (curtos) - teclas comuns de pesca
  if (cmd == "w") { Keyboard.press('w'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "a") { Keyboard.press('a'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "s") { Keyboard.press('s'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "d") { Keyboard.press('d'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "e") { Keyboard.press('e'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "tab") { Keyboard.press(KEY_TAB); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "1") { Keyboard.press('1'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "2") { Keyboard.press('2'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "3") { Keyboard.press('3'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "4") { Keyboard.press('4'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "5") { Keyboard.press('5'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "6") { Keyboard.press('6'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "alt") { Keyboard.press(KEY_LEFT_ALT); Serial.println("OK"); Serial.flush(); return; }

  // Keyboard release (curtos) - formato: tecla + "0"
  if (cmd == "w0") { Keyboard.release('w'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "a0") { Keyboard.release('a'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "s0") { Keyboard.release('s'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "d0") { Keyboard.release('d'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "e0") { Keyboard.release('e'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "tab0") { Keyboard.release(KEY_TAB); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "10") { Keyboard.release('1'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "20") { Keyboard.release('2'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "30") { Keyboard.release('3'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "40") { Keyboard.release('4'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "50") { Keyboard.release('5'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "60") { Keyboard.release('6'); Serial.println("OK"); Serial.flush(); return; }
  if (cmd == "alt0") { Keyboard.release(KEY_LEFT_ALT); Serial.println("OK"); Serial.flush(); return; }

  // Separar comando e argumentos (comandos longos/complexos)
  int colonIndex = cmd.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:UNKNOWN_COMMAND");
    Serial.flush();
    return;
  }

  String command = cmd.substring(0, colonIndex);
  String args = cmd.substring(colonIndex + 1);

  // ===== COMANDOS DE MOUSE =====
  if (command == "MOVE") {
    handleMove(args);
  }
  else if (command == "CLICK") {
    handleClick(args);
  }
  else if (command == "RIGHT_CLICK") {
    handleRightClick(args);
  }
  else if (command == "DRAG") {
    handleDrag(args);
  }
  else if (command == "MOVE_REL") {
    handleMoveRelative(args);
  }
  else if (command == "MOVE_REL_LOOP") {
    handleMoveRelativeLoop(args);
  }
  else if (command == "MOUSE_DOWN") {
    handleMouseDown(args);
  }
  else if (command == "MOUSE_UP") {
    handleMouseUp(args);
  }
  // ===== COMANDOS DE TECLADO =====
  else if (command == "KEY_PRESS") {
    handleKeyPress(args);
  }
  else if (command == "KEY_DOWN") {
    handleKeyDown(args);
  }
  else if (command == "KEY_UP") {
    handleKeyUp(args);
  }
  else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
    Serial.flush();
  }
}

// ===== HANDLERS DE MOUSE =====

void handleMove(String coords) {
  // Formato: x:y
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // ✅ MOVIMENTO DIRETO COM AbsMouse - SEM LOOPS!
  // AbsMouse.move() vai DIRETAMENTE para (x, y) em UMA instrução!
  // Não precisa de loops, timeouts, ou calibração!
  AbsMouse.move(x, y);

  Serial.print("OK:MOVE:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleClick(String coords) {
  // Formato: x:y
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Mover para posição (DIRETO!)
  AbsMouse.move(x, y);
  delay(20);  // Pequena pausa antes de clicar

  // Clicar
  Mouse.click(MOUSE_LEFT);

  Serial.print("OK:CLICK:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleRightClick(String coords) {
  // Formato: x:y
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Mover para posição (DIRETO!)
  AbsMouse.move(x, y);
  delay(20);  // Pequena pausa antes de clicar

  // Clicar direito
  Mouse.click(MOUSE_RIGHT);

  Serial.print("OK:RIGHT_CLICK:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}

void handleDrag(String coords) {
  // Formato: x1:y1:x2:y2
  int colon1 = coords.indexOf(':');
  if (colon1 == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int colon2 = coords.indexOf(':', colon1 + 1);
  if (colon2 == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int colon3 = coords.indexOf(':', colon2 + 1);
  if (colon3 == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x1 = coords.substring(0, colon1).toInt();
  int y1 = coords.substring(colon1 + 1, colon2).toInt();
  int x2 = coords.substring(colon2 + 1, colon3).toInt();
  int y2 = coords.substring(colon3 + 1).toInt();

  // PASSO 1: Mover para início (DIRETO!)
  AbsMouse.move(x1, y1);
  delay(DRAG_PAUSE_START_MS);

  // PASSO 2: Segurar botão esquerdo
  Mouse.press(MOUSE_LEFT);
  delay(DRAG_PAUSE_START_MS);

  // PASSO 3: Mover para destino (DIRETO!)
  AbsMouse.move(x2, y2);
  delay(DRAG_PAUSE_END_MS);

  // PASSO 4: Soltar botão
  Mouse.release(MOUSE_LEFT);
  delay(DRAG_PAUSE_END_MS);

  Serial.print("OK:DRAG:(");
  Serial.print(x1);
  Serial.print(",");
  Serial.print(y1);
  Serial.print(")→(");
  Serial.print(x2);
  Serial.print(",");
  Serial.print(y2);
  Serial.println(")");
  Serial.flush();
}

void handleMouseDown(String button) {
  button.trim();
  if (button == "L") {
    Mouse.press(MOUSE_LEFT);
    Serial.println("OK:MOUSE_DOWN:L");
  } else if (button == "R") {
    Mouse.press(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_DOWN:R");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMouseUp(String button) {
  button.trim();
  if (button == "L") {
    Mouse.release(MOUSE_LEFT);
    Serial.println("OK:MOUSE_UP:L");
  } else if (button == "R") {
    Mouse.release(MOUSE_RIGHT);
    Serial.println("OK:MOUSE_UP:R");
  } else {
    Serial.println("ERROR:INVALID_BUTTON");
  }
  Serial.flush();
}

void handleMoveRelative(String coords) {
  // Formato: dx:dy
  // Move mouse relativo (usado para câmera durante ALT)
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int dx = coords.substring(0, colonIndex).toInt();
  int dy = coords.substring(colonIndex + 1).toInt();

  // Movimento relativo direto (não afeta AbsMouse)
  Mouse.move(dx, dy, 0);

  Serial.print("OK:MOVE_REL:(");
  Serial.print(dx);
  Serial.print(",");
  Serial.print(dy);
  Serial.println(")");
  Serial.flush();
}

void handleMoveRelativeLoop(String params) {
  // Formato: dx:dy:count:delay_ms
  // Exemplo: MOVE_REL_LOOP:-115:43:8:50
  // Move (-115, 43) repetido 8 vezes com 50ms entre cada

  int colon1 = params.indexOf(':');
  if (colon1 == -1) {
    Serial.println("ERROR:INVALID_PARAMS");
    Serial.flush();
    return;
  }

  int colon2 = params.indexOf(':', colon1 + 1);
  if (colon2 == -1) {
    Serial.println("ERROR:INVALID_PARAMS");
    Serial.flush();
    return;
  }

  int colon3 = params.indexOf(':', colon2 + 1);
  if (colon3 == -1) {
    Serial.println("ERROR:INVALID_PARAMS");
    Serial.flush();
    return;
  }

  int dx = params.substring(0, colon1).toInt();
  int dy = params.substring(colon1 + 1, colon2).toInt();
  int count = params.substring(colon2 + 1, colon3).toInt();
  int delayMs = params.substring(colon3 + 1).toInt();

  // Executar movimento em loop
  for (int i = 0; i < count; i++) {
    Mouse.move(dx, dy, 0);
    if (delayMs > 0 && i < count - 1) {
      delay(delayMs);
    }
  }

  Serial.print("OK:MOVE_REL_LOOP:(");
  Serial.print(dx);
  Serial.print(",");
  Serial.print(dy);
  Serial.print(")x");
  Serial.print(count);
  Serial.println(")");
  Serial.flush();
}

// ===== HANDLERS DE TECLADO =====

void handleKeyPress(String key) {
  key.trim();

  // Tecla única (caractere)
  if (key.length() == 1) {
    Keyboard.write(key[0]);
    Serial.println("OK:KEY_PRESS");
    Serial.flush();
    return;
  }

  // Tecla especial
  uint8_t keyCode = parseSpecialKey(key);
  if (keyCode != 0) {
    Keyboard.press(keyCode);
    delay(50);
    Keyboard.release(keyCode);
    Serial.println("OK:KEY_PRESS");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

void handleKeyDown(String key) {
  key.trim();

  // Tecla única
  if (key.length() == 1) {
    Keyboard.press(key[0]);
    Serial.println("OK:KEY_DOWN");
    Serial.flush();
    return;
  }

  // Tecla especial
  uint8_t keyCode = parseSpecialKey(key);
  if (keyCode != 0) {
    Keyboard.press(keyCode);
    Serial.println("OK:KEY_DOWN");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

void handleKeyUp(String key) {
  key.trim();

  // Tecla única
  if (key.length() == 1) {
    Keyboard.release(key[0]);
    Serial.println("OK:KEY_UP");
    Serial.flush();
    return;
  }

  // Tecla especial
  uint8_t keyCode = parseSpecialKey(key);
  if (keyCode != 0) {
    Keyboard.release(keyCode);
    Serial.println("OK:KEY_UP");
  } else {
    Serial.println("ERROR:INVALID_KEY");
  }
  Serial.flush();
}

// ===== FUNÇÕES AUXILIARES =====

uint8_t parseSpecialKey(String key) {
  /*
   * Converte nome de tecla especial para código
   */
  if (key == "TAB") return KEY_TAB;
  if (key == "ENTER" || key == "RETURN") return KEY_RETURN;
  if (key == "ESC") return KEY_ESC;
  if (key == "BACKSPACE") return KEY_BACKSPACE;
  if (key == "DELETE") return KEY_DELETE;
  if (key == "INSERT") return KEY_INSERT;
  if (key == "HOME") return KEY_HOME;
  if (key == "END") return KEY_END;
  if (key == "PAGE_UP") return KEY_PAGE_UP;
  if (key == "PAGE_DOWN") return KEY_PAGE_DOWN;
  if (key == "UP") return KEY_UP_ARROW;
  if (key == "DOWN") return KEY_DOWN_ARROW;
  if (key == "LEFT") return KEY_LEFT_ARROW;
  if (key == "RIGHT") return KEY_RIGHT_ARROW;
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

  return 0;  // Tecla não reconhecida
}
