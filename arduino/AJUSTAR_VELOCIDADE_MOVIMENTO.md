# ⚙️ Ajustar Velocidade e Precisão do Movimento

## 🎯 Configurações no Topo do Sketch (linhas 63-68)

```cpp
// Configurações de movimento
#define MOVE_TIMEOUT_MS 4000       // Timeout para alcançar alvo (4 segundos)
#define MOVE_STEP_DELAY_MS 3       // ← AJUSTAR AQUI: Delay entre movimentos
#define MOUSETO_MAX_JUMP 5         // ← AJUSTAR AQUI: Pixels por movimento
#define DRAG_PAUSE_START_MS 200    // Pausa ao chegar no início do drag
#define DRAG_PAUSE_END_MS 400      // Pausa ao chegar no fim do drag
#define DRAG_STEP_DELAY_MS 8       // ← AJUSTAR AQUI: Delay para drag
```

---

## 🐌 Para Movimento MAIS LENTO e HUMANIZADO

### Opção 1: Movimento Muito Suave (Recomendado)
```cpp
#define MOVE_STEP_DELAY_MS 5       // 5ms entre cada movimento
#define MOUSETO_MAX_JUMP 3         // 3 pixels por vez
```

**Resultado:**
- 🐌 Muito lento e suave
- ✅ Mais humano
- ⏱️ Leva ~1-2 segundos para mover pela tela

---

### Opção 2: Movimento Médio (Balanceado)
```cpp
#define MOVE_STEP_DELAY_MS 3       // 3ms entre cada movimento
#define MOUSETO_MAX_JUMP 5         // 5 pixels por vez
```

**Resultado:**
- 🐇 Velocidade média
- ✅ Ainda parece humano
- ⏱️ Leva ~0.5-1 segundo

---

### Opção 3: Movimento Rápido
```cpp
#define MOVE_STEP_DELAY_MS 1       // 1ms entre cada movimento
#define MOUSETO_MAX_JUMP 10        // 10 pixels por vez
```

**Resultado:**
- 🚀 Rápido
- ⚠️ Menos natural
- ⏱️ Leva ~0.3 segundos

---

## 🎯 Para Ajustar PRECISÃO

Se o mouse **não para no local correto**:

### Problema: Mouse vai ALÉM do alvo

**Solução:** Diminuir o fator de correção

```cpp
void setup() {
  // ...
  MouseTo.setCorrectionFactor(0.95);  // Reduz 5%
}
```

Valores para testar: `0.90`, `0.92`, `0.95`, `0.97`

---

### Problema: Mouse NÃO CHEGA no alvo

**Solução:** Aumentar o fator de correção

```cpp
void setup() {
  // ...
  MouseTo.setCorrectionFactor(1.05);  // Aumenta 5%
}
```

Valores para testar: `1.03`, `1.05`, `1.08`, `1.10`

---

## 🧪 Teste de Calibração

### 1. Testar Centro da Tela
```
MOVE:960:540
```

**Verificar:**
- Mouse chegou **exatamente** no centro da tela?
- Se passou → Diminuir `correctionFactor`
- Se faltou → Aumentar `correctionFactor`

---

### 2. Testar Slot de Vara
```
MOVE:709:1005
```

**Verificar:**
- Mouse está **exatamente** sobre o slot da vara?
- Se não → Ajustar `correctionFactor`

---

### 3. Testar Precisão nos 4 Cantos

```
MOVE:0:0          # Canto superior esquerdo
MOVE:1920:0       # Canto superior direito
MOVE:0:1080       # Canto inferior esquerdo
MOVE:1920:1080    # Canto inferior direito
```

**Verificar:**
- Mouse vai para todos os cantos corretamente?
- Se errar → Problema no `setScreenResolution`

---

## 📊 Interpretando os Logs de Debug

Quando você envia `MOVE:709:1005`, aparece:

```
DEBUG:MOVES=54,TIME=58ms
OK:MOVE:(709,1005)
```

