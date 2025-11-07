# 🔍 DEBUG: Por que F6 Move Mouse Para o Canto Direito?

## Problema

Quando você aperta **F6**, o mouse move para o canto direito da tela.

## Análise de Código

### Sequência F6 → Movimento:

```
1. F6 pressionado
   ↓
2. hotkey_manager._handle_manual_feeding()
   ↓
3. fishing_engine.trigger_feeding()
   ↓
4. feeding_system.execute_feeding()
   ↓
5. chest_manager.open_chest(ChestOperation.FEEDING)
   ↓
6. chest_manager.center_camera()  ← AQUI!
   ↓
7. if self.input_manager and hasattr(self.input_manager, 'move_to'):
       self.input_manager.move_to(target_x, target_y)  # Arduino
   else:
       pyautogui.moveTo(target_x, target_y)  # ← FALLBACK PROBLEMÁTICO
```

### Código Problemático:

**Arquivo:** `core/chest_manager.py`
**Linha 152-159:**

```python
# ✅ USAR ARDUINO via InputManager ao invés de pyautogui
if self.input_manager and hasattr(self.input_manager, 'move_to'):
    self.input_manager.move_to(target_x, target_y)
    _safe_print("✅ [CHEST] Câmera centralizada via Arduino")
else:
    # Fallback para pyautogui se InputManager não disponível
    pyautogui.moveTo(target_x, target_y, duration=0.3)  # ← PROBLEMA!
    _safe_print("⚠️ [CHEST] Câmera centralizada via pyautogui (fallback)")
```

## Possíveis Causas

### Causa 1: Arduino não conectado

Se Arduino **não está conectado**, o código usa `pyautogui.moveTo()` como fallback.

**Como verificar:**
Nos logs, procure por:
- ✅ `"Câmera centralizada via Arduino"` → Arduino está sendo usado (BOM)
- ⚠️ `"Câmera centralizada via pyautogui (fallback)"` → PyAutoGUI está sendo usado (PROBLEMA!)

### Causa 2: target_x e target_y estão errados

A posição de centralização pode estar incorreta:

```python
initial_pos = self.config_manager.get('initial_camera_pos')
if initial_pos:
    target_x = initial_pos['x']
    target_y = initial_pos['y']
else:
    # Fallback para centro da tela
    screen_width, screen_height = pyautogui.size()
    target_x = screen_width // 2  # 1920 // 2 = 960
    target_y = screen_height // 2  # 1080 // 2 = 540
```

Se `initial_camera_pos` estiver errado na config, o mouse vai para posição errada!

### Causa 3: Múltiplos movimentos

Há **outros `pyautogui.moveTo()`** no código:

**chest_manager.py linha 210:**
```python
pyautogui.moveTo(target_x, target_y, duration=0.5)
```

**chest_manager.py linha 336:**
```python
pyautogui.moveTo(x, y, duration=duration)
```

Esses podem estar executando JUNTO com o Arduino!

## Como Identificar o Problema

### Passo 1: Verificar se Arduino está conectado

**No bot, pressione F6 e veja os logs:**

```
✅ [CHEST] Câmera centralizada via Arduino  ← BOM! Está usando Arduino
⚠️ [CHEST] Câmera centralizada via pyautogui (fallback)  ← RUIM! Está usando PyAutoGUI
```

Se aparecer **"pyautogui (fallback)"**, então Arduino NÃO está conectado!

### Passo 2: Verificar posição de centralização

**Nos logs, procure:**

```
📍 [CHEST] Centralizando câmera em (X, Y)
```

Se X e Y forem **muito altos** (tipo 1900+), então a posição está errada!

### Passo 3: Verificar config

**Abra o arquivo:** `data/config.json`

**Procure por:**
```json
{
  "initial_camera_pos": {
    "x": 960,  ← Deve ser próximo de 960
    "y": 540   ← Deve ser próximo de 540
  }
}
```

Se `x` ou `y` forem muito altos (1900+), **DELETE** essa seção da config e reinicie o bot!

## Soluções

### Solução 1: Garantir que Arduino está conectado

**Antes de pressionar F6:**

1. Ir na aba **Arduino** na UI
2. Clicar **"Conectar"**
3. Aguardar **"✅ Arduino conectado"**
4. **Agora sim** pressionar F6

### Solução 2: Corrigir initial_camera_pos

**Deletar posição inicial errada:**

1. Fechar o bot
2. Abrir `data/config.json`
3. Procurar `"initial_camera_pos"`
4. **Deletar** a seção inteira:
   ```json
   "initial_camera_pos": {
     "x": 1900,  ← DELETE ISTO
     "y": 1000
   },
   ```
5. Salvar arquivo
6. Reabrir bot
7. Bot vai usar centro da tela (960, 540)

### Solução 3: REMOVER pyautogui.moveTo() do código (DEFINITIVA)

Editar `core/chest_manager.py` para **FORÇAR** uso do Arduino:

**Linha 152-159, MUDAR PARA:**

```python
# ✅ FORÇAR uso do Arduino (sem fallback!)
if self.input_manager and hasattr(self.input_manager, 'move_to'):
    self.input_manager.move_to(target_x, target_y)
    _safe_print("✅ [CHEST] Câmera centralizada via Arduino")
else:
    # ❌ NÃO USAR pyautogui - apenas avisar erro!
    _safe_print("❌ [CHEST] Arduino não conectado! F6 não funcionará!")
    _safe_print("⚠️ [CHEST] Conecte o Arduino na aba Arduino primeiro!")
    return False  # Abortar operação!
```

**Fazer o mesmo nas linhas 207-211:**

```python
if self.input_manager and hasattr(self.input_manager, 'camera_turn_in_game'):
    self.input_manager.camera_turn_in_game(dx, dy)
    _safe_print("   ✅ Câmera movida via Arduino!")
else:
    _safe_print("❌ [CHEST] Arduino não conectado!")
    return False
```

## TESTE IMEDIATO

**Execute AGORA:**

1. Abra o bot
2. Vá na aba **Arduino**
3. Conecte o Arduino
4. Aguarde **"✅ Arduino conectado"**
5. Pressione **F6**
6. **Olhe os logs** e me diga:
   - Apareceu "Câmera centralizada via Arduino" ou "via pyautogui"?
   - Qual foi a posição de centralização mostrada?
   - O mouse ainda foi para o canto direito?

---

**RESPONDA ESTAS PERGUNTAS:**

1. **O Arduino está conectado quando você pressiona F6?**
2. **O que aparece nos logs quando pressiona F6?**
3. **Qual é o valor de `initial_camera_pos` no seu `data/config.json`?**
