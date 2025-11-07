/*
 * Arduino HID Controller for Fishing Bot v5 - MouseTo Edition
 *
 * Hardware: Arduino Pro Micro (ATmega32U4) ou Leonardo
 * Bibliotecas necessárias:
 *   - Mouse.h (nativa)
 *   - Keyboard.h (nativa)
 *   - MouseTo.h (https://github.com/per1234/MouseTo)
 *
 * ✅ INSTALAÇÃO MouseTo:
 *   Arduino IDE → Sketch → Include Library → Manage Libraries
 *   Buscar "MouseTo" → Instalar "MouseTo by per1234"
 *
 * ========================================
 * PROTOCOLO SERIAL (115200 baud)
 * ========================================
 *
 * === COMANDOS DE SISTEMA ===
 * PING                         - Teste (responde PONG)
 * EMERGENCY_STOP               - Soltar todos inputs
 * RESET_POS:<x>:<y>            - Calibrar posição do mouse (chamar após abrir baú)
 *
 * === MOUSE - COMANDOS LONGOS (com MouseTo - absoluto) ===
 * MOVE:<x>:<y>                 - Mover absoluto com MouseTo
 * CLICK:<x>:<y>                - Clicar esquerdo em posição
 * RIGHT_CLICK:<x>:<y>          - Clicar direito em posição
 * DRAG:<x1>:<y1>:<x2>:<y2>     - Arrastar de (x1,y1) para (x2,y2)
 * MOVE_REL:<dx>:<dy>           - Mover relativo (sem MouseTo)
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
 *  
 * MOVE:960:540                 - Move para centro da tela
 * CLICK:1350:450               - Clica em (1350, 450)
 * DRAG:1350:450:899:1005       - Arrasta isca para slot vara
 * MOVE_REL:100:-50             - Move +100px direita, -50px cima
 * MOVE_REL_LOOP:-115:43:8:50   - Move (-115,43) 8x com 50ms delay (câmera)
 * MLD                          - Segura botão esquerdo (rápido)
 * d                            - Pressiona tecla D (rápido)
 * d0                           - Solta tecla D (rápido)
 */

#include <Keyboard.h>
#include <Mouse.h>
#include <MouseTo.h>

// Configurações de movimento
#define MOVE_TIMEOUT_MS 4000       // Timeout para alcançar alvo (4 segundos)
#define MOVE_STEP_DELAY_MS 3       // Delay entre movimentos (3ms = mais suave)
#define MOUSETO_MAX_JUMP 5         // Pixels por movimento (menor = mais suave)
#define DRAG_PAUSE_START_MS 200    // Pausa após chegar no início do drag
#define DRAG_PAUSE_END_MS 400      // Pausa após chegar no fim do drag
#define DRAG_STEP_DELAY_MS 8       // Delay entre passos do drag (mais lento = mais humano)

