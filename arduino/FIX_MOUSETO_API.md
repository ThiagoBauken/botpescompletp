# 🔧 Correção da API MouseTo

## ❌ Problema Identificado

Erro de compilação:
```
error: 'class MouseToClass' has no member named 'atTarget'
```

## 🔍 Causa

Assumi API incorreta para a biblioteca MouseTo. A biblioteca **não possui** método `atTarget()`.

---

## ✅ API Correta do MouseTo

### Métodos Principais

```cpp
// 1. Definir alvo (coordenadas absolutas)
MouseTo.setTarget(x, y);

// 2. Mover em direção ao alvo
bool reached = MouseTo.move();
// Retorna: true = chegou ao alvo, false = ainda não chegou

// 3. Configuração (opcional)
MouseTo.setCorrectionFactor(1.0);         // Ajuste fino de precisão
MouseTo.setScreenResolution(1920, 1080);  // Resolução da tela
MouseTo.setMaxJump(10);                   // Máximo de pixels por passo
```

### **Como Funciona:**

1. `MouseTo.move()` **retorna `true`** quando atinge o alvo
2. Múltiplas chamadas de `move()` são necessárias para alvos distantes
3. Cada chamada move até `maxJump` pixels (padrão: 10px)

---

## 🛠️ Correções Aplicadas

### **Antes (ERRADO):**

```cpp
bool moveToPosition(int x, int y) {
  MouseTo.setTarget(x, y);

  while (!MouseTo.atTarget()) {  // ❌ ERRO: atTarget() não existe!
    MouseTo.move();
    delay(1);
  }

  return true;
}
```

### **Depois (CORRETO):**

```cpp
bool moveToPosition(int x, int y) {
  MouseTo.setTarget(x, y);

  unsigned long startTime = millis();
  while (true) {
    // ✅ MouseTo.move() retorna true quando chegou ao alvo
    if (MouseTo.move()) {
      return true;  // Alvo alcançado!
    }

    delay(1);

    // Timeout de segurança
    if (millis() - startTime > MOVE_TIMEOUT_MS) {
      return false;
    }
  }
}
```

---

## 📊 Lógica do Movimento

### Exemplo: Mover de (0, 0) para (100, 100)

```cpp
MouseTo.setTarget(100, 100);  // Define alvo

// Chamada 1: MouseTo.move() → Move (10, 10) → retorna false
// Chamada 2: MouseTo.move() → Move (10, 10) → retorna false
// Chamada 3: MouseTo.move() → Move (10, 10) → retorna false
// ...
// Chamada 10: MouseTo.move() → Move (10, 10) → retorna true! (chegou)
```

**Total:** ~10 chamadas para mover 100 pixels (maxJump=10)

---

## 🎯 Funções Corrigidas

### 1. `moveToPosition()` - Movimento Rápido

```cpp
bool moveToPosition(int x, int y) {
  MouseTo.setTarget(x, y);
  unsigned long startTime = millis();

  while (true) {
    if (MouseTo.move()) return true;  // ✅ Chegou!
    delay(1);                          // 1ms entre movimentos

    if (millis() - startTime > 200) return false;  // Timeout 200ms
  }
}
```

**Uso:** Movimentos normais (CLICK, MOVE)

---

### 2. `moveToPositionSlow()` - Movimento Suave

```cpp
bool moveToPositionSlow(int x, int y, int stepDelayMs) {
  MouseTo.setTarget(x, y);
  unsigned long startTime = millis();

  while (true) {
    if (MouseTo.move()) return true;  // ✅ Chegou!
    delay(stepDelayMs);                // 5ms entre movimentos (DRAG)

    if (millis() - startTime > 600) return false;  // Timeout 600ms
  }
}
```

**Uso:** DRAG (movimento lento para simular humano)

---

## 🧪 Teste de Validação

### Código de Teste

```cpp
void setup() {
  Serial.begin(115200);
  Mouse.begin();
  MouseTo.setCorrectionFactor(1);

  // Testar movimento para (960, 540) - centro da tela 1920x1080
  Serial.println("Movendo para centro...");
  MouseTo.setTarget(960, 540);

  int calls = 0;
  while (true) {
    if (MouseTo.move()) {
      Serial.print("Alvo alcançado em ");
      Serial.print(calls);
      Serial.println(" chamadas");
      break;
    }
    calls++;
    delay(1);
  }
}
```

**Saída Esperada:**
```
Movendo para centro...
Alvo alcançado em 96 chamadas
```

---

## ⚙️ Configurações Recomendadas

### Para Tela 1920x1080

```cpp
void setup() {
  // ...

  // Definir resolução da tela (melhora performance do homing)
  MouseTo.setScreenResolution(1920, 1080);

  // Fator de correção (ajustar se movimento impreciso)
  MouseTo.setCorrectionFactor(1.0);  // Testar valores 0.9-1.1

  // MaxJump = 10 (padrão) é bom para precisão
  // Valores maiores = mais rápido, menos preciso
  MouseTo.setMaxJump(10);
}
```

---

## 📝 Calibração

Se os movimentos não chegarem exatamente no alvo:

### 1. Testar Fator de Correção

```cpp
// Muito curto? Aumentar fator
MouseTo.setCorrectionFactor(1.05);  // +5%

// Muito longe? Diminuir fator
MouseTo.setCorrectionFactor(0.95);  // -5%
```

### 2. Usar MousePosition.html

Incluído na biblioteca em `extras/MousePosition.html`:
- Abrir no navegador
- Mover mouse e verificar coordenadas
- Comparar com alvo esperado

---

## ✅ Resultado

**Compilação:** ✅ OK
**API:** ✅ Correta
**Timeout:** ✅ Implementado
**Performance:** ✅ Otimizado (1ms delay = ~1000 checks/segundo)

---

## 🚀 Próximos Passos

1. ✅ Sketch corrigido e compilando
2. ⏳ Fazer upload no Arduino
3. ⏳ Testar movimento com Serial Monitor
   ```
   Enviar: MOVE:960:540
   Esperar: OK:MOVE:(960,540)
   ```
4. ⏳ Validar precisão (mouse deve chegar exatamente no alvo)
5. ⏳ Ajustar `correctionFactor` se necessário
6. ⏳ Integrar ao InputManager Python
