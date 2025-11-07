# 🧪 Guia de Teste - Biblioteca MouseTo

## 📋 Checklist Antes de Testar

### 1. Verificar se MouseTo está instalada

**Arduino IDE → Sketch → Include Library → Manage Libraries**

Buscar: **MouseTo**

Deve aparecer:
```
MouseTo by per1234
Version: 2.1.0 (ou superior)
```

Se não estiver instalada → Clicar em **Install**

---

### 2. Verificar Placa e Porta

**Tools → Board:**
- Arduino Leonardo (ou)
- Arduino Micro (ou)
- SparkFun Pro Micro

**Tools → Port:**
- Windows: `COMx` (ex: COM3, COM4)
- Linux: `/dev/ttyACMx`

---

## 🧪 TESTE 1: Sketch Simples (Verificar Biblioteca)

### Passo 1: Abrir Sketch de Teste

Abrir arquivo:
```
C:\Users\Thiago\Desktop\v5\arduino\test_mouseto_library\test_mouseto_library.ino
```

### Passo 2: Compilar (Verify)

Clicar em **✓ Verify** (ou Ctrl+R)

**✅ SUCESSO se aparecer:**
```
Sketch uses XXXX bytes (XX%) of program storage space.
Done compiling.
```

**❌ ERRO se aparecer:**
```
error: MouseTo.h: No such file or directory
```
→ Biblioteca não instalada! Voltar ao passo 1.

### Passo 3: Upload

1. Conectar Arduino via USB
2. Selecionar porta correta (Tools → Port)
3. Clicar em **→ Upload** (ou Ctrl+U)

**✅ SUCESSO se aparecer:**
```
Uploading...
Writing | ################################################## | 100%
avrdude done. Thank you.
```

### Passo 4: Abrir Serial Monitor

**Tools → Serial Monitor** (ou Ctrl+Shift+M)

Configurar:
- **Baud rate:** 115200
- **Line ending:** Newline

**✅ SUCESSO se aparecer:**
```
=================================
TESTE DA BIBLIOTECA MOUSETO
=================================
✓ Mouse.begin() OK
✓ MouseTo configurado OK

TESTE 1: Mover para centro (960, 540)
✓ Alvo alcançado em 96 chamadas, 150ms
=================================
TESTE CONCLUÍDO
=================================

Envie comandos via Serial Monitor:
  MOVE:x:y  - Move para posição (ex: MOVE:500:300)
  PING      - Teste de comunicação
```

---

## 🧪 TESTE 2: Comandos Interativos

Com Serial Monitor aberto (115200 baud):

### Comando 1: PING
```
Enviar: PING
Esperar: PONG
```

**✅ Sucesso:** Responde "PONG"
**❌ Erro:** Nada acontece → Verificar baud rate

---

### Comando 2: Mover Mouse

```
Enviar: MOVE:500:300
Esperar:
  Movendo para (500, 300)...
  OK - Alvo alcançado!
```

**✅ Sucesso:** Mouse se move para posição
**❌ Erro:** "TIMEOUT" → MouseTo não está funcionando

---

### Comando 3: Mover para Centro

```
Enviar: MOVE:960:540
```

**✅ Sucesso:** Mouse vai para centro da tela (1920x1080)

---

### Comando 4: Canto Superior Esquerdo

```
Enviar: MOVE:0:0
```

**✅ Sucesso:** Mouse vai para canto

---

## 🧪 TESTE 3: Sketch Completo (Com Protocolo)

### Passo 1: Abrir Sketch Principal

Abrir arquivo:
```
C:\Users\Thiago\Desktop\v5\arduino\arduino_hid_controller_HID\arduino_hid_controller_HID.ino
```

### Passo 2: Compilar

Clicar em **✓ Verify**

**✅ SUCESSO:**
```
Sketch uses XXXX bytes (XX%) of program storage space.
Done compiling.
```

**❌ ERRO se aparecer:**
```
error: 'class MouseToClass' has no member named 'atTarget'
```
→ Código não está atualizado! Verificar se salvou as correções.

### Passo 3: Upload

**→ Upload** (Ctrl+U)

### Passo 4: Testar Protocolo Completo

Com Serial Monitor (115200 baud):

