# 📦 Guia de Instalação - Biblioteca AbsMouse

Este guia explica como instalar a biblioteca **AbsMouse** no Arduino Leonardo/Pro Micro para permitir posicionamento absoluto do mouse (como um tablet gráfico).

---

## 🎯 Por que AbsMouse?

**Problema:** A biblioteca `Mouse.h` padrão do Arduino só suporta movimento **relativo** (mover X pixels para esquerda/direita).

**Solução:** A biblioteca **AbsMouse** permite movimento **absoluto** (mover diretamente para coordenada X,Y na tela), igual ao `pyautogui.moveTo()`.

---

## 📥 Método 1: Instalação via Arduino IDE (RECOMENDADO)

### Passo 1: Abrir o Gerenciador de Bibliotecas

1. Abra o **Arduino IDE**
2. No menu superior, clique em:
   ```
   Sketch → Include Library → Manage Libraries...
   ```
3. Aguarde o gerenciador abrir

### Passo 2: Buscar e Instalar

1. Na barra de busca, digite: `AbsMouse`
2. Encontre a biblioteca **"AbsMouse"** por **Jonathan Edgecombe**
3. Clique no botão **"Install"**
4. Aguarde a instalação concluir

### Passo 3: Verificar Instalação

Depois de instalar, verifique se aparece em:
```
Sketch → Include Library → AbsMouse
```

---

## 📥 Método 2: Instalação Manual

Se o Método 1 não funcionar, use instalação manual:

### Passo 1: Baixar a Biblioteca

1. Acesse: https://github.com/jonathanedgecombe/absmouse/releases
2. Baixe o arquivo **ZIP** da última versão
3. Extraia o conteúdo para uma pasta chamada `AbsMouse`

### Passo 2: Copiar para Pasta de Bibliotecas

**No Windows:**
```
C:\Users\SEU_USUARIO\Documents\Arduino\libraries\AbsMouse\
```

**No Linux/Mac:**
```
~/Documents/Arduino/libraries/AbsMouse/
```

A estrutura deve ficar assim:
```
Arduino/
└── libraries/
    └── AbsMouse/
        ├── AbsMouse.h
        ├── AbsMouse.cpp
        ├── HID.cpp
        └── examples/
```

### Passo 3: Reiniciar Arduino IDE

Feche e abra o Arduino IDE novamente para reconhecer a biblioteca.

---

## 🔧 Carregar o Sketch Atualizado

### Passo 1: Abrir o Sketch

1. No Arduino IDE, vá em: `File → Open`
2. Navegue até:
   ```
   C:\Users\Thiago\Desktop\v5\arduino\arduino_hid_controller_FIXED\
   ```
3. Abra o arquivo: `arduino_hid_controller_FIXED.ino`

### Passo 2: Verificar Resolução da Tela

No topo do código, verifique se a resolução está correta:

```cpp
#define SCREEN_WIDTH 1920
#define SCREEN_HEIGHT 1080
```

Se sua tela tiver resolução diferente, ajuste esses valores.

### Passo 3: Selecionar Placa e Porta

1. Em `Tools → Board`, selecione:
   - **Arduino Leonardo** (se for Leonardo)
   - **Arduino Pro Micro** (se for Pro Micro)

2. Em `Tools → Port`, selecione a porta COM do Arduino (ex: COM3, COM4)

### Passo 4: Compilar e Carregar

1. Clique no botão **"Verify"** (✓) para compilar
2. Se não houver erros, clique em **"Upload"** (→)
3. Aguarde a mensagem: `Done uploading.`

---

## ✅ Testar o Sistema

### Teste 1: Verificar Conexão

Após carregar o sketch, abra o **Serial Monitor** (`Tools → Serial Monitor`):

1. Configure para **115200 baud**
2. Você deve ver: `READY`
3. Digite: `PING` e pressione Enter
4. Deve responder: `PONG`

### Teste 2: Movimento Absoluto

No Serial Monitor, teste o comando `MOUSEABS`:

```
MOUSEABS:960:540
```

O mouse deve mover **diretamente** para o centro da tela (1920/2, 1080/2).

### Teste 3: Testar Várias Posições

Teste outros cantos da tela:

