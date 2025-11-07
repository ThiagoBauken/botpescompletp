/*
 * ============================================================================
 * 🔍 DEBUG: Coordenadas HID-Project
 * ============================================================================
 *
 * Este sketch mostra EXATAMENTE o que está sendo enviado ao Windows!
 *
 * ============================================================================
 */

#include <HID-Project.h>

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("====================================");
  Serial.println("DEBUG: Coordenadas HID-Project");
  Serial.println("====================================");
  Serial.println("");

  // Inicializar AbsoluteMouse
  AbsoluteMouse.begin();

  Serial.println("AbsoluteMouse inicializado!");
  Serial.println("");
  Serial.println("Enviando comandos de teste...");
  Serial.println("");

  delay(2000);

  // TESTE 1: Canto Superior Esquerdo (0, 0)
  Serial.println(">>> TESTE 1: Canto Superior Esquerdo");
  Serial.println("    Comando: moveTo(0, 0)");
  AbsoluteMouse.moveTo(0, 0);
  Serial.println("    Enviado!");
  delay(2000);

  // TESTE 2: Centro (960, 540)
  Serial.println(">>> TESTE 2: Centro");
  Serial.println("    Comando: moveTo(960, 540)");
  AbsoluteMouse.moveTo(960, 540);
  Serial.println("    Enviado!");
  delay(2000);

  // TESTE 3: Canto Superior Direito (1919, 0)
  Serial.println(">>> TESTE 3: Canto Superior Direito");
  Serial.println("    Comando: moveTo(1919, 0)");
  AbsoluteMouse.moveTo(1919, 0);
  Serial.println("    Enviado!");
  delay(2000);

  // TESTE 4: Canto Inferior Direito (1919, 1079)
  Serial.println(">>> TESTE 4: Canto Inferior Direito");
  Serial.println("    Comando: moveTo(1919, 1079)");
  AbsoluteMouse.moveTo(1919, 1079);
  Serial.println("    Enviado!");
  delay(2000);

  // TESTE 5: Slot 1 (709, 1005)
  Serial.println(">>> TESTE 5: Slot 1");
  Serial.println("    Comando: moveTo(709, 1005)");
  AbsoluteMouse.moveTo(709, 1005);
  Serial.println("    Enviado!");
  delay(2000);

  // TESTE 6: Voltar ao centro
  Serial.println(">>> TESTE 6: Voltar ao centro");
  Serial.println("    Comando: moveTo(960, 540)");
  AbsoluteMouse.moveTo(960, 540);
  Serial.println("    Enviado!");
  delay(2000);

  Serial.println("");
  Serial.println("====================================");
  Serial.println("TESTES CONCLUIDOS!");
  Serial.println("====================================");
  Serial.println("");
  Serial.println("ANALISE:");
  Serial.println("- Se mouse foi para posicoes DIFERENTES = Funcionando!");
  Serial.println("- Se mouse ficou sempre no CENTRO = Problema de configuracao!");
  Serial.println("");
  Serial.println("Digite comandos manualmente agora:");
  Serial.println("Exemplo: MOVE:100:100");
  Serial.println("");
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

        Serial.print(">>> Recebido: MOVE:");
        Serial.print(x);
        Serial.print(":");
        Serial.println(y);

        Serial.print("    Enviando moveTo(");
        Serial.print(x);
        Serial.print(", ");
        Serial.print(y);
        Serial.println(")...");

        // ENVIAR COMANDO
        AbsoluteMouse.moveTo(x, y);

        Serial.print("    OK:MOVE:(");
        Serial.print(x);
        Serial.print(",");
        Serial.print(y);
        Serial.println(")");
        Serial.println("");
      } else {
        Serial.println("ERROR: Formato invalido! Use: MOVE:x:y");
      }
    } else if (command.equals("PING")) {
      Serial.println("PONG");
    } else {
      Serial.print("COMANDO DESCONHECIDO: ");
      Serial.println(command);
    }
  }
}
