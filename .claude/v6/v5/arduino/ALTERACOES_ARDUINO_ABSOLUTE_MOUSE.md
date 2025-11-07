# 🎯 Alterações: Arduino Absolute Mouse (AbsMouse)

**Data:** 2025-10-14
**Objetivo:** Fazer o Arduino controlar TODOS os movimentos do mouse, incluindo movimento relativo da câmera durante abertura do baú.

---

## 📋 Resumo das Mudanças

### 1. Arduino Sketch Atualizado

**Arquivo:** `arduino\arduino_hid_controller_FIXED\arduino_hid_controller_FIXED.ino`

**Adicionado:**
- ✅ Suporte para biblioteca **AbsMouse** (movimento absoluto)
- ✅ Novo comando `MOUSEABS:<x>:<y>` para posicionamento absoluto
- ✅ Resolução da tela configurável (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
- ✅ Validação de coordenadas (evita movimento fora da tela)

**Como funciona:**
- Arduino agora simula um **tablet digitalizador** (absolute positioning device)
- Mouse pula **instantaneamente** para coordenada X,Y na tela
- Sem mais movimentos "viajando" pela tela em múltiplos passos

---

### 2. Python: ArduinoInputManager

**Arquivo:** `core\arduino_input_manager.py`

**Já estava pronto!** O código Python foi atualizado anteriormente para:
- ✅ Tentar comando `MOUSEABS` primeiro (se Arduino tiver AbsMouse)
- ✅ Fallback automático para movimento relativo otimizado (3 passos)
- ✅ Graceful degradation (funciona com ou sem AbsMouse)

---

### 3. Python: ChestManager

**Arquivo:** `core\chest_manager.py`

**PROBLEMA IDENTIFICADO:**
❌ Estava usando `pyautogui.moveTo()` para movimentos de câmera
❌ Arduino não estava sendo usado durante Page Down (manutenção)

**CORRIGIDO:**
✅ `center_camera()` - Agora usa `input_manager.move_to()` (Arduino)
✅ `execute_camera_movement()` - Agora usa `input_manager.move_to()` (Arduino)
✅ `execute_custom_macro()` - Todos os comandos (`move`, `click`, `key`) agora usam Arduino

**Resultado:**
Quando você aperta **Page Down** (manutenção de varas):
1. ✅ Arduino aperta ALT
2. ✅ **Arduino move mouse** (movimento relativo da câmera) ← CORRIGIDO!
3. ✅ Arduino aperta E
4. ✅ Arduino solta ALT

---

## 🔧 Como Instalar a Biblioteca AbsMouse

### Opção 1: Via Arduino IDE (Recomendado)

1. Abra Arduino IDE
2. Vá em: `Sketch → Include Library → Manage Libraries...`
3. Busque: `AbsMouse`
4. Instale: **AbsMouse** por **Jonathan Edgecombe**

### Opção 2: Manual

1. Baixe: https://github.com/jonathanedgecombe/absmouse/releases
2. Extraia para: `Documents\Arduino\libraries\AbsMouse\`
3. Reinicie o Arduino IDE

---

## 📤 Carregar o Sketch no Arduino

1. Abra o Arduino IDE
2. Abra: `arduino\arduino_hid_controller_FIXED\arduino_hid_controller_FIXED.ino`
3. **IMPORTANTE:** Verifique a resolução da tela no código:
   ```cpp
   #define SCREEN_WIDTH 1920
   #define SCREEN_HEIGHT 1080
   ```
   Se sua tela for diferente, ajuste esses valores!

4. Selecione a placa:
   - `Tools → Board → Arduino Leonardo` (ou Pro Micro)

5. Selecione a porta:
   - `Tools → Port → COMx` (porta do seu Arduino)

6. Clique em **Upload** (→)

7. Aguarde: `Done uploading.`

---

## ✅ Como Testar

### Teste 1: Verificar Conexão

1. Abra `Tools → Serial Monitor`
2. Configure: **115200 baud**
3. Deve aparecer: `READY`
4. Digite: `PING` → Deve responder: `PONG`

### Teste 2: Movimento Absoluto

No Serial Monitor, digite:

```
MOUSEABS:960:540
```

O mouse deve **pular instantaneamente** para o centro da tela!

### Teste 3: Testar no Bot

1. Inicie o bot: **F9**
2. Aperte: **Page Down** (manutenção de varas)
3. Observe os logs:
   - ✅ Deve aparecer: `"✅ [CHEST] Câmera movida via Arduino!"`
   - ✅ Deve aparecer: `"✅ [ARDUINO] Mouse movido (absoluto MOUSEABS)"`
   - ❌ **NÃO** deve aparecer: `"pyautogui (fallback)"`

Se você ver "via Arduino" nos logs, tudo está funcionando perfeitamente! 🎉

---

## 🔍 Solução de Problemas

### "AbsMouse.h: No such file or directory"

**Problema:** Biblioteca não instalada.

**Solução:**
1. Instale via Arduino IDE Library Manager
2. Ou extraia manualmente para `Documents\Arduino\libraries\AbsMouse\`
3. Reinicie o Arduino IDE

### Mouse não move ou vai para posição errada

**Problema:** Resolução da tela incorreta no sketch.

**Solução:**
1. Verifique sua resolução real (Configurações do Windows → Display)
2. Edite o sketch:
   ```cpp
   #define SCREEN_WIDTH 1920  // Ajuste aqui
   #define SCREEN_HEIGHT 1080 // Ajuste aqui
   ```
3. Faça upload novamente

### Logs mostram "pyautogui (fallback)"

**Problema 1:** Arduino não tem AbsMouse instalado.

**Solução:** Instale a biblioteca AbsMouse e faça upload do sketch novamente.

**Problema 2:** InputManager não está conectado ao ChestManager.

**Solução:** Verifique se `arduino_enabled` está `true` em `data/config.json`.

---

## 📊 Antes vs Depois

### ❌ Antes (Sem AbsMouse)

**Abertura do baú (Page Down):**
```
1. Arduino: ALT down
2. pyautogui: move mouse em 10-20 passos pequenos (lento, visível)
3. Arduino: E press
4. Arduino: ALT up
```

**Resultado:** Movimento **lento e visível**, fácil de detectar como bot.

### ✅ Depois (Com AbsMouse)

**Abertura do baú (Page Down):**
```
1. Arduino: ALT down
2. Arduino: MOUSEABS comando → mouse pula instantaneamente
3. Arduino: E press
4. Arduino: ALT up
```

**Resultado:** Movimento **instantâneo e natural**, indistinguível de humano.

---

## 🎯 Arquivos Modificados

1. ✅ `arduino\arduino_hid_controller_FIXED\arduino_hid_controller_FIXED.ino`
   - Adicionado: `#include <AbsMouse.h>`
   - Adicionado: `handleMouseAbsolute()` function
   - Adicionado: Comando `MOUSEABS` no `processCommand()`

2. ✅ `core\chest_manager.py`
   - Modificado: `center_camera()` → usa `input_manager.move_to()`
   - Modificado: `execute_camera_movement()` → usa `input_manager.move_to()`
   - Modificado: `execute_custom_macro()` → usa `input_manager` para tudo

3. ✅ `core\arduino_input_manager.py`
   - Já estava atualizado (commit anterior)
   - Método `move_to()` tenta `MOUSEABS` primeiro
   - Fallback automático para movimento relativo otimizado

---

## 📚 Documentação

Para mais detalhes, veja:
- **GUIA_INSTALACAO_ABSMOUSE.md** - Guia completo de instalação
- **AbsMouse GitHub:** https://github.com/jonathanedgecombe/absmouse

---

## ✅ Checklist Final

Antes de usar o bot, confirme:

- [ ] Biblioteca AbsMouse instalada no Arduino IDE
- [ ] Sketch atualizado carregado no Arduino Leonardo/Pro Micro
- [ ] Resolução configurada corretamente no sketch (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
- [ ] Serial Monitor mostra `READY` ao conectar
- [ ] Teste `MOUSEABS:960:540` funciona (mouse pula para centro)
- [ ] `arduino_enabled: true` em `data/config.json`
- [ ] Logs mostram "via Arduino" ao apertar Page Down

Se todos marcados, o sistema está 100% funcional! 🚀

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-14