**Interpretação:**
- `MOVES=54` → Foram 54 chamadas de `MouseTo.move()`
- `TIME=58ms` → Levou 58 milissegundos

---

### Cálculo de Velocidade

```
Distância = 709 - 960 = -251 pixels (aprox)
Pixels por segundo = 251 / 0.058 = 4327 px/s
```

**Como tornar mais lento:**

**Exemplo 1:** Aumentar delay
```cpp
#define MOVE_STEP_DELAY_MS 10  // 10ms (3x mais lento)
```

Resultado: `TIME=150ms` (aproximadamente)

---

**Exemplo 2:** Diminuir maxJump
```cpp
#define MOUSETO_MAX_JUMP 2  // 2 pixels por vez
```

Resultado: Mais passos, movimento mais suave

---

## 🎮 Configurações Recomendadas por Uso

### Para Pesca (Movimento Normal)
```cpp
#define MOVE_STEP_DELAY_MS 3
#define MOUSETO_MAX_JUMP 5
#define DRAG_STEP_DELAY_MS 8
```

### Para Manutenção de Varas (Drag Preciso)
```cpp
#define MOVE_STEP_DELAY_MS 3
#define MOUSETO_MAX_JUMP 5
#define DRAG_STEP_DELAY_MS 10  // Drag mais lento
```

### Para Movimento Muito Humano (Anti-detecção)
```cpp
#define MOVE_STEP_DELAY_MS 8
#define MOUSETO_MAX_JUMP 3
#define DRAG_STEP_DELAY_MS 15
```

---

## 🔄 Fluxo de Ajuste

```
1. Fazer upload do sketch
2. Testar: MOVE:960:540
3. Observar velocidade e precisão
4. Se muito rápido → Aumentar MOVE_STEP_DELAY_MS
5. Se impreciso → Ajustar correctionFactor
6. Repetir até satisfeito
7. Testar DRAG:500:300:700:500
8. Se drag muito rápido → Aumentar DRAG_STEP_DELAY_MS
```

---

## ✅ Configuração Final Recomendada

Após testes, use esta configuração:

```cpp
// Configurações de movimento
#define MOVE_TIMEOUT_MS 4000       // 4 segundos timeout
#define MOVE_STEP_DELAY_MS 5       // 5ms = movimento suave
#define MOUSETO_MAX_JUMP 4         // 4 pixels = preciso
#define DRAG_PAUSE_START_MS 200
#define DRAG_PAUSE_END_MS 400
#define DRAG_STEP_DELAY_MS 12      // 12ms = drag muito humano

void setup() {
  // ...
  MouseTo.setScreenResolution(1920, 1080);
  MouseTo.setCorrectionFactor(1.0);  // Ajustar conforme necessário
  MouseTo.setMaxJump(MOUSETO_MAX_JUMP);
}
```

---

## 🎯 Teste Final

Após ajustar, teste estes comandos:

```
MOVE:960:540        # Centro (deve levar ~0.5-1s)
MOVE:709:1005       # Slot vara 1
MOVE:1350:450       # Posição de isca
DRAG:1350:450:709:1005  # Arrastar isca para vara
```

**✅ Sucesso se:**
- Mouse move suavemente
- Mouse para exatamente no alvo
- Drag é suave e preciso
- Parece movimento humano

---

## 📝 Logs Esperados (Movimento Otimizado)

```
DEBUG:MOVES=120,TIME=600ms
OK:MOVE:(960,540)
```

- `MOVES=120` → Muitos passos pequenos = suave
- `TIME=600ms` → Tempo razoável = não muito rápido

Se `TIME` for menor que 200ms → Muito rápido!
Se `TIME` for maior que 2000ms → Muito lento!

---

## 🚀 Aplicar Configurações

1. Editar linhas 63-68 do sketch
2. Salvar (Ctrl+S)
3. Upload (Ctrl+U)
4. Testar movimentos
5. Repetir ajustes até perfeito

Boa sorte! 🎯
