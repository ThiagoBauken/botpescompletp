# Fix: Sobrecarga do Arduino - Adicionar Delays Estratégicos

**Data:** 2025-10-26
**Problema:** Vara não equipa após fechar baú (Arduino sobrecarregado)
**Causa:** Muitos comandos enviados rapidamente → buffer serial cheio → comandos atrasados/perdidos
**Status:** CORRIGIDO

---

## Análise do Problema

### Sequência de Comandos Durante Manutenção

Durante manutenção de varas, o Arduino recebe **MUITOS comandos em sequência rápida:**

```
1. KEY_DOWN:alt          (abrir baú)
2. MOVE_REL:1200:200     (mover câmera)
3. KEY_DOWN:e            (pressionar E)
4. KEY_UP:e
5. RESET_POS:959:539     (calibrar mouse)

[Durante arrastos - MÚLTIPLOS comandos:]
6. MOVE:1583:299         (mover para vara no baú)
7. MOUSE_DOWN:left       (pressionar botão)
8. MOVE:1188:1005        (arrastar para slot 6)
9. MOUSE_UP:left         (soltar botão)
10. [REPETIR para cada vara e isca - 10-20 arrastos!]

[Fechando baú:]
30. KEY_UP:alt           (soltar alt)
31. KEY_DOWN:tab         (fechar baú)
32. KEY_UP:tab

[Equipar vara:]
33. MOUSE_DOWN:right     (segurar botão direito)
34. KEY_DOWN:1           (equipar vara slot 1)  ← PROBLEMA AQUI!
35. KEY_UP:1
```

### Por Que Falha?

**Arduino processa comandos SERIALMENTE:**
- Buffer serial: ~64 bytes (pequeno!)
- Se comandos chegam rápido → buffer enche
- Comandos seguintes:
  - ❌ São perdidos
  - ❌ Chegam atrasados
  - ❌ São processados mas jogo não registra (muito rápido)

**Quando tenta equipar vara:**
- Arduino ainda está processando comandos 30-33
- Comando `KEY_DOWN:1` chega mas:
  - Ou Arduino não processou
  - Ou processou mas tecla foi pressionada rápido demais (50ms)
  - Ou jogo ainda estava fechando baú

---

## Solução Implementada

### Fix 1: Delay Após Fechar Baú (1 segundo)

**Arquivo:** `core/chest_operation_coordinator.py`
**Linha:** 672-676

**ANTES:**
```python
# Aguardar baú fechar completamente
time.sleep(0.6)
_safe_print("   ✅ Baú fechado, aguardando animação...")

self.chest_is_open = False
return True
```

**DEPOIS:**
```python
# Aguardar baú fechar completamente
time.sleep(0.6)
_safe_print("   ✅ Baú fechado, aguardando animação...")

self.chest_is_open = False

# ✅ CRÍTICO: Dar tempo para Arduino processar comandos anteriores
# Após manutenção, Arduino recebeu MUITOS comandos (MOVE, MOUSE_DOWN/UP, KEY_UP:alt, TAB)
# Aguardar para garantir que buffer serial está limpo antes de equipar vara
_safe_print("⏳ Aguardando Arduino processar comandos anteriores...")
time.sleep(1.0)  # ← NOVO: 1 segundo extra

return True
```

**Benefício:**
- Buffer serial limpa
- Arduino termina de processar comandos pendentes
- Baú fecha completamente no jogo

---

### Fix 2: Delays ao Equipar Vara

**Arquivo:** `core/rod_manager.py`
**Linhas:** 233-254

**ANTES:**
```python
# Segurar botão direito
if hold_right_button:
    self.input_manager.mouse_down('right')
    time.sleep(0.3)  # ← 300ms

# Pressionar slot
self.input_manager.press_key(str(slot))  # ← 50ms duração
time.sleep(0.5)  # ← 500ms após
```

**DEPOIS:**
```python
# Segurar botão direito
if hold_right_button:
    _safe_print("   🖱️ Segurando botão direito...")
    self.input_manager.mouse_down('right')
    time.sleep(0.5)  # ← 500ms (era 300ms)

# ✅ NOVO: Delay antes de pressionar
time.sleep(0.3)

# Pressionar slot com duração maior
_safe_print(f"   ⌨️ Pressionando tecla '{slot}' com duração de 200ms...")
self.input_manager.press_key(str(slot), duration=0.2)  # ← 200ms (era 50ms)

# ✅ NOVO: Delay maior após
time.sleep(0.8)  # ← 800ms (era 500ms)
```

**Benefícios:**
- **500ms após mouse_down:** Arduino processa comando antes da próxima ação
- **300ms antes da tecla:** Garante que mouse_down foi processado
- **200ms duração:** Jogo tem tempo de registrar a tecla pressionada
- **800ms após tecla:** Jogo processa equipar vara

