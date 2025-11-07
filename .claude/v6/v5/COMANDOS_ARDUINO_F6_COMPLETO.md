# 📋 COMANDOS ARDUINO F6 (FEEDING) - SEQUÊNCIA COMPLETA

**Data:** 2025-10-22
**Função:** Alimentação automática (F6)
**Arduino:** Conectado

---

## 🔄 SEQUÊNCIA COMPLETA DE COMANDOS

### **FASE 0: PREPARAÇÃO (ANTES DE ABRIR BAÚ)**

```python
# 0.1: Liberar ALT preventivamente
→ Arduino: KEY_UP:ALT
← Arduino: OK:KEY_UP

# 0.2: Soltar botões do mouse
→ Arduino: MOUSE_UP:R
← Arduino: OK:MOUSE_UP:R
→ Arduino: MOUSE_UP:L
← Arduino: OK:MOUSE_UP:L

# 0.3: Parar ações contínuas do fishing cycle
→ Arduino: (stop_continuous_clicking() - para threads internas)
→ Arduino: (stop_camera_movement() - para threads internas)
```

---

### **FASE 1: ABERTURA DO BAÚ (chest_operation_coordinator.py)**

```python
# 1.1: Pressionar ALT
→ Arduino: KEY_DOWN:ALT
← Arduino: OK:KEY_DOWN

# Aguardar 0.5s (com ALT pressionado)

# 1.2: Movimento da câmera (API Windows - não usa Arduino!)
# _camera_turn_in_game(delta_x, delta_y)
# Config: chest_side='left', chest_distance=1200
# DX = -1200 (esquerda)
# DY = 200 (para baixo)
# Método: pywin32 API ou PyAutoGUI (NÃO Arduino!)

# 1.3: Pressionar E
→ Arduino: KEY_PRESS:e
← Arduino: OK:KEY_PRESS

# Aguardar 0.5s

# 1.4: Soltar ALT
→ Arduino: KEY_UP:ALT
← Arduino: OK:KEY_UP

# Aguardar 0.2s

# ✅ JOGO TELEPORTA MOUSE PARA (959, 539) AUTOMATICAMENTE!

# Aguardar 0.5s

# 1.5: CALIBRAR MouseTo (CRÍTICO!)
→ Arduino: RESET_POS:959:539
← Arduino: OK:RESET_POS:(959,539)
# OU (se AbsMouse):
← Arduino: OK:RESET_POS:(959,539):NOT_NEEDED
```

**⚠️ NOTA IMPORTANTE:**
- O movimento de câmera durante ALT **NÃO USA ARDUINO!**
- Usa API Windows (`pywin32`) ou PyAutoGUI
- Arduino é usado apenas para ALT e E
- Após abrir baú, jogo posiciona mouse em (959, 539) automaticamente
- `RESET_POS` informa ao Arduino onde o mouse está (sem mover!)

---

### **FASE 2: DETECÇÃO DE COMIDA (feeding_system.py)**

```python
# 2.1: Template matching (Python/OpenCV - não usa Arduino)
# Detecta 'filefrito' template na tela
# Exemplo: encontrado em (1350, 750)

# 2.2: Clicar na comida inicial
# click(1350, 750) é chamado:

# 2.2.1: Mover mouse para comida
→ Arduino: MOVE:1350:750
← Arduino: OK:MOVE:(1350,750)

# Aguardar 0.05s

# 2.2.2: Pressionar botão esquerdo
→ Arduino: MOUSE_DOWN:L
← Arduino: OK:MOUSE_DOWN:L

# Aguardar 0.1s (botão pressionado)

# 2.2.3: Soltar botão esquerdo
→ Arduino: MOUSE_UP:L
← Arduino: OK:MOUSE_UP:L

# Aguardar 1.0s (UI estabilizar)
```

---

### **FASE 3: LOOP DE ALIMENTAÇÃO (feed_count vezes)**

Exemplo: `feed_count = 2` (configurado na UI)

