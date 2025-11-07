# 🎯 Arduino Sketch - Protocolo Híbrido

## ✅ Melhorias Implementadas

Integrei os melhores conceitos do código antigo mantendo a robustez do MouseTo.

---

## 🔄 O Que Foi Adicionado

### 1. **Comandos Curtos (Fast Path)**

Inspirado no código antigo - comandos de 1-6 caracteres para operações frequentes:

#### Mouse (3 caracteres)
```cpp
MLD  → Mouse.press(MOUSE_LEFT)    // Mouse Left Down
MLU  → Mouse.release(MOUSE_LEFT)  // Mouse Left Up
MRD  → Mouse.press(MOUSE_RIGHT)   // Mouse Right Down
MRU  → Mouse.release(MOUSE_RIGHT) // Mouse Right Up
```

#### Teclado (1-6 caracteres)
```cpp
// PRESS (tecla única)
w    → Keyboard.press('w')
a    → Keyboard.press('a')
s    → Keyboard.press('s')
d    → Keyboard.press('d')
e    → Keyboard.press('e')
tab  → Keyboard.press(KEY_TAB)
1-6  → Keyboard.press('1'-'6')  // Slots de vara
alt  → Keyboard.press(KEY_LEFT_ALT)

// RELEASE (tecla + "0")
w0   → Keyboard.release('w')
a0   → Keyboard.release('a')
s0   → Keyboard.release('s')
d0   → Keyboard.release('d')
e0   → Keyboard.release('e')
tab0 → Keyboard.release(KEY_TAB)
10-60 → Keyboard.release('1'-'6')
alt0 → Keyboard.release(KEY_LEFT_ALT)
```

**Vantagem:** Menos bytes via serial = mais rápido

---

### 2. **Movimento Relativo com Loop**

Inspirado no comando `BOX` do código antigo:

```cpp
// Formato: MOVE_REL_LOOP:dx:dy:count:delay_ms
// Exemplo do código antigo (BOX):
//   for (int i = 0; i < 8; i++) {
//     Mouse.move(-115, 43);
//     delay(50);
//   }

// Agora com nosso protocolo:
MOVE_REL_LOOP:-115:43:8:50
```

**Use cases:**
- Movimento de câmera repetido (ex: ajustar visão do jogo)
- Scroll em listas/inventário
- Movimentos padronizados (ex: abrir baú sempre no mesmo lugar relativo)

---

### 3. **Movimento Relativo Simples**

Para casos onde movimento absoluto não é necessário:

```cpp
MOVE_REL:100:-50  → Mouse.move(100, -50)
```

**Quando usar:**
- Ajustes finos de posição
- Movimento de câmera 3D (onde posição absoluta não importa)
- Compensação de drift

---

## 📊 Protocolo Completo Atualizado

### **Tier 1: Comandos Curtos (Fast)**
| Comando | Bytes | Descrição |
|---------|-------|-----------|
| `MLD` | 3 | Mouse left down |
| `MLU` | 3 | Mouse left up |
| `MRD` | 3 | Mouse right down |
| `MRU` | 3 | Mouse right up |
| `w` | 1 | Press W |
| `w0` | 2 | Release W |
| `1` | 1 | Press 1 (slot vara) |
| `10` | 2 | Release 1 |

### **Tier 2: Comandos Longos (Robust)**
| Comando | Exemplo | Descrição |
|---------|---------|-----------|
| `MOVE:x:y` | `MOVE:960:540` | Move absoluto (MouseTo) |
| `CLICK:x:y` | `CLICK:1350:450` | Clique em posição |
| `RIGHT_CLICK:x:y` | `RIGHT_CLICK:800:500` | Clique direito |
| `DRAG:x1:y1:x2:y2` | `DRAG:1350:450:899:1005` | Arrastar item |
| `MOVE_REL:dx:dy` | `MOVE_REL:100:-50` | Move relativo |
| `MOVE_REL_LOOP:dx:dy:n:ms` | `MOVE_REL_LOOP:-115:43:8:50` | Loop movimento |
| `KEY_PRESS:key` | `KEY_PRESS:TAB` | Tecla especial |

---

## 🎮 Exemplos Práticos

### Pesca - Ciclo Completo

```python
# Python envia comandos curtos durante pesca:
serial.write(b"MRD\n")              # Segurar botão direito (1.6s)
time.sleep(1.6)

serial.write(b"MLD\n")              # Começar cliques rápidos
time.sleep(7.5)
serial.write(b"MLU\n")

serial.write(b"a\n")                # Movimento câmera esquerda
time.sleep(1.5)
serial.write(b"a0\n")

serial.write(b"d\n")                # Movimento câmera direita
time.sleep(1.2)
serial.write(b"d0\n")
```

**Comparação:**
- Comandos longos: `KEY_DOWN:a\n` (10 bytes)
- Comandos curtos: `a\n` (2 bytes)
- **80% menos dados!**

---

### Manutenção de Vara

```python
# 1. Detectar isca em (1350, 450)
# 2. Arrastar para slot 3 em (899, 1005)

# Comando longo (preciso com MouseTo):
serial.write(b"DRAG:1350:450:899:1005\n")

# Arduino executa:
# - Move absoluto para (1350, 450) com MouseTo
# - Segura botão esquerdo
# - Move absoluto para (899, 1005) suavemente
# - Solta botão
```

