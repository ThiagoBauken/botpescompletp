# FishingBot v4.0 - Guia de Distribuição

## 📦 Como Distribuir

Após compilar com `BUILD_EXE.bat`, você terá esta estrutura:

```
FishingBot_Release/
├── FishingBot.exe          ← Executável principal
├── templates/              ← Necessário! (40+ templates)
├── locales/                ← Necessário! (traduções PT/EN/RU)
├── config/                 ← Necessário! (configuração padrão)
└── README.md
```

### ⚠️ IMPORTANTE

**Distribua a pasta COMPLETA**, não apenas o .exe!

O executável precisa das pastas `templates`, `locales` e `config` para funcionar.

---

## 📥 Como Usuário Final Usa

1. **Extrair a pasta completa** em qualquer local
2. **Executar como Administrador** (botão direito → Executar como Administrador)
   - Necessário para hotkeys globais funcionarem
3. **Primeira execução:**
   - Criará pasta `data/` automaticamente
   - Pedirá licença (ou gerará licença de desenvolvimento)
4. **Pressionar F9** para iniciar

---

## 🗜️ Compactar para Distribuição

### Opção 1: ZIP Simples
```bash
# Compactar toda a pasta
"C:\Program Files\7-Zip\7z.exe" a -tzip FishingBot_v4.0.zip FishingBot_Release\
```

### Opção 2: Auto-Extrator (SFX)
```bash
# Criar instalador auto-extraível
"C:\Program Files\7-Zip\7z.exe" a -sfx7z.sfx FishingBot_v4.0_Installer.exe FishingBot_Release\
```

---

## 🛡️ Problemas com Antivírus

**Falsos Positivos São Comuns!**

PyInstaller executáveis frequentemente disparam alertas de antivírus devido a:
- Empacotamento de código Python
- Uso de `keyboard` e `pyautogui` (interceptação de input)
- Falta de assinatura digital

### Soluções:

1. **Assinar o executável** (requer certificado):
   ```bash
   signtool sign /f certificado.pfx /p senha /t http://timestamp.digicert.com FishingBot.exe
   ```

2. **Adicionar à lista de exceções** do antivírus

3. **Usar Nuitka** ao invés de PyInstaller (menos falsos positivos):
   ```bash
   pip install nuitka
   nuitka --standalone --onefile --windows-disable-console main.py
   ```

---

## 📊 Tamanho Esperado

| Componente | Tamanho |
|------------|---------|
| FishingBot.exe | ~50-80 MB |
| templates/ | ~5-10 MB |
| locales/ | ~50 KB |
| config/ | ~10 KB |
| **Total** | **~60-90 MB** |

---

## 🔧 Rebuilds

Para recompilar após mudanças no código:

```bash
# Limpar cache do PyInstaller
rmdir /S /Q build dist __pycache__

# Recompilar
pyinstaller FishingBot.spec
```

Ou simplesmente execute `BUILD_EXE.bat` novamente.

---

## 🚀 Distribuição Online

### GitHub Release

1. Criar tag de versão:
   ```bash
   git tag v4.0.0
   git push origin v4.0.0
   ```

2. No GitHub → Releases → Create Release
3. Upload do arquivo `FishingBot_v4.0.zip`

### Google Drive / Mega

Simplesmente faça upload do ZIP e compartilhe o link.

---

## 📝 Notas

- **Primeira execução pode ser lenta** (~5-10s) enquanto extrai arquivos temporários
- **Executável é portátil** - pode ser movido entre máquinas Windows
- **Requer Windows 10/11** (64-bit recomendado)
- **Python NÃO é necessário** no computador do usuário final