#### Teste Sistema
```
Enviar: PING
Esperar: PONG
```

#### Teste Mouse Absoluto
```
Enviar: MOVE:960:540
Esperar: OK:MOVE:(960,540)
```

#### Teste Clique
```
Enviar: CLICK:800:400
Esperar: OK:CLICK:(800,400)
```

#### Teste Drag
```
Enviar: DRAG:500:300:700:500
Esperar: OK:DRAG:(500,300)→(700,500)
```

#### Teste Mouse Relativo
```
Enviar: MOVE_REL:100:0
Esperar: OK:MOVE_REL:(100,0)
```

#### Teste Comandos Curtos
```
Enviar: MLD
Esperar: OK

Enviar: MLU
Esperar: OK

Enviar: d
Esperar: OK

Enviar: d0
Esperar: OK
```

---

## 📊 Diagnóstico de Problemas

### Problema 1: Biblioteca não encontrada

**Erro:**
```
error: MouseTo.h: No such file or directory
```

**Solução:**
1. Arduino IDE → Sketch → Include Library → Manage Libraries
2. Buscar "MouseTo"
3. Instalar "MouseTo by per1234"
4. Reiniciar Arduino IDE
5. Tentar compilar novamente

---

### Problema 2: Arduino não reconhecido

**Erro:**
```
Port COM3 not found
```

**Solução Windows:**
1. Abrir Device Manager (Gerenciador de Dispositivos)
2. Verificar em "Ports (COM & LPT)"
3. Deve aparecer: "Arduino Leonardo (COMx)"
4. Se não aparecer → Instalar drivers:
   - https://www.arduino.cc/en/Guide/DriverInstallation

**Solução Linux:**
```bash
ls /dev/ttyACM*
# Deve listar: /dev/ttyACM0 (ou similar)

# Adicionar usuário ao grupo dialout:
sudo usermod -a -G dialout $USER
# Logout e login novamente
```

---

### Problema 3: Mouse não move corretamente

**Sintoma:** Mouse se move, mas não chega no alvo exato

**Solução:** Ajustar fator de correção

No sketch, linha ~78:
```cpp
// Testar valores entre 0.9 e 1.1
MouseTo.setCorrectionFactor(1.05);  // Aumenta 5%
```

**Calibração:**
1. Enviar: `MOVE:960:540` (centro)
2. Verificar se mouse chegou exato no centro
3. Se passou do alvo → Diminuir fator (0.95)
4. Se não chegou → Aumentar fator (1.05)

---

### Problema 4: Timeout em movimentos

**Sintoma:** `ERROR:MOVE_TIMEOUT` ou `TIMEOUT`

**Solução:** Aumentar timeout

No sketch, linha ~33:
```cpp
#define MOVE_TIMEOUT_MS 500  // Aumentar de 200 para 500
```

---

## ✅ Checklist de Validação

Todos os testes devem passar:

- [ ] **Compilação OK** - Sem erros ao verificar sketch
- [ ] **Upload OK** - Arduino aceita código
- [ ] **Serial conecta** - Serial Monitor abre e mostra mensagens
- [ ] **PING/PONG** - Responde ao comando PING
- [ ] **Mouse move absoluto** - `MOVE:960:540` funciona
- [ ] **Mouse preciso** - Chega exatamente no alvo
- [ ] **Clique funciona** - `CLICK:x:y` clica na posição
- [ ] **Drag funciona** - `DRAG:x1:y1:x2:y2` arrasta
- [ ] **Comandos curtos** - `MLD`, `d`, `d0` funcionam

---

## 🎯 Resultado Esperado

Depois de todos os testes, você deve ter:

✅ **Biblioteca MouseTo instalada e funcionando**
✅ **Arduino respondendo comandos**
✅ **Mouse movendo com precisão absoluta**
✅ **Drag funcionando suavemente**
✅ **Comandos curtos operacionais**

---

## 🚀 Próximo Passo

Se todos os testes passaram, você está pronto para:

**Integrar ao Python!**

Próximos arquivos a criar:
1. `arduino_wrapper.py` - Classe de comunicação serial
2. Modificar `input_manager.py` - Adicionar suporte Arduino
3. Testar integração completa com bot de pesca

Quer que eu crie esses arquivos agora?