```
MOUSEABS:0:0        → Canto superior esquerdo
MOUSEABS:1920:0     → Canto superior direito
MOUSEABS:0:1080     → Canto inferior esquerdo
MOUSEABS:1920:1080  → Canto inferior direito
MOUSEABS:960:540    → Centro da tela
```

Se o mouse **pular diretamente** para cada posição (sem "viajar"), a biblioteca está funcionando corretamente!

---

## 🔍 Solução de Problemas

### Erro: "AbsMouse.h: No such file or directory"

**Causa:** Biblioteca não instalada corretamente.

**Solução:**
1. Verifique se a pasta `AbsMouse` está em `Documents/Arduino/libraries/`
2. Reinicie o Arduino IDE
3. Tente instalar pelo Gerenciador de Bibliotecas novamente

### Mouse não move ou move incorretamente

**Causa 1:** Resolução da tela incorreta.

**Solução:** Verifique `SCREEN_WIDTH` e `SCREEN_HEIGHT` no sketch.

**Causa 2:** Arduino não é Leonardo/Pro Micro.

**Solução:** AbsMouse só funciona em placas com chip ATmega32U4 (Leonardo, Pro Micro, Micro).

### Serial Monitor mostra "ERROR:COORDS_OUT_OF_BOUNDS"

**Causa:** Coordenadas enviadas estão fora da resolução da tela.

**Solução:** Certifique-se de que X ≤ SCREEN_WIDTH e Y ≤ SCREEN_HEIGHT.

---

## 📊 Comparação: Antes vs Depois

### Antes (Mouse Relativo)

```python
# Python envia múltiplos comandos
MOUSEMOVE:50:50
MOUSEMOVE:50:50
MOUSEMOVE:50:50  # 8-20 passos para chegar ao destino
...
```

**Resultado:** Movimento lento, visível, "viajando" pela tela.

### Depois (Mouse Absoluto com AbsMouse)

```python
# Python envia 1 comando
MOUSEABS:1306:858
```

**Resultado:** Mouse **pula instantaneamente** para a posição exata!

---

## 🎮 Integração com o Bot

Depois de instalar a biblioteca e carregar o sketch:

1. **Não precisa modificar nada no Python** - o código já está pronto!
2. O `ArduinoInputManager` vai automaticamente:
   - Tentar comando `MOUSEABS` primeiro
   - Se falhar (sem biblioteca), usar fallback relativo otimizado
3. Para testar, inicie o bot normalmente com **F9**

---

## 🔗 Links Úteis

- **Repositório AbsMouse:** https://github.com/jonathanedgecombe/absmouse
- **Documentação Arduino:** https://www.arduino.cc/en/Reference/HomePage
- **Forum Arduino:** https://forum.arduino.cc/

---

## ✅ Checklist Final

Antes de testar o bot, confirme:

- [ ] Biblioteca AbsMouse instalada
- [ ] Sketch `arduino_hid_controller_FIXED.ino` carregado no Arduino
- [ ] Resolução da tela configurada corretamente no sketch
- [ ] Serial Monitor mostra `READY` ao conectar
- [ ] Comando `MOUSEABS:960:540` move mouse para centro da tela
- [ ] Arduino IDE configurado para 115200 baud

Se todos os itens estiverem marcados, o sistema está pronto! 🎉

---

## 📝 Notas Técnicas

### Como funciona o AbsMouse?

A biblioteca **AbsMouse** modifica o HID descriptor do Arduino para simular um **tablet digitalizador** ao invés de um mouse comum. Tablets digitalizadores reportam posição absoluta (X,Y na tela) enquanto mouses reportam movimento relativo (deslocamento delta-X, delta-Y).

### Por que precisa da resolução da tela?

O Arduino precisa saber a resolução para calcular as coordenadas corretas no protocolo HID. Se configurar errado, as posições não vão corresponder à tela real.

### É seguro para detecção anti-cheat?

**Absolutamente!** Do ponto de vista do sistema operacional, o Arduino **É** um dispositivo USB HID legítimo. O movimento é indistinguível de um mouse/tablet real conectado ao PC.

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Autor:** Claude Code Assistant
**Data:** 2025-10-14