---

### Ajuste de Câmera (Relativo)

```python
# Ajustar câmera do jogo (movimento relativo repetido)
# Equivalente ao comando "BOX" do código antigo

serial.write(b"MOVE_REL_LOOP:-115:43:8:50\n")

# Arduino executa:
# for (i = 0; i < 8; i++) {
#   Mouse.move(-115, 43);
#   delay(50);
# }
```

---

## 🚀 Otimizações de Performance

### Antes (Comandos Longos)

```python
# Ciclo de pesca (7.5s de cliques rápidos)
for _ in range(90):  # 12 cliques/segundo * 7.5s
    serial.write(b"KEY_DOWN:MOUSE_LEFT\n")  # 20 bytes
    time.sleep(0.05)
    serial.write(b"KEY_UP:MOUSE_LEFT\n")    # 18 bytes
    time.sleep(0.03)

# Total: 90 * 38 bytes = 3420 bytes
```

### Depois (Comandos Curtos)

```python
# Segurar botão durante 7.5s (jogo detecta como cliques)
serial.write(b"MLD\n")  # 4 bytes
time.sleep(7.5)
serial.write(b"MLU\n")  # 4 bytes

# Total: 8 bytes
# 🚀 99.7% menos dados!
```

---

## 📋 Quando Usar Cada Tipo

### **Use Comandos Curtos quando:**
- ✅ Operação frequente (ex: pressionar tecla A/D)
- ✅ Baixa latência necessária
- ✅ Não precisa de coordenadas

### **Use Comandos Longos quando:**
- ✅ Operação com coordenadas (MOVE, CLICK, DRAG)
- ✅ Teclas especiais (F1-F12, PAGE_UP, etc.)
- ✅ Precisa de feedback detalhado (parsing de resposta)

### **Use Movimento Relativo quando:**
- ✅ Ajustar câmera 3D
- ✅ Compensar drift de posição
- ✅ Movimento padronizado repetido (loop)

### **Use MouseTo (absoluto) quando:**
- ✅ Clicar em UI do jogo
- ✅ Arrastar itens (drag & drop)
- ✅ Precisão crítica (slots de vara, iscas, etc.)

---

## 🔧 Configurações Ajustáveis

No topo do sketch:

```cpp
// Timeouts
#define MOVE_TIMEOUT_MS 200      // Movimento absoluto (MouseTo)
#define DRAG_PAUSE_START_MS 200  // Pausa início drag
#define DRAG_PAUSE_END_MS 400    // Pausa fim drag
#define DRAG_STEP_DELAY_MS 5     // Suavidade do drag

// Correção MouseTo (ajustar se impreciso)
MouseTo.setCorrectionFactor(1);  // 0.9-1.1
```

---

## 📊 Comparação Final

| Recurso | Código Antigo | Nosso Híbrido |
|---------|--------------|---------------|
| **Comandos curtos** | ✅ Sim | ✅ Sim |
| **Movimento absoluto** | ❌ Não | ✅ MouseTo |
| **Movimento relativo** | ✅ Sim | ✅ Sim + Loop |
| **Drag & drop** | ❌ Manual | ✅ Automático |
| **Tratamento de erros** | ❌ Não | ✅ Timeouts |
| **Feedback serial** | ❌ Não | ✅ OK/ERROR |
| **Parsing estruturado** | ❌ Hardcoded | ✅ Modular |

---

## ✅ Resultado

**Combinamos:**
- ✅ **Velocidade** dos comandos curtos (código antigo)
- ✅ **Precisão** do MouseTo (movimento absoluto)
- ✅ **Robustez** do tratamento de erros
- ✅ **Flexibilidade** de movimento relativo + loop

**Código final:**
- 520 linhas (bem organizado)
- Suporta 2 protocolos (curto + longo)
- Compatível com código antigo (comandos curtos)
- Estendido com MouseTo (movimento absoluto preciso)

---

## 🧪 Testes Sugeridos

### 1. Teste de Comandos Curtos
```python
import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)

# Teste mouse
ser.write(b"MLD\n")  # Segurar esquerdo
time.sleep(1)
ser.write(b"MLU\n")  # Soltar

# Teste teclado
ser.write(b"d\n")    # Pressionar D
time.sleep(0.5)
ser.write(b"d0\n")   # Soltar D
```

### 2. Teste de Movimento Relativo Loop
```python
# Mover câmera em padrão
ser.write(b"MOVE_REL_LOOP:-100:0:5:100\n")  # 5x para esquerda
time.sleep(1)
ser.write(b"MOVE_REL_LOOP:100:0:5:100\n")   # 5x para direita (volta)
```

### 3. Teste de Drag Absoluto
```python
# Arrastar item de (500, 300) para (700, 500)
ser.write(b"DRAG:500:300:700:500\n")
response = ser.readline().decode().strip()
print(f"Arduino: {response}")  # OK:DRAG:(500,300)→(700,500)
```

---

## 🎯 Próximos Passos

1. ✅ Sketch atualizado com comandos híbridos
2. ⏳ Criar wrapper Python no InputManager
3. ⏳ Testar comunicação serial
4. ⏳ Validar no jogo (manutenção varas, feeding, etc.)

Quer que eu crie o **wrapper Python** agora para integrar este protocolo no InputManager?
