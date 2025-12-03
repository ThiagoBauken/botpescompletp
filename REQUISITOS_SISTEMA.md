# Requisitos do Sistema - FishingMageBot

## O que precisa estar instalado no PC

### 1. **Visual C++ Redistributable** ⚠️ CRÍTICO
**Problema**: Sem isso, bibliotecas Python compiladas (numpy, opencv, pyautogui) não funcionam!

**Solução**: Instalar TODOS os pacotes:
- [Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- [Visual C++ 2015-2022 Redistributable (x86)](https://aka.ms/vs/17/release/vc_redist.x86.exe)
- [Visual C++ 2013 Redistributable (x64)](https://aka.ms/highdpimfc2013x64enu)
- [Visual C++ 2013 Redistributable (x86)](https://aka.ms/highdpimfc2013x86enu)

**Como verificar**:
```cmd
dir "C:\Windows\System32\vcruntime*.dll"
```
Se não aparecer vários arquivos, falta instalar!

---

### 2. **Python 3.13+ (se rodar como script)**
Se usar o `.exe` compilado → NÃO precisa de Python

Se rodar `python main.py` → Precisa de:
- Python 3.13 ou superior
- Todas as dependências do `requirements.txt`

**Instalar dependências**:
```cmd
pip install -r requirements.txt
```

---

### 3. **Arduino Driver (se usar Arduino)**
Se usar modo Arduino (não pyautogui):

**Windows 10/11**: Driver instala automaticamente ao conectar Arduino Pro Micro

**Windows 7/8**: Precisa instalar driver manualmente:
- [Arduino Leonardo/Pro Micro Driver](https://www.arduino.cc/en/software)

**Como verificar**:
1. Conectar Arduino
2. Abrir "Gerenciador de Dispositivos"
3. Procurar em "Portas (COM & LPT)"
4. Deve aparecer: "Arduino Leonardo (COM3)" ou similar

---

### 4. **Resolução de Tela**
⚠️ **IMPORTANTE**: O bot foi feito para **1920x1080**

**Se tiver outra resolução**:
- Os movimentos de câmera podem não funcionar corretamente
- Soluções:
  1. Mudar jogo para 1920x1080 (Fullscreen ou Windowed)
  2. OU: Ajustar valores na config (veja abaixo)

**Como verificar resolução**:
```cmd
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
```

---

### 5. **Sensibilidade do Mouse no Jogo**
⚠️ **CRÍTICO PARA MACRO DO BAÚ**

**Problema**: Se a sensibilidade do mouse no jogo for diferente, o macro não vai para o lugar certo!

**Solução**:
1. Abrir jogo → Configurações → Mouse
2. **Sensibilidade Mouse**: Anotar o valor
3. Testar abrir baú manualmente:
   - Segurar ALT
   - Mover mouse ~300px para esquerda/direita
   - Mover ~200px para baixo
   - Pressionar E

**Se não funcionar**: Ajustar valores na config (veja próxima seção)

---

## Configuração do Baú (config.json)

### Valores padrão (seu PC):
```json
{
  "chest_side": "right",
  "chest_distance": 1200,
  "chest_vertical_offset": 200
}
```

### Como ajustar para o PC dele:

#### 1. **Testar com valores menores primeiro**:
```json
{
  "chest_side": "left",
  "chest_distance": 300,
  "chest_vertical_offset": 200
}
```

#### 2. **Se ainda não funcionar, aumentar**:
```json
{
  "chest_side": "left",
  "chest_distance": 400,
  "chest_vertical_offset": 250
}
```

#### 3. **Sensibilidade ALTA no jogo → valores MENORES**:
```json
{
  "chest_distance": 200,
  "chest_vertical_offset": 150
}
```

#### 4. **Sensibilidade BAIXA no jogo → valores MAIORES**:
```json
{
  "chest_distance": 500,
  "chest_vertical_offset": 300
}
```

---

## Logs de Debug (para ver o que está acontecendo)

Com as correções que fiz, os logs agora mostram:

```
🧭 [CHEST] Lado do baú: 'left' → normalizado: 'left'
📐 [CHEST] Movimento calculado:
   Horizontal (DX): +300 (←esquerda)
   Vertical (DY): +200 (↓baixo)
   Config atual: distance=300, vertical_offset=200
```

**Como usar os logs**:
1. Rodar o bot
2. Tentar abrir baú (F6)
3. Ver nos logs se está indo para o lado certo
4. Ajustar valores conforme necessário

---

## Checklist Completo

### No PC que NÃO funciona:

- [ ] Visual C++ Redistributable instalado (2013, 2015-2022, x86 e x64)
- [ ] Resolução de tela: 1920x1080
- [ ] Sensibilidade do mouse no jogo: Anotar valor
- [ ] Arduino conectado (se usar modo Arduino): Verificar COM port
- [ ] Config do baú: Ajustar `distance` e `vertical_offset`
- [ ] Logs mostrando movimento correto: Ver setas ←→↓

### Teste Manual:

1. **Abrir o jogo**
2. **Segurar ALT** (modo freelook)
3. **Mover mouse** ~300px para esquerda/direita
4. **Mover mouse** ~200px para baixo
5. **Pressionar E**
6. Baú deve abrir! ✅

Se não abrir → Ajustar valores na config

---

## Instalação Rápida (Copiar/Colar no CMD)

```cmd
REM 1. Baixar e instalar Visual C++ Redistributable
start https://aka.ms/vs/17/release/vc_redist.x64.exe
start https://aka.ms/vs/17/release/vc_redist.x86.exe

REM 2. Verificar resolução
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution

REM 3. Testar bot
python main.py
```

---

## Diferenças entre PCs

| Item | Seu PC | PC dele | Solução |
|------|--------|---------|---------|
| Visual C++ | ✅ Instalado | ❌ Falta | Instalar |
| Resolução | 1920x1080 | ??? | Verificar |
| Sensibilidade | X | Y | Ajustar config |
| Distance | 1200 | 1200 | Pode precisar ajustar |
| Vertical offset | 200 | 200 | Pode precisar ajustar |

---

## FAQ

**Q: "O bot abre, mas não faz nada ao apertar F9"**
A: Falta Visual C++ Redistributable

**Q: "O baú não abre, só move a câmera"**
A: Ajustar `distance` e `vertical_offset` na config

**Q: "Vai pro lado errado"**
A: Trocar `chest_side` de "left" para "right" (ou vice-versa)

**Q: "Vai muito pouco/muito"**
A: Aumentar/diminuir valores de `distance` e `vertical_offset`

**Q: "Arduino não conecta"**
A: Instalar driver do Arduino Pro Micro

---

## Suporte

Se ainda não funcionar depois de seguir este checklist, envie:

1. **Screenshot dos logs** quando tentar abrir baú
2. **Resolução da tela**: `wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution`
3. **Visual C++ instalado**: `dir "C:\Windows\System32\vcruntime*.dll"`
4. **Config atual**: Conteúdo de `data/config.json`