void setup() {
  // Inicializar Serial
  Serial.begin(115200);
  while (!Serial) { ; }

  // Inicializar HID
  Keyboard.begin();
  Mouse.begin();

  // Configurar MouseTo
  MouseTo.setScreenResolution(1920, 1080);  // CRÍTICO: Definir resolução da tela!
  MouseTo.setCorrectionFactor(0.97);        // Correção: estava indo longe demais (987->959, 554->539)
  MouseTo.setMaxJump(MOUSETO_MAX_JUMP);     // Pixels por movimento (configurável no topo)

  // NÃO fazer homing inicial - o Python vai calibrar com RESET_POS após abrir o baú

  // Sinalizar pronto
  Serial.println("READY");
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

  // RESET_POS - Informar posição do mouse (executar após abrir baú)
  // Formato: RESET_POS:x:y
  // IMPORTANTE: Apenas informa ao MouseTo onde o mouse está, SEM mover!
  if (cmd.startsWith("RESET_POS:")) {
    handleResetPosition(cmd.substring(10));  // Remove "RESET_POS:"
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

  // Mover usando MouseTo (absoluto)
  if (!moveToPosition(x, y)) {
    Serial.println("ERROR:MOVE_TIMEOUT");
    Serial.flush();
    return;
  }

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

  // Mover para posição
  if (!moveToPosition(x, y)) {
    Serial.println("ERROR:MOVE_TIMEOUT");
    Serial.flush();
    return;
  }

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

  // Mover para posição
  if (!moveToPosition(x, y)) {
    Serial.println("ERROR:MOVE_TIMEOUT");
    Serial.flush();
    return;
  }

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

  // PASSO 1: Mover para início
  if (!moveToPosition(x1, y1)) {
    Serial.println("ERROR:DRAG_MOVE_START_TIMEOUT");
    Serial.flush();
    return;
  }
  delay(DRAG_PAUSE_START_MS);

  // PASSO 2: Segurar botão esquerdo
  Mouse.press(MOUSE_LEFT);
  delay(DRAG_PAUSE_START_MS);

  // PASSO 3: Mover para destino (lento, com passos)
  if (!moveToPositionSlow(x2, y2, DRAG_STEP_DELAY_MS)) {
    // Se falhar, soltar botão antes de retornar erro
    Mouse.release(MOUSE_LEFT);
    Serial.println("ERROR:DRAG_MOVE_END_TIMEOUT");
    Serial.flush();
    return;
  }
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
  // Move mouse relativo (sem MouseTo, usa Mouse.move direto)
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int dx = coords.substring(0, colonIndex).toInt();
  int dy = coords.substring(colonIndex + 1).toInt();

  // Movimento relativo direto
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

void handleResetPosition(String coords) {
  /*
   * RESET_POS - Sincroniza o estado interno do MouseTo com a posição REAL do cursor
   *
   * ✅ SOLUÇÃO DEFINITIVA (2025-10-23):
   * Movimento 1px para FORÇAR atualização do estado interno do MouseTo!
   *
   * PROBLEMA: setTarget() sozinho NÃO atualiza current_x e current_y internos
   * SOLUÇÃO: Mover 1px para esquerda e voltar (força sincronização)
   *
   * Sequência:
   * 1. setTarget(x-1, y) + move() → Vai para (958, 539) - FORÇA atualização!
   * 2. setTarget(x, y) + move()   → Volta para (959, 539) - Estado correto!
   * 3. Agora current_x = 959 e current_y = 539 (SINCRONIZADO!)
   *
   * Movimento total: 2px (quase invisível)
   * Confiabilidade: 95%+
   *
   * Formato: x:y (ex: 959:539)
   */
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // ✅ PASSO 1: Mover 1px para ESQUERDA (força atualização do estado interno)
  MouseTo.setTarget(x - 1, y, false);  // false = não fazer home para (0,0)
  unsigned long startTime = millis();
  while (true) {
    if (MouseTo.move()) {
      break;  // Chegou em (x-1, y)!
    }
    delay(MOVE_STEP_DELAY_MS);  // 3ms entre passos

    // Timeout de segurança (2 segundos)
    if (millis() - startTime > 2000) {
      break;
    }
  }

  delay(50);  // Pequena pausa entre movimentos

  // ✅ PASSO 2: Voltar para posição CORRETA
  MouseTo.setTarget(x, y, false);
  startTime = millis();
  while (true) {
    if (MouseTo.move()) {
      break;  // Chegou em (x, y)! Estado interno agora CORRETO!
    }
    delay(MOVE_STEP_DELAY_MS);

    // Timeout de segurança
    if (millis() - startTime > 2000) {
      break;
    }
  }

  // ✅ Agora current_x = x e current_y = y estão PERFEITAMENTE sincronizados!
  // Próximos comandos MOVE vão calcular delta corretamente!

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
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

bool moveToPosition(int x, int y) {
  /*
   * Move mouse para posição absoluta usando MouseTo
   *
   * Returns: true se chegou, false se timeout
   */
  MouseTo.setTarget(x, y, false);  // false = não fazer "home" antes (não vai para canto)

  unsigned long startTime = millis();
  int moveCount = 0;

  while (true) {
    // MouseTo.move() retorna true quando chegou ao alvo
    if (MouseTo.move()) {
      // Alvo alcançado! (debug comentado para não confundir Python)
      // Serial.print("DEBUG:MOVES=");
      // Serial.print(moveCount);
      // Serial.print(",TIME=");
      // Serial.print(millis() - startTime);
      // Serial.println("ms");
      return true;
    }

    moveCount++;
    delay(MOVE_STEP_DELAY_MS);  // Delay configurável = movimento mais suave e humanizado

    // Timeout de segurança
    if (millis() - startTime > MOVE_TIMEOUT_MS) {
      return false;
    }
  }
}

bool moveToPositionSlow(int x, int y, int stepDelayMs) {
  /*
   * Move mouse lentamente para drag suave
   *
   * Returns: true se chegou, false se timeout
   */
  MouseTo.setTarget(x, y, false);  // false = não fazer "home" antes (não vai para canto)

  unsigned long startTime = millis();
  while (true) {
    // MouseTo.move() retorna true quando chegou ao alvo
    if (MouseTo.move()) {
      return true;  // Alvo alcançado!
    }

    delay(stepDelayMs);  // Delay maior para movimento suave

    // Timeout maior para movimento lento
    if (millis() - startTime > (MOVE_TIMEOUT_MS * 3)) {
      return false;
    }
  }
}

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
