/*
 * TESTE SIMPLES - AbsMouse
 *
 * Este sketch testa APENAS o AbsMouse sem Serial
 * O mouse deve mover automaticamente em círculo
 */

#include <AbsMouse.h>

void setup() {
  // Inicializar AbsMouse
  AbsMouse.init(1920, 1080);

  delay(3000); // Aguardar 3 segundos
}

void loop() {
  // Mover para centro
  AbsMouse.move(960, 540);
  delay(2000);

  // Mover para canto superior esquerdo
  AbsMouse.move(100, 100);
  delay(2000);

  // Mover para canto superior direito
  AbsMouse.move(1820, 100);
  delay(2000);

  // Mover para canto inferior direito
  AbsMouse.move(1820, 980);
  delay(2000);

  // Mover para canto inferior esquerdo
  AbsMouse.move(100, 980);
  delay(2000);
}
