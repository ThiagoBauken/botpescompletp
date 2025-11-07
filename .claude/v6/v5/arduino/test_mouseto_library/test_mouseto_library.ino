/*
 * Teste Simples da Biblioteca MouseTo
 *
 * Este sketch verifica se a biblioteca MouseTo está instalada corretamente
 * e testa as funções básicas.
 */

#include <Mouse.h>
#include <MouseTo.h>

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }

  Serial.println("=================================");
  Serial.println("TESTE DA BIBLIOTECA MOUSETO");
  Serial.println("=================================");

  // Inicializar Mouse HID
  Mouse.begin();

  // Configurar MouseTo
  MouseTo.setScreenResolution(1920, 1080);
  MouseTo.setCorrectionFactor(1);

  Serial.println("✓ Mouse.begin() OK");
  Serial.println("✓ MouseTo configurado OK");
  Serial.println("");

  // Teste 1: Mover para centro da tela
  Serial.println("TESTE 1: Mover para centro (960, 540)");
  MouseTo.setTarget(960, 540);

  int moveCount = 0;
  unsigned long startTime = millis();

  while (true) {
    if (MouseTo.move()) {
      // Chegou ao alvo!
      unsigned long elapsed = millis() - startTime;
      Serial.print("✓ Alvo alcançado em ");
      Serial.print(moveCount);
      Serial.print(" chamadas, ");
      Serial.print(elapsed);
      Serial.println("ms");
      break;
    }
    moveCount++;
    delay(1);

    // Timeout
    if (millis() - startTime > 5000) {
      Serial.println("✗ TIMEOUT - Não chegou ao alvo em 5s");
      break;
    }
  }

  Serial.println("");
  Serial.println("=================================");
  Serial.println("TESTE CONCLUÍDO");
  Serial.println("=================================");
  Serial.println("");
  Serial.println("Envie comandos via Serial Monitor:");
  Serial.println("  MOVE:x:y  - Move para posição (ex: MOVE:500:300)");
  Serial.println("  PING      - Teste de comunicação");
}

void loop() {
  // Aguardar comandos do Serial Monitor
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "PING") {
      Serial.println("PONG");

    } else if (command.startsWith("MOVE:")) {
      // Formato: MOVE:x:y
      int colonIndex = command.indexOf(':', 5);
      if (colonIndex > 0) {
        int x = command.substring(5, colonIndex).toInt();
        int y = command.substring(colonIndex + 1).toInt();

        Serial.print("Movendo para (");
        Serial.print(x);
        Serial.print(", ");
        Serial.print(y);
        Serial.println(")...");

        MouseTo.setTarget(x, y);

        unsigned long startTime = millis();
        while (true) {
          if (MouseTo.move()) {
            Serial.println("OK - Alvo alcançado!");
            break;
          }
          delay(1);

          if (millis() - startTime > 1000) {
            Serial.println("TIMEOUT");
            break;
          }
        }
      }

    } else {
      Serial.print("Comando desconhecido: ");
      Serial.println(command);
    }
  }
}
