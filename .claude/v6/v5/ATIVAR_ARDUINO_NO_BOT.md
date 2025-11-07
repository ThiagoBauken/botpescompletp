# 🔧 Como Ativar o Arduino no Bot

**Problema Identificado:** Bot está usando PyAutoGUI em vez do Arduino!

**Linha crítica:** `main_window.py:265`
```python
use_arduino = self.config_manager.get('arduino.enabled', False)  # ← FALSE por padrão!
```

---

## ✅ **SOLUÇÃO 1: Ativar na Interface (Recomendado)**

### **Passo 1: Abrir Bot**
```bash
python main.py
```

### **Passo 2: Ir para Aba Arduino**

Na interface do bot, procure a aba **"Arduino"** ou **"Hardware"**.

Deve ter:
- ☑️ **Checkbox "Usar Arduino HID"** ou **"Ativar Arduino"**
- Campo para selecionar **Porta COM** (COM10)
- Botão **"Conectar"**

### **Passo 3: Ativar e Conectar**

1. ✅ **Marcar checkbox** "Usar Arduino HID"
2. **Selecionar porta:** COM10
3. **Clicar em "Conectar"**

**Deve aparecer:**
```
✅ Arduino conectado em COM10
✅ InputManager agora usa Arduino! TODOS os inputs via HID
🎯 Calibrando MouseTo...
```

### **Passo 4: Salvar Configuração**

- Clicar em **"Salvar Configurações"**
- Isso grava `arduino.enabled = True` no `data/config.json`

### **Passo 5: Testar**

- Pressionar **F9** (iniciar pesca)
- Após 1 pesca, deve acionar feeding
- **Agora o mouse vai funcionar corretamente!**

---

## ✅ **SOLUÇÃO 2: Editar Config Manualmente**

Se não encontrar a aba Arduino na UI:

### **Passo 1: Fechar Bot**

### **Passo 2: Editar `data/config.json`**

Abrir arquivo: `C:\Users\Thiago\Desktop\v5\data\config.json`

**Procurar seção `arduino`:**
```json
{
  "arduino": {
    "enabled": false,  ← MUDAR PARA true
    "port": "COM10",
    "baudrate": 115200
  }
}
```

**Alterar para:**
```json
{
  "arduino": {
    "enabled": true,   ← AGORA TRUE!
    "port": "COM10",
    "baudrate": 115200
  }
}
```

### **Passo 3: Salvar arquivo**

### **Passo 4: Abrir bot novamente**

```bash
python main.py
```

**Deve aparecer no console:**
```
🖱️ Inicializando InputManager...
🤖 Modo Arduino HID ativado
⚠️ Conexão será feita quando clicar em 'Conectar' na aba Arduino
✅ ArduinoInputManager inicializado (aguardando conexão)
🔒 Quando conectado, TODOS os inputs serão via hardware USB HID
```

### **Passo 5: Conectar Arduino na UI**

- Ir para aba **Arduino**
- Clicar em **"Conectar"**
- Aguardar mensagem: **"✅ Arduino conectado"**

---

## 🔍 **VERIFICAR SE ESTÁ FUNCIONANDO**

### **No Console (quando bot inicia):**

**ANTES (PyAutoGUI):**
```
🖱️ Inicializando InputManager...
🖥️ Usando InputManager padrão (pyautogui)...   ← ERRADO!
✅ InputManager padrão inicializado
```

**DEPOIS (Arduino):**
```
🖱️ Inicializando InputManager...
🤖 Modo Arduino HID ativado                     ← CORRETO!
✅ ArduinoInputManager inicializado (aguardando conexão)
🔒 Quando conectado, TODOS os inputs serão via hardware USB HID
```

### **Quando Pressionar F9 e Feeding Ativar:**

**Deve aparecer:**
```
🍖 EXECUTANDO ALIMENTAÇÃO AUTOMÁTICA
📦 Abrindo baú para alimentação...
🎯 [CHEST] Calibrando MouseTo em (959, 539)...
✅ [CHEST] MouseTo calibrado! Movimentos serão diretos.
🔍 Detectando comida...
✅ COMIDA ENCONTRADA: filefrito em (1350, 450)
🖱️ Clicando na comida via Arduino...           ← DEVE TER "via Arduino"
```

**Se não aparecer "via Arduino", ainda está usando PyAutoGUI!**

---

## 📊 **DIFERENÇA ENTRE OS DOIS:**

| Aspecto | PyAutoGUI (atual) | Arduino (desejado) |
|---------|-------------------|-------------------|
| Movimento mouse | ❌ Relativo impreciso | ✅ Absoluto preciso |
| Calibração | ❌ Não funciona | ✅ RESET_POS funciona |
| Slots | ❌ Erra posição | ✅ Acerta exatamente |
| Feeding | ❌ Mouse erra comida | ✅ Mouse acerta comida |
| Anti-cheat | ⚠️ Detectável software | ✅ Hardware real |

---

## 🎯 **TESTE FINAL**

Após ativar Arduino:

1. **Fechar bot**
2. **Reconectar Arduino:**
   - Desconectar USB
   - Aguardar 5 segundos
   - Reconectar
   - Aguardar 3 segundos
3. **Abrir bot:** `python main.py`
4. **Verificar console:** Deve mostrar "🤖 Modo Arduino HID ativado"
5. **Ir para aba Arduino → Conectar**
6. **Pressionar F9** (iniciar pesca)
7. **Após 1 pesca → Feeding ativa**
8. **Mouse deve mover CORRETAMENTE agora!** ✅

---

## 🆘 **SE `data/config.json` NÃO EXISTIR**

Criar arquivo `data/config.json` com conteúdo mínimo:

```json
{
  "arduino": {
    "enabled": true,
    "port": "COM10",
    "baudrate": 115200
  }
}
```

---

## 📝 **RESUMO**

**Problema:** Bot não estava configurado para usar Arduino
**Causa:** `arduino.enabled = false` (padrão)
**Solução:** Ativar Arduino na UI ou editar `data/config.json`
**Resultado:** Mouse move corretamente para comida e botão eat!

---

**Depois de ativar, teste e me avise! 🚀**
