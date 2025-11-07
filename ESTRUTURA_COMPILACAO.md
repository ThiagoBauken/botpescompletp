# 📁 Estrutura de Pastas - Fishing MageBOT v5.0 Compilado

## 🎯 Estrutura Após Compilação

Quando você compila o projeto usando **PyInstaller** (`BUILD_EXE.bat`) ou **Nuitka** (`BUILD_NUITKA.bat`), a estrutura final será:

```
📦 dist/FishingMageBOT/
│
├── 🎯 FishingMageBOT.exe          # Executável principal
│   └── (PyInstaller: ~50-80MB | Nuitka: ~30-50MB)
│
│   └── (GIF agora está dentro de templates/)
│
├── 📂 templates/                   # Imagens para detecção OpenCV
│   ├── motion.gif                 # 🎨 GIF animado do mago (161 frames)
│   ├── catch.png                  # Detecção de peixe capturado
│   ├── varanobauci.png            # Vara com isca
│   ├── enbausi.png                # Vara sem isca
│   ├── varaquebrada.png           # Vara quebrada
│   ├── inventory.png              # Inventário aberto
│   ├── filefrito.png              # Comida
│   ├── carneurso.png              # Isca: carne de urso
│   ├── carnedelobo.png            # Isca: carne de lobo
│   ├── grub.png                   # Isca: grub
│   ├── minhoca.png                # Isca: minhoca
│   └── ... (40+ templates + GIF)
│
├── 🌍 locales/                     # Traduções (4 idiomas)
│   ├── pt_BR/
│   │   └── ui.json                # Português
│   ├── en_US/
│   │   └── ui.json                # English
│   ├── es_ES/
│   │   └── ui.json                # Español
│   └── ru_RU/
│       └── ui.json                # Русский
│
├── ⚙️ config/                      # Configurações padrão
│   └── default_config.json        # Valores padrão do sistema
│
├── 💾 data/                        # Dados do usuário (auto-criado)
│   ├── config.json                # Configurações personalizadas
│   ├── license.key                # Licença ativada
│   ├── credentials.json           # Credenciais WebSocket
│   └── logs/                      # Logs do sistema
│       ├── fishing_bot_2025-11-01.log
│       ├── ui_2025-11-01.log
│       └── performance_2025-11-01.log
│
├── 📚 _internal/                   # (Apenas PyInstaller)
│   └── (Bibliotecas Python e DLLs)
│
└── 📝 README.txt                   # Instruções de uso
```

---

## 🔑 Arquivos Essenciais que DEVEM ser Incluídos

### 1. **GIF Animado** ✨
- **Nome:** `motion.gif`
- **Localização:** Pasta `templates/`
- **Tamanho:** ~2-3 MB
- **Uso:** Animação na interface (mago pescando)
- **Comportamento:**
  - Aparece à esquerda e à direita do título "Fishing MageBOT"
  - Anima quando o bot está rodando
  - Fica estático quando o bot está parado
  - Preserva proporções originais (832x480 → redimensionado para 124x72px)

### 2. **Templates (Pasta Completa)**
- **Obrigatório:** Todos os 40+ arquivos PNG
- **Críticos:**
  - `catch.png` - Sem ele o bot não detecta peixes
  - `varanobauci.png` / `enbausi.png` - Sistema de varas
  - `inventory.png` - Detecção de inventário
  - `filefrito.png` - Sistema de alimentação

### 3. **Locales (4 idiomas)**
- Todos os 4 arquivos JSON devem estar presentes
- Usuário pode trocar idioma no canto inferior direito da UI

### 4. **Config**
- `default_config.json` é o fallback se usuário não tiver config próprio

---

## 🚀 Como o GIF é Carregado no Código

No arquivo [ui/main_window.py](ui/main_window.py), linha ~800:

```python
def load_animated_gif(self):
    """Carregar e animar o GIF do mago pescando"""
    gif_path = "motion2Fast_Mago_pescando_a_gua_ondula_suavemente_enquanto_um__0.gif"

    if not os.path.exists(gif_path):
        print(f"[WARN] GIF não encontrado: {gif_path}")
        return

    # Carrega todos os 161 frames
    self.gif_image = Image.open(gif_path)
    for frame in ImageSequence.Iterator(self.gif_image):
        # Preserva proporção original (832x480)
        original_width, original_height = frame.size
        target_height = 72
        aspect_ratio = original_width / original_height
        target_width = int(target_height * aspect_ratio)
        # Resultado: 124x72 pixels
        ...
```

### ⚡ Animação Controlada por Estado

