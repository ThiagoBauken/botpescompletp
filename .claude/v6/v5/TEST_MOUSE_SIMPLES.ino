/*
 * ============================================================================
 * 🧪 TESTE SIMPLES: Verifica se mouse HID funciona
 * ============================================================================
 *
 * Este sketch MOVE O MOUSE AUTOMATICAMENTE a cada 2 segundos.
 *
 * NÃO precisa de comandos Serial!
 * NÃO precisa de nada complicado!
 *
 * SE O MOUSE MOVER → USB HID está funcionando!
 * SE O MOUSE NÃO MOVER → Problema no USB HID ou biblioteca!
 *
 * ============================================================================
 */

#include <HID-Project.h>

void setup() {
  // Inicializar Serial (para debug)
  Serial.begin(115200);
  delay(1000);

  // Inicializar AbsoluteMouse
  AbsoluteMouse.begin();

  Serial.println("====================================");
  Serial.println("TESTE: Mouse HID Automatico");
  Serial.println("====================================");
  Serial.println("O mouse vai mover AUTOMATICAMENTE!");
  Serial.println("Aguarde 5 segundos...");
  Serial.println("");

  // Aguardar 5 segundos antes de começar
  delay(5000);

  Serial.println("INICIANDO TESTE!");
  Serial.println("");
}

void loop() {
  // TESTE 1: Mover para centro da tela
  Serial.println(">>> Movendo para CENTRO (960, 540)...");
  AbsoluteMouse.moveTo(960, 540);
  delay(2000);

  // TESTE 2: Mover para canto superior esquerdo
  Serial.println(">>> Movendo para CANTO SUPERIOR ESQUERDO (100, 100)...");
  AbsoluteMouse.moveTo(100, 100);
  delay(2000);

  // TESTE 3: Mover para canto inferior direito
  Serial.println(">>> Movendo para CANTO INFERIOR DIREITO (1800, 900)...");
  AbsoluteMouse.moveTo(1800, 900);
  delay(2000);

  // TESTE 4: Mover para lado esquerdo
  Serial.println(">>> Movendo para LADO ESQUERDO (100, 540)...");
  AbsoluteMouse.moveTo(100, 540);
  delay(2000);

  // TESTE 5: Mover para lado direito
  Serial.println(">>> Movendo para LADO DIREITO (1800, 540)...");
  AbsoluteMouse.moveTo(1800, 540);
  delay(2000);

  Serial.println("");
  Serial.println("====================================");
  Serial.println("CICLO COMPLETO!");
  Serial.println("Repetindo em 2 segundos...");
  Serial.println("====================================");
  Serial.println("");

  delay(2000);
}
