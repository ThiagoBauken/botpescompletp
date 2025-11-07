# 🔐 Dois Diálogos DIFERENTES de Autenticação

## 🎯 O Que Você Está Vendo

Quando você roda `main.py`, **DOIS diálogos diferentes** podem aparecer:

---

## 1️⃣ **LicenseDialog** (APARECE PRIMEIRO)

📂 **Arquivo:** [ui/license_dialog.py](ui/license_dialog.py:1)

### Visual:
```
┌───────────────────────────────────────┐
│  🔐 Ultimate Fishing Bot v4.0 - Licença │
├───────────────────────────────────────┤
│                                       │
│  Insira sua License Key:              │
│  ┌─────────────────────────────────┐  │
│  │ XXXX-XXXX-XXXX-XXXX             │  │
│  └─────────────────────────────────┘  │
│                                       │
│  [  Ativar  ]  [  Cancelar  ]        │
│                                       │
└───────────────────────────────────────┘
```

### Campos:
- ✅ **APENAS License Key** (campo único)

### Função:
- Validar licença do **Keymaster**
- Autenticação **local** (não conecta ao servidor)
- Salva em: `data/license.key`

### Quando aparece:
- ✅ **SEMPRE** na primeira execução
- ✅ Quando `data/license.key` não existe ou é inválida
- ✅ **Independente** de servidor

### Código ([main.py:77-89](main.py#L77-L89)):
```python
if not license_manager.check_license():
    license_dialog = LicenseDialog(license_manager)
    license_key = license_dialog.show()

    if license_key:
        valid, data = license_manager.validate_license(license_key)
        if valid:
            print("✅ Licença ativada!")
```

---

## 2️⃣ **ActivationDialog** (APARECE DEPOIS - SE LICENÇA VÁLIDA)

📂 **Arquivo:** [client/activation_dialog.py](client/activation_dialog.py:1)

### Visual:
```
┌───────────────────────────────────────┐
│  🔐 Ativação - Fishing Bot            │
├───────────────────────────────────────┤
│  🎣 Fishing Bot                       │
│  Ative sua licença para começar       │
│                                       │
│  Login:                               │
│  ┌─────────────────────────────────┐  │
│  │ user@email.com                  │  │
│  └─────────────────────────────────┘  │
│                                       │
│  Senha (opcional):                    │
│  ┌─────────────────────────────────┐  │
│  │ ●●●●●●●●                        │  │
│  └─────────────────────────────────┘  │
│                                       │
│  License Key:                         │
│  ┌─────────────────────────────────┐  │
│  │ XXXX-XXXX-XXXX-XXXX             │  │
│  └─────────────────────────────────┘  │
│                                       │
│  ☑ Manter conectado (salvar creds)    │
│                                       │
│  [  🚀 Ativar  ]  [  Cancelar  ]     │
└───────────────────────────────────────┘
```

### Campos:
- ✅ **Login** (email ou username)
- ✅ **Senha** (opcional - para o servidor)
- ✅ **License Key** (mesma do Keymaster)
- ✅ **Checkbox:** Manter conectado

