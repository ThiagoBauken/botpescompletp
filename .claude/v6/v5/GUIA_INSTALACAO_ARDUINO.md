# 🚀 GUIA COMPLETO - Instalação do Arduino Leonardo

**Tempo estimado:** 10 minutos
**Dificuldade:** Fácil

---

## 📦 O QUE VOCÊ PRECISA:

1. ✅ **Arduino Leonardo** ou **Arduino Pro Micro** (ATmega32U4)
2. ✅ **Cabo USB** (Micro-USB para Leonardo, Type-C ou Micro-USB para Pro Micro)
3. ✅ **Arduino IDE** instalado no Windows
4. ✅ **Arquivo do código:** `arduino_hid_controller.ino`

---

## 📍 LOCALIZAÇÃO DO ARQUIVO:

O código do Arduino está em:
```
C:\Users\Thiago\Desktop\v5\arduino\arduino_hid_controller\arduino_hid_controller.ino
```

---

## 🛠️ PASSO A PASSO COMPLETO:

### **PASSO 1: Instalar o Arduino IDE** (se ainda não tem)

1. Baixar Arduino IDE: https://www.arduino.cc/en/software
2. Instalar normalmente (Next → Next → Install)
3. Abrir o Arduino IDE

---

### **PASSO 2: Conectar o Arduino Leonardo**

1. Conecte o **Arduino Leonardo** ao computador via USB
2. Aguarde o Windows instalar os drivers automaticamente (1-2 minutos)
3. Se o Windows não instalar:
   - Abra **Gerenciador de Dispositivos** (Win + X → Gerenciador de Dispositivos)
   - Procure por "Portas (COM e LPT)"
   - Deve aparecer "Arduino Leonardo (COMx)" onde x é o número da porta

**Exemplo:**
```
Portas (COM e LPT)
  └─ Arduino Leonardo (COM3)  ← Este é seu Arduino!
```

---

### **PASSO 3: Configurar o Arduino IDE**

#### 3.1 - Selecionar a Placa

1. Abra o Arduino IDE
2. Clique em **Tools** (Ferramentas) no menu superior
3. Clique em **Board** (Placa)
4. Selecione: **Arduino Leonardo**

**Screenshot:**
```
Tools
 ├─ Board: "Arduino Leonardo" ✓
 ├─ Port: ...
 └─ ...
```

#### 3.2 - Selecionar a Porta COM

1. Ainda no menu **Tools** (Ferramentas)
2. Clique em **Port** (Porta)
3. Selecione a porta COM do Arduino (ex: COM3)
   - Geralmente aparece como "COM3 (Arduino Leonardo)"

**Screenshot:**
```
Tools
 ├─ Board: "Arduino Leonardo" ✓
 ├─ Port: "COM3 (Arduino Leonardo)" ✓
 └─ ...
```

---

### **PASSO 4: Abrir o Código no Arduino IDE**

#### Opção 1: Abrir arquivo diretamente

1. No Arduino IDE, clique em **File** → **Open**
2. Navegue até: `C:\Users\Thiago\Desktop\v5\arduino\arduino_hid_controller\`
3. Selecione o arquivo: **`arduino_hid_controller.ino`**
4. Clique em **Open** (Abrir)

#### Opção 2: Copiar e colar

1. Abra o arquivo `arduino_hid_controller.ino` no Bloco de Notas
2. Copie TODO o conteúdo (Ctrl + A, Ctrl + C)
3. No Arduino IDE, cole o código (Ctrl + V)

---

### **PASSO 5: Verificar o Código** (opcional mas recomendado)

1. Clique no botão **Verify** (✓) no canto superior esquerdo
2. Aguarde a compilação (5-10 segundos)
3. Deve aparecer: **"Done compiling."** na parte inferior

**Se houver erro:**
- Verifique se a placa está configurada como "Arduino Leonardo"
- Verifique se o código foi colado corretamente

---

### **PASSO 6: Fazer Upload para o Arduino**

1. Clique no botão **Upload** (→) no canto superior esquerdo
2. Aguarde o upload (10-20 segundos)

**O que vai acontecer:**
```
Sketch uses 5234 bytes (18%) of program storage space...
Uploading...
    ████████████████████ 100%
Done uploading.
```

3. ✅ Quando aparecer **"Done uploading."** → PRONTO!

---

### **PASSO 7: Testar a Conexão**

#### Teste Rápido no Arduino IDE

1. Clique em **Tools** → **Serial Monitor** (ou Ctrl + Shift + M)
2. Configure o baud rate para **9600** (canto inferior direito)
3. Digite: `PING` e pressione Enter
4. Deve aparecer: `PONG`

**Exemplo:**
```
9600 baud
--------
PING
PONG
```

✅ Se apareceu "PONG", o Arduino está funcionando!

#### Teste Completo via Python

1. Abra o terminal/prompt de comando
2. Navegue até a pasta do bot:
   ```bash
   cd C:\Users\Thiago\Desktop\v5
   ```
3. Execute o teste:
   ```bash
   python core/arduino_input_manager.py
   ```

**Saída esperada:**
```
============================================================
🧪 TESTE DE CONEXÃO ARDUINO - VERSÃO COMPLETA
============================================================
🔌 Conectando ao Arduino na porta COM3...
✅ Arduino conectado em COM3