```python
def start_bot(self):
    # Quando bot inicia...
    self.start_gif_animation()  # GIF começa a animar

def pause_bot(self):
    # Quando pausar...
    self.stop_gif_animation()   # GIF para de animar

def stop_bot(self):
    # Quando parar...
    self.stop_gif_animation()   # GIF para de animar
```

---

## 📦 Compilação com Nuitka vs PyInstaller

### **PyInstaller** (`BUILD_EXE.bat`)
```batch
pyinstaller --add-data "templates\motion.gif;templates"
```
- **Sintaxe:** `arquivo_origem;destino_no_exe`
- **Resultado:** GIF fica em `dist/FishingMageBOT/templates/motion.gif`

### **Nuitka** (`BUILD_NUITKA.bat`)
```batch
nuitka --include-data-file=templates\motion.gif=templates\motion.gif
```
- **Sintaxe:** `arquivo_origem=destino_no_exe`
- **Resultado:** GIF fica em `dist/FishingMageBOT/templates/motion.gif`

---

## ✅ Checklist Pré-Distribuição

Antes de enviar o ZIP para usuários, confirme:

- [ ] `FishingMageBOT.exe` existe e abre sem erros
- [ ] **GIF** `motion2Fast_Mago_pescando_a_gua_ondula_suavemente_enquanto_um__0.gif` está na raiz
- [ ] Pasta `templates/` com 40+ PNGs
- [ ] Pasta `locales/` com 4 subpastas (pt_BR, en_US, es_ES, ru_RU)
- [ ] Pasta `config/` com `default_config.json`
- [ ] Pasta `data/` vazia (será preenchida pelo usuário)
- [ ] `README.txt` com instruções

---

## 🐛 Troubleshooting

### ❌ "GIF não encontrado"
**Causa:** Arquivo não está na mesma pasta do .exe
**Solução:** Verifique se o GIF está em `dist/FishingMageBOT/` junto com o executável

### ❌ GIF não anima
**Causa:** Pillow não incluído na compilação
**Solução:**
- PyInstaller: `--hidden-import=PIL`
- Nuitka: `--include-package=PIL`

### ❌ Erro ao carregar frames
**Causa:** GIF corrompido ou formato incompatível
**Solução:** Re-download do GIF original, verificar que tem 161 frames

---

## 📊 Tamanhos Aproximados

| Item | Tamanho |
|------|---------|
| GIF animado | ~2-3 MB |
| Templates (40+ PNGs) | ~5-8 MB |
| Locales (4 idiomas) | ~100 KB |
| Config | ~20 KB |
| **PyInstaller .exe** | 50-80 MB |
| **Nuitka .exe** | 30-50 MB |
| **ZIP final** | 80-120 MB |

---

## 🎨 Detalhes do GIF

- **Resolução Original:** 832x480 pixels
- **Frames Totais:** 161
- **Taxa de Frames:** Variável (definida por frame)
- **Formato:** GIF animado
- **Duração Total:** ~10-15 segundos (loop infinito)
- **Redimensionamento na UI:** 124x72 pixels (preserva aspect ratio 1.733:1)

---

## 🔄 Fluxo de Compilação

```
┌─────────────────┐
│  Código Fonte   │
│   + GIF + PNG   │
└────────┬────────┘
         │
         ├─────────┐
         │         │
    PyInstaller  Nuitka
         │         │
         ↓         ↓
    ┌────────────────┐
    │  dist/         │
    │  FishingMageBOT│
    │  ├── .exe      │
    │  ├── GIF       │◄── GIF copiado para raiz
    │  ├── templates/│
    │  ├── locales/  │
    │  ├── config/   │
    │  └── data/     │
    └────────────────┘
         │
         ↓
    Comprimir em ZIP
         │
         ↓
    Distribuir para usuários
```

---

## 💡 Dicas para Desenvolvedores

1. **Testar sem compilar:** Execute `python main.py` - o GIF deve aparecer
2. **Testar pós-compilação:** Execute o .exe em outra máquina limpa
3. **Logs úteis:** Procure por `[OK] GIF carregado com 161 frames` no console
4. **Performance:** Nuitka é 3-5x mais rápido que PyInstaller para carregar GIF
5. **Tamanho:** Se o ZIP estiver muito grande (>150MB), considere otimizar o GIF

---

## 📞 Suporte

Se tiver problemas com o GIF na compilação:

1. Verifique o log de compilação para warnings sobre PIL/Pillow
2. Teste o GIF separadamente: `python test_gif.py`
3. Confirme que Pillow está instalado: `pip show Pillow`
4. Use `--log-level DEBUG` no Nuitka para mais informações

---

**Última Atualização:** 2025-11-01
**Versão do Bot:** v5.0
**Python:** 3.13+
**Pillow:** 11.0.0+