### Função:
- Autenticação no **servidor multi-usuário**
- Conectar via **WebSocket** (wss://)
- Salva em: `data/credentials.json`

### Quando aparece:
- ✅ **APENAS SE** licença já está válida
- ✅ **APENAS SE** servidor multi-usuário está ativo
- ✅ **APENAS SE** `data/credentials.json` não existe
- ❌ **NUNCA** aparece se licença inválida

### Código ([main.py:159-201](main.py#L159-L201)):
```python
# SÓ EXECUTA SE LICENÇA VÁLIDA
if license_manager and license_manager.is_licensed():
    cred_manager = CredentialManager()
    saved_credentials = cred_manager.load_credentials()

    if not saved_credentials:
        # AQUI: Mostra ActivationDialog
        activation_dialog = ActivationDialog()
        activation_result = activation_dialog.show()

        if activation_result:
            login = activation_result['login']
            password = activation_result['password']
            license_key = activation_result['license_key']

            if activation_result['remember']:
                cred_manager.save_credentials(login, password, license_key)
```

---

## 🔄 Fluxo Completo: Qual Diálogo Aparece?

### Cenário 1: Primeira Execução (Sem Licença)
```
1. Iniciar main.py
   ↓
2. LicenseDialog aparece (pede LICENSE KEY)
   ↓
3. Usuario insere: XXXX-XXXX-XXXX-XXXX
   ↓
4. Valida no Keymaster
   ↓
5. Se válida → Salva em data/license.key
   ↓
6. Bot inicia normalmente (modo standalone)
   ↓
❌ ActivationDialog NÃO aparece
   (porque não tem servidor configurado)
```

---

### Cenário 2: Licença Válida + Servidor Ativo
```
1. Iniciar main.py
   ↓
2. LicenseDialog NÃO aparece (licença OK)
   ↓
3. Verifica: servidor multi-usuário ativo?
   ↓
4. SIM → Verifica: credentials.json existe?
   ↓
5. NÃO → ActivationDialog aparece
   ↓
6. Usuario preenche:
   - Login: user@email.com
   - Senha: minhasenha123
   - License Key: XXXX-XXXX-XXXX-XXXX
   - ☑ Manter conectado
   ↓
7. Salva em data/credentials.json
   ↓
8. Conecta ao servidor via WebSocket
   ↓
✅ Bot inicia em modo cliente-servidor
```

---

### Cenário 3: Já Tem Tudo Salvo
```
1. Iniciar main.py
   ↓
2. LicenseDialog NÃO aparece (data/license.key existe)
   ↓
3. ActivationDialog NÃO aparece (data/credentials.json existe)
   ↓
4. Carrega credenciais automaticamente
   ↓
5. Conecta ao servidor
   ↓
✅ Bot inicia direto (sem diálogos)
```

---

## 📊 Comparação Lado a Lado

| Característica | LicenseDialog | ActivationDialog |
|----------------|---------------|------------------|
| **Arquivo** | ui/license_dialog.py | client/activation_dialog.py |
| **Quando aparece** | Primeira execução (sempre) | Após licença válida + servidor ativo |
| **Campos** | 1 campo (License Key) | 4 campos (Login/Senha/Key/Checkbox) |
| **Função** | Validar licença local | Autenticar no servidor |
| **Salva em** | data/license.key | data/credentials.json |
| **Conecta ao servidor** | ❌ Não | ✅ Sim (WebSocket) |
| **Modo** | Standalone | Cliente-Servidor |
| **Obrigatório** | ✅ Sim (sempre) | ❌ Não (apenas se servidor ativo) |

---

## ❓ FAQ

### Q: Por que o ActivationDialog não aparece para mim?
**A:** Você provavelmente está no **modo standalone** (sem servidor). O ActivationDialog só aparece se:
1. Licença está válida (LicenseDialog já foi preenchido)
2. Servidor multi-usuário está configurado
3. `data/credentials.json` não existe

### Q: Posso usar apenas o LicenseDialog?
**A:** SIM! O bot funciona perfeitamente apenas com o LicenseDialog (modo standalone v3/v4).

### Q: Qual a diferença entre as duas license keys?
**A:** É a **MESMA** license key! Você insere a mesma chave em ambos os diálogos:
- LicenseDialog: Valida localmente
- ActivationDialog: Envia ao servidor junto com login/senha

### Q: Como forçar o ActivationDialog a aparecer?
**A:**
1. Tenha licença válida (preencha LicenseDialog)
2. Configure servidor em `config.json`:
   ```json
   "server": {
     "url": "wss://seu-servidor.com/ws"
   }
   ```
3. Delete `data/credentials.json`
4. Reinicie main.py

### Q: Posso pular o ActivationDialog?
**A:** SIM! Se você cancelar ou não tiver servidor configurado, o bot roda em modo standalone normalmente.

---

## 🎯 Resumo Executivo

**Você vê o diálogo com apenas a KEY** = **LicenseDialog** (obrigatório, sempre aparece)

**O diálogo com Login/Senha/Key** = **ActivationDialog** (opcional, só aparece com servidor)

**São dois sistemas independentes:**
1. **LicenseDialog** → Licença local (v3/v4)
2. **ActivationDialog** → Servidor multi-usuário (v5 - NOVO)

**Para usar o bot normalmente:**
- ✅ Preencha apenas o LicenseDialog
- ❌ Ignore o ActivationDialog (não vai aparecer se não tiver servidor)

**Para usar modo servidor:**
- ✅ Preencha ambos (LicenseDialog primeiro, depois ActivationDialog)
- ✅ Configure `server.url` no config.json
- ✅ Tenha servidor FastAPI rodando