#### **ITERAÇÃO 1 - Primeira Comida:**

```python
# 3.1: Detectar botão 'eat' (template matching - Python/OpenCV)
# Exemplo: encontrado em (1083, 373)

# 3.2: Clicar no botão eat
# click(1083, 373):

# 3.2.1: Mover para eat
→ Arduino: MOVE:1083:373
← Arduino: OK:MOVE:(1083,373)

# Aguardar 0.05s

# 3.2.2: Pressionar esquerdo
→ Arduino: MOUSE_DOWN:L
← Arduino: OK:MOUSE_DOWN:L

# Aguardar 0.1s

# 3.2.3: Soltar esquerdo
→ Arduino: MOUSE_UP:L
← Arduino: OK:MOUSE_UP:L

# Aguardar 1.5s (após eat)
# Aguardar 0.5s (antes do próximo ciclo)
```

#### **ITERAÇÃO 2 - Segunda Comida:**

```python
# 3.3: RE-detectar botão 'eat' (posição pode mudar!)
# Exemplo: agora em (1100, 380)

# 3.4: Clicar no eat novamente
# click(1100, 380):

→ Arduino: MOVE:1100:380
← Arduino: OK:MOVE:(1100,380)

# Aguardar 0.05s

→ Arduino: MOUSE_DOWN:L
← Arduino: OK:MOUSE_DOWN:L

# Aguardar 0.1s

→ Arduino: MOUSE_UP:L
← Arduino: OK:MOUSE_UP:L

# Aguardar 1.5s (após último eat)
# Aguardar 0.5s (após última comida)
```

**IMPORTANTE:**
- Botão "eat" **muda de posição** quando é a última comida!
- Por isso, **sempre re-detecta** a cada clique
- Se não detectar eat: tenta buscar nova comida em outro slot
- Se não há mais comida: para o loop

---

### **FASE 4: FECHAMENTO DO BAÚ**

```python
# 4.1: Pressionar ESC
→ Arduino: KEY_PRESS:ESC
← Arduino: OK:KEY_PRESS

# Aguardar 0.3s

# Baú fechado!
```

---

## 📊 RESUMO DE COMANDOS ARDUINO

### **Comandos de Teclado:**
```
KEY_DOWN:ALT       - Segurar ALT (abertura baú)
KEY_UP:ALT         - Soltar ALT (3 vezes: preventivo, após baú, erro)
KEY_PRESS:e        - Pressionar E (abrir baú)
KEY_PRESS:ESC      - Pressionar ESC (fechar baú)
```

### **Comandos de Mouse:**
```
MOUSE_DOWN:L       - Pressionar botão esquerdo (cliques)
MOUSE_UP:L         - Soltar botão esquerdo (cliques)
MOUSE_DOWN:R       - Pressionar botão direito (segurança)
MOUSE_UP:R         - Soltar botão direito (segurança)
```

### **Comandos de Movimento:**
```
RESET_POS:959:539  - Calibrar posição após abrir baú
MOVE:x:y           - Mover para coordenadas absolutas
```

---

## 🔢 CONTAGEM TOTAL (EXEMPLO: 2 COMIDAS)

| Fase | Comando | Quantidade |
|------|---------|------------|
| Preparação | KEY_UP:ALT | 1 |
| Preparação | MOUSE_UP:R | 1 |
| Preparação | MOUSE_UP:L | 1 |
| Abertura | KEY_DOWN:ALT | 1 |
| Abertura | KEY_PRESS:e | 1 |
| Abertura | KEY_UP:ALT | 1 |
| Calibração | RESET_POS:959:539 | 1 |
| Comida inicial | MOVE:x:y | 1 |
| Comida inicial | MOUSE_DOWN:L | 1 |
| Comida inicial | MOUSE_UP:L | 1 |
| Loop (2x) | MOVE:x:y | 2 |
| Loop (2x) | MOUSE_DOWN:L | 2 |
| Loop (2x) | MOUSE_UP:L | 2 |
| Fechamento | KEY_PRESS:ESC | 1 |
| **TOTAL** | | **17 comandos** |

