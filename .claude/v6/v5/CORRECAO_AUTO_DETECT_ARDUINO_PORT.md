# 🔧 Correção: Auto-detecção de Porta Arduino

**Data:** 2025-10-14
**Problema:** UI sempre carregava porta COM3 do config.json, mas o Arduino Pro Micro muda de porta (COM3 → COM6 → COM8) toda vez que faz upload.

**Solução:** Sistema automático de detecção de porta Arduino que identifica e seleciona a porta correta.

---

## ❌ Problema Original

### Como era antes:

1. Usuário faz upload no Arduino → Porta muda para COM8
2. Bot inicia → Carrega `com_port: COM3` do config.json
3. UI mostra COM3 selecionada (porta antiga)
4. Usuário precisa **MANUALMENTE** clicar e selecionar COM8
5. Bot não conecta se não mudar manualmente

### Por que a porta muda?

Arduino **Leonardo/Pro Micro** usa USB nativo (ATmega32U4):
- Durante upload → Bootloader ativo → Porta temporária (COM6)
- Sketch carrega → Arduino reinicia → Nova porta (COM8)
- Cada upload pode criar uma porta COM diferente

---

## ✅ Solução Implementada

### Novo comportamento:

1. **Ao carregar UI:** Detecta automaticamente porta Arduino ativa
2. **Ao clicar "Recarregar":** Re-detecta porta Arduino
3. **Se porta mudou:** Atualiza automaticamente para a nova
4. **Se Arduino detectado:** Mostra mensagem confirmando porta

---

## 📝 Alterações no Código

### Arquivo: `ui/main_window.py`

#### 1. Nova função: `_detect_arduino_port()` (linhas 5418-5441)

```python
def _detect_arduino_port(self, ports=None):
    """Detectar automaticamente porta do Arduino"""
    try:
        import serial.tools.list_ports

        if ports is None:
            ports = get_com_ports()

        # Buscar portas COM com descrição de Arduino
        for port_info in serial.tools.list_ports.comports():
            port_name = port_info.device
            description = port_info.description.lower()

            # Verificar se é Arduino Leonardo, Pro Micro ou compatível
            if any(keyword in description for keyword in ['arduino', 'leonardo', 'pro micro', 'atmega32u4', 'ch340']):
                if port_name in ports:
                    print(f"[ARDUINO] Detectado: {port_name} - {port_info.description}")
                    return port_name

        return None

    except Exception as e:
        print(f"[ARDUINO] Erro ao detectar porta: {e}")
        return None
```

**O que faz:**
- Varre todas as portas COM do sistema
- Busca por palavras-chave: `arduino`, `leonardo`, `pro micro`, `atmega32u4`, `ch340`
- Retorna a primeira porta Arduino encontrada

#### 2. Atualizada: `refresh_arduino_ports()` (linhas 5385-5441)

**Antes:**
```python
def refresh_arduino_ports(self):
    ports = get_com_ports()
    # Atualiza menu
    # NÃO detectava Arduino automaticamente
```

**Depois:**
```python
def refresh_arduino_ports(self):
    ports = get_com_ports()
    # Atualiza menu

    # ✅ NOVO: Auto-detectar e selecionar porta Arduino
    arduino_port = self._detect_arduino_port(ports)

    if arduino_port:
        if current_port != arduino_port:
            self.arduino_port_var.set(arduino_port)
            self.log_arduino(f"🔄 Porta Arduino detectada automaticamente: {arduino_port}")
```

#### 3. Atualizada: `load_arduino_config()` (linhas 5694-5733)

**Antes:**
```python
def load_arduino_config(self):
    arduino_config = self.config_manager.get('arduino', {})
    if arduino_config:
        # Sempre usava porta do config.json
        self.arduino_port_var.set(arduino_config.get('com_port', 'COM3'))
```

**Depois:**
```python
def load_arduino_config(self):
    arduino_config = self.config_manager.get('arduino', {})
    if arduino_config:
        config_port = arduino_config.get('com_port', 'COM3')

        # ✅ NOVO: Auto-detectar porta Arduino ao carregar
        detected_port = self._detect_arduino_port(ports)

        if detected_port:
            # Usa porta detectada (sempre a correta!)
            self.arduino_port_var.set(detected_port)
            if detected_port != config_port:
                self.log_arduino(f"🔄 Porta Arduino auto-detectada: {detected_port} (config tinha: {config_port})")
```

---

## 🎯 Fluxo de Detecção

### Cenário 1: Arduino conectado e reconhecido

```
1. Bot inicia
2. Lê config.json: com_port = "COM3"
3. Escaneia portas: ["COM1", "COM3", "COM8"]
4. Detecta Arduino em COM8 (descrição: "Arduino Micro")
5. ✅ Atualiza automaticamente para COM8
6. Log: "🔄 Porta Arduino auto-detectada: COM8 (config tinha: COM3)"
```

### Cenário 2: Porta do config ainda existe

```
1. Bot inicia
2. Lê config.json: com_port = "COM3"
3. Escaneia portas: ["COM1", "COM3"]
4. Não detecta Arduino (descrição genérica)
5. ⚠️ Usa COM3 do config (pode ou não ser Arduino)
6. Log: "⚠️ Usando porta do config: COM3 (Arduino não detectado automaticamente)"
```