✅ Arduino conectado com sucesso!

📡 Teste 1: PING
   ✅ PONG recebido

⌨️ Teste 2: Pressionar tecla '1' (em 2 segundos...)
   ✅ Tecla '1' pressionada

🖱️ Teste 3: Click esquerdo (em 2 segundos...)
   ✅ Click executado

🖱️ Teste 4: Segurar botão direito por 1 segundo...
   ✅ Botão direito segurado e solto

🖱️ Teste 5: Movimento relativo do mouse...
   ✅ Movimento de mouse executado

============================================================
✅ TODOS OS TESTES PASSARAM!
============================================================
```

✅ Se passou em todos os testes, está pronto para usar!

---

## 🔍 TROUBLESHOOTING (Problemas Comuns):

### ❌ Problema 1: "Port not found" (Porta não encontrada)

**Solução:**
1. Desconecte e reconecte o Arduino USB
2. Aguarde 10 segundos
3. Verifique no Gerenciador de Dispositivos se aparece "Arduino Leonardo (COMx)"
4. Se não aparecer:
   - Instale os drivers: https://www.arduino.cc/en/software
   - Ou instale drivers SparkFun (para Pro Micro): https://learn.sparkfun.com/tutorials/pro-micro--fio-v3-hookup-guide/installing-windows

---

### ❌ Problema 2: "Upload failed" (Falha no upload)

**Solução:**
1. Pressione o botão **RESET** no Arduino
2. Aguarde 5 segundos
3. Clique em **Upload** novamente rapidamente
4. Se ainda falhar:
   - Feche o Serial Monitor (se estiver aberto)
   - Tente novamente

---

### ❌ Problema 3: "Sketch too big" (Código muito grande)

**Solução:**
- Seu Arduino pode ser um modelo diferente (Uno não funciona!)
- Verifique se é realmente um **Leonardo** ou **Pro Micro** (ATmega32U4)
- Arduino Uno NÃO suporta HID (teclado/mouse)

---

### ❌ Problema 4: Python não encontra o Arduino

**Solução:**
1. Verifique qual porta COM no Gerenciador de Dispositivos
2. Edite o arquivo `config/default_config.json`:
   ```json
   "arduino": {
     "enabled": true,
     "com_port": "COM3",  ← Coloque a porta correta aqui
     "auto_connect": true
   }
   ```
3. Ou especifique manualmente no código:
   ```python
   input_manager = ArduinoInputManager(port='COM3')
   ```

---

### ❌ Problema 5: Serial Monitor não responde

**Solução:**
1. Verifique o **baud rate**: deve estar em **9600**
2. Selecione "Both NL & CR" no Serial Monitor
3. Pressione o botão RESET no Arduino
4. Deve aparecer `READY` no Serial Monitor
5. Teste com `PING` novamente

---

## 📝 VERIFICAÇÃO FINAL:

Antes de usar com o bot, confirme:

- [x] Arduino Leonardo conectado e reconhecido pelo Windows
- [x] Código `arduino_hid_controller.ino` carregado com sucesso
- [x] Serial Monitor responde "PONG" ao comando "PING"
- [x] Teste Python (`python core/arduino_input_manager.py`) passou em todos os testes
- [x] Porta COM correta identificada (ex: COM3)

✅ Se todos os itens estão marcados, você está pronto para usar o bot com Arduino!

---

## 🚀 PRÓXIMO PASSO: Usar o Bot com Arduino

Edite o arquivo `main.py`:

**Linha ~20-30 (aproximadamente):**
```python
# ANTES (InputManager padrão):
from core.input_manager import InputManager
input_manager = InputManager(config_manager)

# DEPOIS (Arduino HID):
from core.arduino_input_manager import ArduinoInputManager
input_manager = ArduinoInputManager(config_manager=config_manager)
# Auto-detecta a porta COM automaticamente!
```

Salve e execute o bot normalmente:
```bash
python main.py
```

✅ Agora TODOS os inputs serão executados pelo Arduino via hardware USB HID!

---

## 📞 SUPORTE:

Se tiver problemas:
1. Verifique o [ARDUINO_AUDIT_REPORT.md](ARDUINO_AUDIT_REPORT.md) - Auditoria completa
2. Leia o [arduino/README_ARDUINO.md](arduino/README_ARDUINO.md) - Guia técnico
3. Execute `python test_arduino_compatibility.py` - Teste de compatibilidade

---

**Criado para Ultimate Fishing Bot v5**
**Data:** 2025-10-13
**Autor:** Thiago + Claude