---

## ⚠️ MOVIMENTOS QUE **NÃO** USAM ARDUINO

### **1. Movimento de Câmera Durante ALT:**

Durante `_camera_turn_in_game(delta_x, delta_y)`:
```python
# ❌ NÃO USA ARDUINO!
# Usa API Windows (pywin32) ou PyAutoGUI

# Windows API:
import ctypes
for i in range(num_steps):
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0)
    time.sleep(0.01)

# OU PyAutoGUI (fallback):
pyautogui.move(dx, dy, duration=0.3)
```

**Por quê?**
- Durante ALT (freelook), cursor fica invisível
- Movimento é **relativo** (não absoluto)
- API Windows ou PyAutoGUI move câmera diretamente
- Arduino **não** é usado para este movimento!

---

## 🎯 ONDE OS PROBLEMAS PODEM OCORRER

### **Problema 1: Mouse vai para canto direito após RESET_POS**

**Causa:** MouseTo tem estado interno que desincroniza

**Solução:** Usar AbsMouse (sem estado interno)

### **Problema 2: Primeiro MOVE vai errado**

**Causa:** RESET_POS não atualiza posição interna do MouseTo corretamente

**Debug:**
```python
# Logs esperados:
🎯 [COORDINATOR] Calibrando Arduino MouseTo...
   📤 Comando: RESET_POS:959:539
   📥 Resposta: OK:RESET_POS:(959,539)
   ✅ MouseTo sincronizado!

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (959, 539)
   🎯 Destino: (1350, 750)
   ➡️  Delta: (+391, +211)
   📤 Comando: MOVE:1350:750
   📥 Resposta: OK:MOVE:(1350,750)
   🔍 Verificação:
      Esperado: (1350, 750)
      Real: (1350, 750)  ← ✅ DEVE SER EXATO!
      Erro: (0, 0)  ← ✅ ZERO!
```

Se aparecer:
```
Real: (1919, 1079)  ← ❌ ERRADO!
Erro: (-569, -329)
```

Então MouseTo está com estado interno errado!

### **Problema 3: center_camera() usa PyAutoGUI**

**Causa:** `chest_manager.center_camera()` pode executar **ANTES** da calibração

**Código problemático** (chest_manager.py linha 158):
```python
if self.input_manager and hasattr(self.input_manager, 'move_to'):
    self.input_manager.move_to(target_x, target_y)  # Arduino
else:
    pyautogui.moveTo(target_x, target_y)  # ← PROBLEMA!
```

**Verificar logs:**
```
✅ [CHEST] Câmera centralizada via Arduino  ← BOM!
⚠️ [CHEST] Câmera centralizada via pyautogui (fallback)  ← RUIM!
```

Se aparecer "via pyautogui", então Arduino **não está conectado**!

---

## 🧪 COMO TESTAR

### **Teste 1: Verificar se Arduino está conectado**

```python
# No bot, antes de F6:
# Aba Arduino → Conectar
# Aguardar: "✅ Arduino conectado"
```

### **Teste 2: Verificar sequência completa**

```python
# Pressionar F6
# Verificar logs:

# DEVE aparecer:
🛡️ [SAFETY] ALT liberado via Arduino
✅ ALT pressionado via Arduino
✅ E pressionado via Arduino
✅ ALT liberado via Arduino
🎯 [COORDINATOR] Calibrando Arduino MouseTo...
📤 Comando: RESET_POS:959:539
📥 Resposta: OK:RESET_POS:(959,539)
✅ [COORDINATOR] Arduino calibrado!

# Se aparecer:
⚠️ ALT pressionado via PyAutoGUI (Arduino não disponível)
# Então Arduino NÃO está conectado!
```

### **Teste 3: Verificar movimento de comida**