### Cenário 3: Porta do config não existe

```
1. Bot inicia
2. Lê config.json: com_port = "COM3"
3. Escaneia portas: ["COM1", "COM8"]
4. COM3 não existe mais!
5. ⚠️ Usa primeira porta disponível (COM1)
6. Log: "⚠️ Porta COM3 não encontrada, usando: COM1"
```

### Cenário 4: Nenhuma porta disponível

```
1. Bot inicia
2. Lê config.json: com_port = "COM3"
3. Escaneia portas: []
4. Nenhuma porta COM encontrada
5. ❌ Usa "COM3" como fallback
6. Log: "❌ Nenhuma porta COM encontrada!"
```

---

## 🔍 Palavras-chave de Detecção

O sistema busca por estas palavras na descrição da porta:

| Palavra-chave | Exemplo de Descrição |
|---------------|----------------------|
| `arduino` | "Arduino Leonardo (COM8)" |
| `leonardo` | "Arduino Leonardo bootloader (COM6)" |
| `pro micro` | "SparkFun Pro Micro (COM5)" |
| `atmega32u4` | "ATmega32U4 USB Serial (COM7)" |
| `ch340` | "CH340 USB-SERIAL (COM4)" |

**Nota:** A busca é case-insensitive (maiúsculas/minúsculas não importam).

---

## 📊 Mensagens da UI

### ✅ Arduino detectado e porta mudou:
```
🔄 Porta Arduino auto-detectada: COM8 (config tinha: COM3)
```

### ✅ Arduino detectado, porta correta:
```
✅ Porta Arduino confirmada: COM3
```

### ⚠️ Arduino não detectado, usando config:
```
⚠️ Usando porta do config: COM3 (Arduino não detectado automaticamente)
```

### ⚠️ Porta do config não existe:
```
⚠️ Porta COM3 não encontrada, usando: COM8
```

### ❌ Nenhuma porta encontrada:
```
❌ Nenhuma porta COM encontrada!
```

---

## 🚀 Como Usar

### 1. **Ao iniciar o bot:**

O bot **automaticamente** detecta e seleciona a porta Arduino correta!

Você **NÃO precisa** fazer nada manualmente! 🎉

### 2. **Se a porta mudar depois:**

Clique no botão **"Recarregar Portas"** na aba Arduino.

O sistema vai re-detectar e atualizar automaticamente.

### 3. **Para conectar:**

Depois que a porta correta estiver selecionada:

1. Clique em **"Conectar"**
2. Arduino vai conectar automaticamente
3. Pronto para usar! 🎯

---

## 🔧 Troubleshooting

### Arduino não é detectado automaticamente

**Possíveis causas:**

1. **Driver USB não instalado:**
   - Windows não reconhece o Arduino
   - Instale drivers CH340 ou drivers oficiais Arduino

2. **Descrição genérica da porta:**
   - Windows mostra apenas "USB Serial Device"
   - Solução: Selecione manualmente a porta na UI

3. **Arduino não é Leonardo/Pro Micro:**
   - Arduino Uno/Mega não tem USB nativo
   - Sistema de detecção não funciona
   - Use seleção manual

### Como verificar a descrição da porta:

**Windows:**
1. `Win + X` → Gerenciador de Dispositivos
2. Expanda: `Portas (COM e LPT)`
3. Veja o nome completo: `Arduino Micro (COM8)`

Se aparecer apenas `USB Serial Device (COM8)`, o sistema não vai detectar automaticamente.

---

## ✅ Benefícios

| Antes | Depois |
|-------|--------|
| ❌ Porta sempre desatualizada | ✅ Porta sempre correta |
| ❌ Usuário precisa clicar manualmente | ✅ Totalmente automático |
| ❌ Erro "Arduino não conectado" | ✅ Conecta na primeira tentativa |
| ❌ Confuso para iniciantes | ✅ Funciona "out of the box" |

---

## 📝 Notas Técnicas

### Por que Pro Micro muda de porta?

- **USB Nativo:** Chip ATmega32U4 se apresenta diretamente como USB
- **Bootloader:** Durante upload, entra em modo bootloader (porta temporária)
- **Sketch carrega:** Arduino reinicia com novo descriptor USB
- **Windows:** Vê como "novo dispositivo" e atribui nova porta COM

### Outros Arduinos (Uno, Mega):

- Usam chip conversor USB-Serial (CH340/FTDI)
- Porta COM **nunca muda**
- **NÃO suportam** HID (teclado/mouse)
- Sistema de detecção pode não funcionar (descrição genérica)

---

## 🎉 Resultado Final

**AGORA:**
1. ✅ Bot detecta Arduino automaticamente
2. ✅ Seleciona porta correta sozinho
3. ✅ Usuário só precisa clicar "Conectar"
4. ✅ Funciona mesmo se porta mudar

**NÃO precisa mais:**
- ❌ Selecionar porta manualmente
- ❌ Lembrar qual porta é a correta
- ❌ Verificar no Gerenciador de Dispositivos
- ❌ Editar config.json

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-14
