/*
 * ============================================================================
 * 🔧 TESTE: HID-Project com API Alternativa
 * ============================================================================
 *
 * Usando ScreenResolution para configurar range correto!
 *
 * ============================================================================
 */

#include <HID-Project.h>

#define SCREEN_WIDTH 1920
#define SCREEN_HEIGHT 1080

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("====================================");
  Serial.println("TESTE: HID-Project API Alternativa");
  Serial.println("====================================");
  Serial.println("");

  // MÉTODO 1: Inicializar AbsoluteMouse
  AbsoluteMouse.begin();
  Serial.println("[1] AbsoluteMouse.begin() - OK");

  delay(1000);

  Serial.println("");
  Serial.println("Aguarde 3 segundos...");
  delay(3000);

  // TESTE AUTOMÁTICO
  Serial.println("");
  Serial.println(">>> TESTE 1: Canto (0, 0)");
  moveAndReport(0, 0);
  delay(2000);

  Serial.println(">>> TESTE 2: Centro (960, 540)");
  moveAndReport(960, 540);
  delay(2000);

  Serial.println(">>> TESTE 3: Direita (1900, 540)");
  moveAndReport(1900, 540);
  delay(2000);

  Serial.println(">>> TESTE 4: Baixo (960, 1000)");
  moveAndReport(960, 1000);
  delay(2000);

  Serial.println(">>> TESTE 5: Canto direito inferior (1919, 1079)");
  moveAndReport(1919, 1079);
  delay(2000);

  Serial.println("");
  Serial.println("====================================");
  Serial.println("Testes concluidos!");
  Serial.println("Digite comandos: MOVE:x:y");
  Serial.println("====================================");
  Serial.println("");
}

void moveAndReport(int x, int y) {
  Serial.print("  Movendo para (");
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.println(")...");

  // Tentar moveTo
  AbsoluteMouse.moveTo(x, y);

  Serial.println("  Comando enviado!");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("MOVE:")) {
      String coords = command.substring(5);
      int colonIndex = coords.indexOf(':');

      if (colonIndex != -1) {
        int x = coords.substring(0, colonIndex).toInt();
        int y = coords.substring(colonIndex + 1).toInt();

        Serial.print(">>> MOVE: (");
        Serial.print(x);
        Serial.print(", ");
        Serial.print(y);
        Serial.println(")");

        moveAndReport(x, y);

        Serial.print("OK:MOVE:(");
        Serial.print(x);
        Serial.print(",");
        Serial.print(y);
        Serial.println(")");
      }
    } else if (command.equals("PING")) {
      Serial.println("PONG");
    } else if (command.startsWith("TEST:")) {
      // Teste especial: mover em sequência
      Serial.println(">>> TESTE SEQUENCIAL:");
      for (int i = 0; i < 5; i++) {
        int x = 100 + (i * 400);
        int y = 100 + (i * 200);
        Serial.print("  [");
        Serial.print(i + 1);
        Serial.print("] ");
        moveAndReport(x, y);
        delay(1000);
      }
      Serial.println(">>> TESTE CONCLUIDO!");
    }
  }
}