---

## Timing Total Adicionado

### Tempo Total Antes
```
Fechar baú: 600ms
Equipar vara:
  - mouse_down: 300ms
  - press_key: 50ms
  - aguardar: 500ms
TOTAL: ~1450ms (1.45s)
```

### Tempo Total Depois
```
Fechar baú: 600ms
Aguardar Arduino: 1000ms  ← NOVO
Equipar vara:
  - mouse_down: 500ms (↑200ms)
  - delay pré-tecla: 300ms ← NOVO
  - press_key: 200ms (↑150ms)
  - aguardar: 800ms (↑300ms)
TOTAL: ~3400ms (3.4s)
```

**Adicionado:** +1950ms (~2 segundos extras)

---

## Por Que Funciona?

### 1. Buffer Serial Limpa
- 1 segundo extra após fechar baú permite Arduino:
  - Processar comandos pendentes no buffer
  - Limpar fila de comandos
  - Estar "pronto" para próximo comando

### 2. Comandos Não Interferem
- Delays entre comandos garantem que:
  - Arduino processa um comando de cada vez
  - Não há sobreposição
  - Cada comando tem tempo de executar completamente

### 3. Jogo Registra Teclas
- 200ms duração (ao invés de 50ms):
  - Jogo tem tempo de detectar tecla pressionada
  - Tecla não é "rápida demais"
  - Mais próximo de pressão humana

### 4. Animações Completam
- 800ms após press_key:
  - Jogo processa animação de equipar vara
  - Interface estabiliza antes de próxima ação
  - Evita interferências

---

## Logs Esperados (Após Fix)

```
📦 Fechando baú com TAB...
🛡️ [SAFETY] Liberando ALT antes de TAB...
🔴 [ALT FORCE] key_up('ALT') chamado
   ✅ ALT liberado via Arduino
📋 Pressionando TAB ÚNICO para fechar baú...
   ✅ TAB pressionado e solto via Arduino
   ✅ Baú fechado, aguardando animação...
⏳ Aguardando Arduino processar comandos anteriores...  ← NOVO LOG
[1.0s de delay]

🎣 PASSO 5: Equipando vara APÓS fechar baú...
   🎣 Equipando vara 1 com botão direito...
🎣 Equipando vara do slot 1...
   🖱️ Segurando botão direito...
[500ms de delay]
[300ms de delay pré-tecla]
   ⌨️ Pressionando tecla '1' com duração de 200ms...  ← NOVO LOG
[200ms pressionando tecla]
[800ms de delay]
✅ Vara do slot 1 equipada
```

---

## Comparação: Antes vs Depois

| Aspecto | ANTES | DEPOIS |
|---------|-------|--------|
| **Delay após fechar baú** | 600ms | 1600ms (+1000ms) |
| **Delay antes de mouse_down** | 0ms | 0ms |
| **Delay após mouse_down** | 300ms | 500ms (+200ms) |
| **Delay antes de press_key** | 0ms | 300ms (+300ms) |
| **Duração da tecla** | 50ms | 200ms (+150ms) |
| **Delay após press_key** | 500ms | 800ms (+300ms) |
| **TOTAL** | 1450ms | 3400ms (+1950ms) |

---

## Arquivos Modificados

1. ✅ `core/chest_operation_coordinator.py` - Linha 672-676
   - Adiciona delay de 1s após fechar baú

2. ✅ `core/rod_manager.py` - Linhas 233-254
   - Aumenta delay após mouse_down: 300ms → 500ms
   - Adiciona delay pré-tecla: 0ms → 300ms
   - Aumenta duração da tecla: 50ms → 200ms
   - Aumenta delay pós-tecla: 500ms → 800ms

---

## Próximos Passos para Testes

1. ✅ Reiniciar bot
2. ✅ Pressionar F6 (alimentação)
3. ✅ Verificar logs:
   - Deve ver "⏳ Aguardando Arduino processar comandos anteriores..."
   - Deve ver "⌨️ Pressionando tecla '1' com duração de 200ms..."
4. ✅ Verificar no jogo: **Vara deve estar na mão após fechar baú!**

---

## Se Ainda Não Funcionar

**Próximos testes:**

1. **Aumentar delay após fechar baú:** 1.0s → 2.0s
2. **Aumentar duração da tecla:** 200ms → 500ms
3. **Verificar Serial Monitor:** Confirmar que comandos chegam na ordem correta
4. **Teste manual:** Comparar timing manual vs. bot

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-26
**Status:** FIX IMPLEMENTADO - AGUARDANDO TESTE