```python
# Após calibração, primeiro MOVE deve ser EXATO:

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (959, 539)
   🎯 Destino: (1350, 750)
   ➡️  Delta: (+391, +211)
   📤 Comando: MOVE:1350:750
   📥 Resposta: OK:MOVE:(1350,750)
   🔍 Verificação:
      Esperado: (1350, 750)
      Real: (1350, 750)  ← DEVE SER EXATO!
      Erro: (0, 0)

# Se erro > 50px, há problema!
```

---

## 📝 LOGS COMPLETOS EXEMPLO (F6 com 2 comidas)

```
🍖 [F6] Executando alimentação manual...

================================================================================
🍖 EXECUTANDO ALIMENTAÇÃO AUTOMÁTICA
================================================================================
📦 PASSO 1: Abrindo baú para alimentação...

==================================================
📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E
==================================================
🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente
Config: lado=left, distância=1200px
🛡️ [SAFETY] Liberando ALT preventivamente...
   ✅ ALT liberado via Arduino

[1/5] Soltando botões do mouse...
   🛡️ [SAFETY] Botões liberados via InputManager (estado atualizado)

[1.5/5] Parando ações contínuas do fishing cycle...
   ✅ Cliques contínuos interrompidos
   ✅ Movimentos A/D interrompidos (teclas liberadas)
   🛡️ [SAFETY] Fishing cycle limpo - pronto para operações de baú

[2/5] Pressionando ALT...
   ✅ ALT pressionado via Arduino

[3/5] Calculando movimento da câmera...
   Deslocamento: -1200px horizontal

[4/5] Movendo câmera com API Windows...
   Movimento: DX=-1200, DY=200
   ✅ Câmera movida com API Windows!

[5/5] Pressionando E...
   ✅ E pressionado via Arduino

[6/5] Soltando ALT...
   ✅ ALT liberado via Arduino

✅ BAÚ ABERTO COM SUCESSO!
==================================================

🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado

🎯 [COORDINATOR] Calibrando Arduino MouseTo...

🎯 [ARDUINO] CALIBRANDO MOUSETO:
   📍 Posição atual do cursor: (959, 539)
   🔄 Sincronizando MouseTo para: (959, 539)
   📤 Comando: RESET_POS:959:539
   ⚠️  IMPORTANTE: Este comando NÃO move o cursor!
   ℹ️  Apenas informa ao Arduino onde o cursor ESTÁ
   📥 Resposta: OK:RESET_POS:(959,539)
   ✅ MouseTo sincronizado!
   ℹ️  Próximos MOVE: serão calculados a partir de (959, 539)

✅ [COORDINATOR] Arduino calibrado! Movimentos serão precisos.

✅ Baú aberto com sucesso
🔍 PASSO 3: Detectando e clicando na comida...
🔍 Executando alimentação inteligente com detecção dinâmica...
🔍 Modo detecção automática - buscando filé frito e botão eat...
✅ COMIDA ENCONTRADA: filefrito em (1350, 750) - Conf: 0.823
🔍 Procurando botão 'eat' na tela...
✅ BOTÃO 'EAT' ENCONTRADO DINAMICAMENTE em (1083, 373)
🍽️ Executando sequência de alimentação automática...
🔢 Configurado para comer 2 vezes

🍖 [FEEDING] CLICANDO NA COMIDA INICIAL:
   📍 Posição: (1350, 750)

🖱️  [ARDUINO] CLICK REQUISITADO:
   📍 Posição: (1350, 750)
   🔘 Botão: left
   ➡️  Movendo para posição antes de clicar...

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (959, 539)
   🎯 Destino: (1350, 750)
   ➡️  Delta: (+391, +211)
   📤 Comando: MOVE:1350:750
   📥 Resposta: OK:MOVE:(1350,750)
   🔍 Verificação:
      Esperado: (1350, 750)
      Real: (1350, 750)
      Erro: (0, 0)
   ✅ Movimento OK!

   ✅ Mouse posicionado!
   🔽 Pressionando botão left...
   🔼 Soltando botão left...
   ✅ CLICK COMPLETO!

⏳ Aguardando 1.0s para UI estabilizar...
🔢 Loop de alimentação: 2 cliques no botão 'eat'
⚠️ IMPORTANTE: Cada clique no 'eat' = 1 comida consumida

🍽️ === COMIDA 1/2 ===
🔍 Detectando posição do botão eat (tentativa 1/2)...
✅ Botão 'eat' detectado em: (1083, 373)
✅ Botão 'eat' confirmado em: (1083, 373)
👆 Clicando no eat...

🖱️  [ARDUINO] CLICK REQUISITADO:
   📍 Posição: (1083, 373)
   🔘 Botão: left
   ➡️  Movendo para posição antes de clicar...

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (1350, 750)
   🎯 Destino: (1083, 373)
   ➡️  Delta: (-267, -377)
   📤 Comando: MOVE:1083:373
   📥 Resposta: OK:MOVE:(1083,373)
   🔍 Verificação:
      Esperado: (1083, 373)
      Real: (1083, 373)
      Erro: (0, 0)
   ✅ Movimento OK!

   ✅ Mouse posicionado!
   🔽 Pressionando botão left...
   🔼 Soltando botão left...
   ✅ CLICK COMPLETO!

⏳ Aguardando 1.5s após eat... (1/2 comidas)
⏳ Pausa de 0.5s antes do próximo ciclo...

🍽️ === COMIDA 2/2 ===
🔍 Detectando posição do botão eat (tentativa 1/2)...
✅ Botão 'eat' detectado em: (1100, 380)
✅ Botão 'eat' confirmado em: (1100, 380)
👆 Clicando no eat...

🖱️  [ARDUINO] CLICK REQUISITADO:
   📍 Posição: (1100, 380)
   🔘 Botão: left
   ➡️  Movendo para posição antes de clicar...

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (1083, 373)
   🎯 Destino: (1100, 380)
   ➡️  Delta: (+17, +7)
   📤 Comando: MOVE:1100:380
   📥 Resposta: OK:MOVE:(1100,380)
   🔍 Verificação:
      Esperado: (1100, 380)
      Real: (1100, 380)
      Erro: (0, 0)
   ✅ Movimento OK!

   ✅ Mouse posicionado!
   🔽 Pressionando botão left...
   🔼 Soltando botão left...
   ✅ CLICK COMPLETO!

⏳ Aguardando 1.5s após eat... (2/2 comidas)
✅ Alimentação automática concluída: 2/2 comidas consumidas
⏳ Aguardando 0.5s após última comida...

📦 PASSO 4: Fechando baú...
[FECHANDO BAÚ] Pressionando ESC...
   ✅ ESC pressionado via Arduino
✅ Alimentação executada com sucesso!
==================================================

✅ [F6] Alimentação executada com sucesso
```

---

## ✅ CONCLUSÃO

**Total de comandos Arduino durante F6 (2 comidas):** 17 comandos

**Comandos críticos:**
1. `RESET_POS:959:539` - Calibração (MAIS IMPORTANTE!)
2. `MOVE:x:y` - Movimentos absolutos (devem ser exatos!)
3. `MOUSE_DOWN:L` / `MOUSE_UP:L` - Cliques
4. Teclas: ALT, E, ESC

**⚠️ ATENÇÃO:**
- Movimento de câmera durante ALT **NÃO** usa Arduino!
- Usa API Windows ou PyAutoGUI
- Arduino **só** para teclas (ALT, E, ESC) e movimentos após calibração!

**Se mouse vai para canto direito:**
1. Verificar se Arduino está conectado
2. Verificar logs para "via pyautogui (fallback)"
3. Verificar erro no primeiro MOVE após RESET_POS
4. Se erro > 50px → Problema no MouseTo → Usar AbsMouse!
