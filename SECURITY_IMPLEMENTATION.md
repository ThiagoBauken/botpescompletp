# 🔐 Security Implementation Guide - Ultimate Fishing Bot v5.0

Este documento descreve o sistema de segurança implementado para proteger o código-fonte, dados sensíveis e licenças do Ultimate Fishing Bot v5.0.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura de Segurança](#arquitetura-de-segurança)
3. [Componentes Implementados](#componentes-implementados)
4. [Guia de Uso](#guia-de-uso)
5. [Processo de Build](#processo-de-build)
6. [Níveis de Proteção](#níveis-de-proteção)
7. [Troubleshooting](#troubleshooting)

---

## Visão Geral

### ✅ O que foi implementado:

1. **AES-256 Encryption** - Criptografia forte para dados em repouso
2. **String Obfuscation** - Ofuscação de strings críticas no código
3. **License Encryption** - Licenças salvas criptografadas
4. **Nuitka Compilation** - Compilação para executável nativo
5. **Build Automation** - Scripts automatizados de build

### 🎯 Objetivos de Segurança:

- ✅ **Proteger URLs de API** no binário compilado
- ✅ **Proteger Project IDs** contra extração
- ✅ **Criptografar licenças** salvas localmente
- ✅ **Dificultar engenharia reversa** do código Python
- ✅ **Automatizar processo** de build seguro

---

## Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────────┐
│               DESENVOLVIMENTO (Source Code)              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Código Python original                              │
│     ├─ URLs: "https://api.example.com"                  │
│     ├─ Project ID: "12345-67890"                        │
│     └─ Licenças salvas em plaintext                     │
│                                                          │
│  ⬇️  PASSO 1: Ofuscação de Strings                      │
│                                                          │
│  2. obfuscate_secrets.py                                │
│     ├─ Substitui URLs por deobfuscate("eJwrSS...")     │
│     ├─ Substitui IDs por deobfuscate("kj3H8x...")      │
│     └─ Cria backups (.bak)                              │
│                                                          │
│  ⬇️  PASSO 2: Compilação Nuitka                         │
│                                                          │
│  3. build_nuitka.py                                     │
│     ├─ Compila Python → C → Binário                     │
│     ├─ Inclui templates/locales                         │
│     └─ Gera executável standalone                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           ⬇️
┌─────────────────────────────────────────────────────────┐
│                DISTRIBUIÇÃO (Binary)                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  UltimateFishingBot.exe                                 │
│  ├─ Código C compilado (não reversível para Python)    │
│  ├─ Strings ofuscadas (não legíveis com strings.exe)   │
│  └─ Templates/Locales embedados                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           ⬇️
┌─────────────────────────────────────────────────────────┐
│                  EXECUÇÃO (Runtime)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Strings deofuscadas na MEMÓRIA                      │
│     └─ "https://api.example.com" (normal)               │
│                                                          │
│  2. Servidor recebe requisições NORMAIS                 │
│     └─ Sem impacto na comunicação                       │
│                                                          │
│  3. Licenças criptografadas com AES-256                 │
│     ├─ license.key: "eJy7xK3mP..."                      │
│     └─ Descriptografada apenas durante validação        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Componentes Implementados

### 1. CryptoManager (`utils/crypto_manager.py`)

**Propósito:** Criptografia AES-256-CBC para dados em repouso

**Características:**
- ✅ AES-256 (FIPS 197 approved)
- ✅ Modo CBC (Cipher Block Chaining)
- ✅ PBKDF2-HMAC-SHA256 (100k iterations)
- ✅ Salt e IV únicos por criptografia
- ✅ Padding PKCS7

**Uso:**
```python
from utils.crypto_manager import CryptoManager

crypto = CryptoManager()

# Criptografar
encrypted = crypto.encrypt("dados sensíveis")

# Descriptografar
decrypted = crypto.decrypt(encrypted)
```

**Onde é usado:**
- `license_manager.py` - Salvar/carregar licenças criptografadas
- Qualquer dado que precise ser armazenado com segurança

---

### 2. StringObfuscator (`utils/string_obfuscator.py`)

**Propósito:** Ofuscar strings no código-fonte antes da compilação

**Técnicas aplicadas:**
1. UTF-8 encode
2. Compressão zlib (nível 9)
3. XOR com chave rotativa
4. Reversão de bytes
5. Base64 encoding

**Uso:**
```python
from utils.string_obfuscator import obfuscate, deobfuscate

# Ofuscar
hidden = obfuscate("https://api.example.com")
# → "eJwrSS0uUShKLS5OTVEoycxN..."

# Deofuscar
original = deobfuscate(hidden)
# → "https://api.example.com"
```

**Onde é usado:**
- `obfuscate_secrets.py` - Substituir strings no código automaticamente
- Build process - Proteger URLs/IDs no binário

---

### 3. Obfuscate Secrets Script (`build_tools/obfuscate_secrets.py`)

**Propósito:** Automatizar substituição de strings sensíveis

**Strings protegidas:**
```python
SECRETS_TO_OBFUSCATE = {
    'https://private-keygen.pbzgje.easypanel.host': 'LICENSE_SERVER_URL',
    'wss://private-serverpesca.pbzgje.easypanel.host/ws': 'WS_SERVER_URL',
    '67a4a76a-d71b-4d07-9ba8-f7e794ce0578': 'PROJECT_ID',
    'UltimateFishingBot/4.0': 'USER_AGENT',
}
```

**Processo:**
1. Lê arquivos Python (`license_manager.py`, `main.py`)
2. Cria backups (`.bak`)
3. Substitui strings por versões ofuscadas
4. Adiciona import `from utils.string_obfuscator import deobfuscate as _d`

**Antes:**
```python
self.server_url = "https://private-keygen.pbzgje.easypanel.host"
```

**Depois:**
```python
from utils.string_obfuscator import deobfuscate as _d
self.server_url = _d("eJwrSS0uUShKLS5OTVEoycxNVXDOL...")  # LICENSE_SERVER_URL
```

**Reversível:**
- Opção 2 no menu restaura backups `.bak`

---

### 4. Nuitka Build Script (`build_tools/build_nuitka.py`)

**Propósito:** Compilar Python para executável nativo

**Características:**
```python
BUILD_CONFIG = {
    "standalone": True,        # Executável independente
    "onefile": True,           # Arquivo único
    "windows_disable_console": False,  # Mostrar console (debug)
    "plugins": ["tk-inter"],   # Plugins necessários
    "lto": "yes",              # Link Time Optimization
    "jobs": 4,                 # Compilação paralela
}
```

**Otimizações aplicadas:**
- ✅ Compilação Python → C → Binário
- ✅ LTO (Link Time Optimization)
- ✅ Embedar templates/locales no executável
- ✅ Metadados de versão (Windows)
- ✅ Remoção de arquivos temporários

**Tamanho esperado do executável:**
- ~50-150 MB (incluindo Python runtime + dependências)

---

### 5. License Manager Updates (`utils/license_manager.py`)

**Proteções adicionadas:**

#### Salvar licença (criptografada):
```python
def save_license(self, key: str) -> bool:
    if self.crypto:
        encrypted_key = self.crypto.encrypt(key)
        # Salva versão criptografada
    else:
        # Fallback: plaintext
```

#### Carregar licença (com fallback):
```python
def load_license(self) -> Optional[str]:
    if self.crypto:
        try:
            license_key = self.crypto.decrypt(stored_data)
        except:
            # Fallback: licença antiga em plaintext
            license_key = stored_data
```

**Compatibilidade:**
- ✅ Lê licenças antigas (plaintext)
- ✅ Salva novas licenças (criptografadas)
- ✅ Não quebra instalações existentes

---

## Guia de Uso

### Preparação do Ambiente

1. **Instalar dependências de segurança:**
```bash
pip install cryptography
pip install nuitka
```

2. **Verificar instalação:**
```bash
python -c "from utils.crypto_manager import CryptoManager; print('OK')"
python -m nuitka --version
```

---

### Processo de Build Seguro

#### PASSO 1: Ofuscar Strings Sensíveis

```bash
cd build_tools
python obfuscate_secrets.py
```

**Menu interativo:**
```
Opções:
  1. Ofuscar secrets (criar backups .bak)
  2. Restaurar backups
  3. Sair

Escolha uma opção (1-3): 1
```

**O que acontece:**
- ✅ Cria backups: `license_manager.py.bak`, `main.py.bak`
- ✅ Substitui strings sensíveis por versões ofuscadas
- ✅ Adiciona import do deobfuscator

**Arquivos modificados:**
- `utils/license_manager.py`
- `main.py`

---

#### PASSO 2: Testar Código Ofuscado

```bash
python main.py
```

**Verificar:**
- ✅ Bot inicia normalmente
- ✅ Licença valida corretamente
- ✅ Conexão com servidor funciona
- ✅ Todas as URLs estão acessíveis

**Se houver erros:**
```bash
cd build_tools
python obfuscate_secrets.py
# Escolha opção 2 (Restaurar backups)
```

---

#### PASSO 3: Compilar com Nuitka

```bash
cd build_tools
python build_nuitka.py
```

**Processo interativo:**
1. Verifica se Nuitka está instalado
2. Confirma se strings foram ofuscadas
3. Opção de limpar builds antigos
4. Mostra configuração
5. Inicia compilação (5-15 minutos)

**Output esperado:**
```
✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!
📍 Local: dist\main.exe
📦 Tamanho: 87.45 MB

🔒 Proteções aplicadas:
   ✅ Código compilado para C
   ✅ Strings ofuscadas
   ✅ Licenças criptografadas com AES-256
```

---

#### PASSO 4: Testar Executável

```bash
cd dist
.\main.exe
```

**Verificar:**
- ✅ Executável inicia sem erros
- ✅ Interface gráfica carrega
- ✅ Templates são detectados
- ✅ Sistema de licenças funciona
- ✅ Conexão com servidor OK

---

#### PASSO 5: Distribuir

**Checklist antes de distribuir:**
- [ ] Testado em máquina limpa (sem Python instalado)
- [ ] Todas as funcionalidades funcionam
- [ ] Licenciamento validando corretamente
- [ ] Templates incluídos no executável
- [ ] Sem dependências externas

**Opcional - Assinatura Digital:**
```bash
# Windows (requer certificado)
signtool sign /f certificado.pfx /p senha /t http://timestamp.digicert.com main.exe
```

---

## Níveis de Proteção

### 🟢 Nível 1: Usuários Casuais (BLOQUEADO)

**Tentativa:** Abrir `.exe` com editor de texto/hex

**Resultado:**
- ❌ Código Python não visível (compilado para C)
- ❌ URLs ofuscadas (não legíveis)
- ❌ Strings como `deobfuscate("eJy...")` não fazem sentido

**Proteção:** ✅ EFETIVA

---

### 🟡 Nível 2: Crackers Amadores (DIFICULTADO)

**Tentativa:** Usar ferramentas como `strings.exe`, `Detect It Easy`

**Resultado:**
- ❌ URLs não aparecem em strings do binário
- ❌ Python bytecode não extraível (compilado)
- ⚠️ Podem ver funções `deobfuscate()` mas não sabem usar

**Proteção:** ✅ DIFICULTA BASTANTE

---

### 🔴 Nível 3: Crackers Profissionais (ATRASADO)

**Tentativa:** Debugger (x64dbg), análise de memória, hooking de APIs

**Resultado:**
- ⚠️ Com **muito trabalho**, podem:
  - Debugar runtime e ver strings descriptografadas na memória
  - Hook functions como `requests.post()` e capturar URLs
  - Analisar fluxo do programa e entender lógica

**Proteção:** ⚠️ ATRASA (mas não impede 100%)

**Mitigações adicionais (não implementadas):**
- Anti-debugging checks
- Code signing
- VM detection
- Obfuscação de control flow

---

### 📊 Comparação de Proteção

| Técnica | Vs Casual | Vs Amador | Vs Profissional |
|---------|-----------|-----------|-----------------|
| **Nenhuma (Python .py)** | ❌ | ❌ | ❌ |
| **PyInstaller** | ✅ | ⚠️ | ❌ |
| **PyArmor Free** | ✅ | ✅ | ⚠️ |
| **Nuitka** | ✅ | ✅ | ⚠️ |
| **Nuitka + Ofuscação** | ✅ | ✅ | ⚠️ |
| **Nossa Implementação** | ✅✅ | ✅✅ | ⚠️⚠️ |

---

## Troubleshooting

### ❌ Problema: "Nuitka not found"

**Solução:**
```bash
pip install -U nuitka
```

---

### ❌ Problema: "ImportError: No module named 'cryptography'"

**Solução:**
```bash
pip install cryptography
```

---

### ❌ Problema: Executável não inicia (missing DLLs)

**Causa:** Modo standalone não incluiu todas as DLLs

**Solução:**
1. Editar `build_nuitka.py`:
```python
BUILD_CONFIG = {
    "standalone": True,
    "onefile": False,  # Mudar para False temporariamente
}
```

2. Recompilar e verificar quais DLLs estão em `dist/main.dist/`

---

### ❌ Problema: "ModuleNotFoundError: No module named 'utils.string_obfuscator'"

**Causa:** Nuitka não incluiu módulo customizado

**Solução:**
```bash
# Em build_nuitka.py, adicionar:
cmd.append("--include-package=utils")
```

---

### ❌ Problema: Templates não encontrados no executável

**Causa:** Diretório `templates/` não foi embedado

**Verificar em `build_nuitka.py`:**
```python
"include_data_dirs": [
    ("templates", "templates"),  # ← Deve estar presente
]
```

---

### ⚠️ Problema: Servidor não aceita requisições após compilação

**Diagnóstico:**

1. **Verificar se strings foram descriptografadas:**
```python
# Adicionar log temporário em license_manager.py
print(f"DEBUG: server_url = {self.server_url}")
```

2. **Testar manualmente:**
```bash
# Antes de compilar
python -c "from utils.string_obfuscator import deobfuscate; print(deobfuscate('eJy...'))"
```

**Causa comum:** String ofuscada incorretamente

**Solução:** Restaurar backup e reofuscar

---

### 🔧 Problema: Build muito lento (>30 minutos)

**Otimizações:**

1. **Aumentar threads:**
```python
"jobs": 8,  # Usar mais cores da CPU
```

2. **Desabilitar LTO temporariamente:**
```python
"lto": "no",  # Mais rápido, mas binário maior
```

3. **Usar cache do Nuitka:**
- Não deletar `main.build/` entre compilações

---

## Arquivos Importantes

### 📁 Estrutura de Arquivos de Segurança

```
v5/
├── utils/
│   ├── crypto_manager.py          # ✅ Criptografia AES-256
│   ├── string_obfuscator.py       # ✅ Ofuscação de strings
│   └── license_manager.py         # ✅ Atualizado com crypto
│
├── build_tools/
│   ├── obfuscate_secrets.py       # ✅ Script de ofuscação
│   └── build_nuitka.py            # ✅ Script de build
│
├── .secrets.example.json          # ✅ Template de secrets
├── .gitignore                     # ✅ Atualizado (ignora .secrets.json)
│
└── SECURITY_IMPLEMENTATION.md     # ✅ Este arquivo
```

---

## Checklist de Segurança

Antes de distribuir executável:

- [ ] ✅ Executado `obfuscate_secrets.py` (opção 1)
- [ ] ✅ Testado código ofuscado com `python main.py`
- [ ] ✅ Compilado com `build_nuitka.py`
- [ ] ✅ Testado executável em máquina limpa
- [ ] ✅ Verificado que URLs não aparecem em `strings main.exe`
- [ ] ✅ Testado licenciamento funciona
- [ ] ✅ Testado conexão com servidor
- [ ] ✅ Verificado tamanho do executável razoável (<200 MB)
- [ ] ⚠️ (Opcional) Assinado digitalmente com certificado
- [ ] ✅ Removido backups `.bak` do repositório
- [ ] ✅ Verificado `.secrets.json` não está no git

---

## Dependências

### Python Packages:
```bash
cryptography>=41.0.0    # AES-256 encryption
nuitka>=1.8.0           # Python → C compiler
```

### Instalação completa:
```bash
pip install -r requirements.txt
pip install cryptography nuitka
```

---

## Suporte

### Problemas com segurança:
- Verificar logs em `data/logs/`
- Executar testes: `python utils/crypto_manager.py`
- Executar testes: `python utils/string_obfuscator.py`

### Problemas com build:
- Verificar versão do Nuitka: `python -m nuitka --version`
- Limpar cache: deletar `main.build/` e `dist/`
- Verificar espaço em disco (build precisa ~2GB temporariamente)

---

## Changelog

### v5.0.0 (2025-10-31)
- ✅ Implementação inicial de CryptoManager (AES-256)
- ✅ Implementação de StringObfuscator
- ✅ Script automatizado de ofuscação
- ✅ Script automatizado de build Nuitka
- ✅ Atualização do LicenseManager com criptografia
- ✅ Documentação completa de segurança

---

## Disclaimer

⚠️ **IMPORTANTE:**

Este sistema de segurança foi projetado para:
- ✅ Proteger contra usuários casuais
- ✅ Dificultar engenharia reversa básica
- ✅ Criptografar dados sensíveis em repouso

**NÃO garante:**
- ❌ Proteção 100% contra crackers profissionais
- ❌ Impossibilidade de extração de strings em runtime
- ❌ Proteção contra análise de memória

**Nenhum sistema de proteção é 100% inquebrável.**

O objetivo é **aumentar significativamente o esforço** necessário para reverter o software, tornando-o comercialmente inviável para a maioria dos atacantes.

---

## Licença

Este sistema de segurança faz parte do Ultimate Fishing Bot v5.0 e está sujeito aos mesmos termos de licença do projeto principal.

---

**Última atualização:** 2025-10-31
**Versão:** 5.0.0
**Autor:** Ultimate Fishing Bot Team
