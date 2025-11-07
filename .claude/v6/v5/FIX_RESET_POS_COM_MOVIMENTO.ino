// 🔧 FIX: handleResetPosition() COM MOVIMENTO FORÇADO
//
// Substitua este código na linha 481 do arduino_hid_controller_HID.ino

void handleResetPosition(String coords) {
  /*
   * ✅ FIX CRÍTICO: RESET_POS agora MOVE o cursor para sincronizar!
   *
   * PROBLEMA: setTarget() sozinho NÃO atualiza current_x e current_y
   * SOLUÇÃO: Mover para 1px diferente, depois voltar (força atualização)
   *
   * Sequência:
   * 1. setTarget(x-1, y) + move() → Vai para (958, 539)
   * 2. setTarget(x, y) + move()   → Volta para (959, 539)
   * 3. Agora current_x e current_y estão CORRETOS!
   */
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // ✅ PASSO 1: Mover para 1px à esquerda (forçar atualização)
  MouseTo.setTarget(x - 1, y, false);
  unsigned long startTime = millis();
  while (true) {
    if (MouseTo.move()) break;  // Chegou!
    delay(3);
    if (millis() - startTime > 2000) break;  // Timeout 2s
  }

  delay(50);  // Pequena pausa

  // ✅ PASSO 2: Voltar para posição correta
  MouseTo.setTarget(x, y, false);
  startTime = millis();
  while (true) {
    if (MouseTo.move()) break;  // Chegou!
    delay(3);
    if (millis() - startTime > 2000) break;  // Timeout 2s
  }

  // ✅ Agora current_x = x e current_y = y estão CORRETOS!

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}
