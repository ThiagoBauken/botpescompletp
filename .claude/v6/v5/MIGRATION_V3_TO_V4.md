# 🔄 Migração v3 → v4: Sistema de Licença

## ✅ Lógica Implementada (100% compatível com v3)

### 📋 Fluxo de Validação

#### Bot v3 (`botpesca - Copia (12).py`)
```python
# Linha 10264 - check_license()
def check_license(self):
    saved_key = self.license_manager.load_license()

    if saved_key:
        valid, data = self.license_manager.validate(saved_key)  # ← VALIDATE
        if valid:
            self.licensed = True
            return

    # Solicitar nova licença
    dialog = LicenseDialog(self)
    license_key = dialog.show()

    if license_key:
        valid, data = self.license_manager.validate(license_key)  # ← VALIDATE
        if valid:
            self.licensed = True
```

#### Bot v4 (`fishing_bot_v4/main.py`)
```python
# Linha 52 - main()
if not license_manager.check_license():
    license_dialog = LicenseDialog(license_manager)
    license_key = license_dialog.show()

    if license_key:
        valid, data = license_manager.validate_license(license_key)  # ← VALIDATE
        if valid:
            print("✅ Licença ativada com sucesso!")
```

### 🔐 LicenseDialog

#### Bot v3 (`linha 6343`)
```python
def activate_license(self):
    key = self.key_entry.get().strip()
    # Tentar ativar
    success, message = self.bot.license_manager.activate(key)  # ← ACTIVATE

    if success:
        self.result = key
        self.dialog.after(1500, self.dialog.destroy)
```

#### Bot v4 (`ui/license_dialog.py linha 174`)
```python
def activate_license(self):
    license_key = self.key_entry.get().strip()
    # Tentar ativar (lógica do v3)
    success, message = self.license_manager.activate_license(license_key)  # ← ACTIVATE

    if success:
        self.result = license_key
        self.root.after(1500, self.root.destroy)
```

## 🔧 Métodos Implementados

### 1. `validate_license()` - v3 linha 1747

**v3**:
```python
def validate(self, key):
    response = requests.post(f"{ACTIVATION_SERVER}/validate", ...)

    if response.status_code == 200:
        result = response.json()
        is_valid = result.get('valid', False)
        return is_valid, result
    else:
        error_msg = f'Servidor retornou {response.status_code}: {response.text}'
        return False, {'message': error_msg}
```

**v4** (atualizado):
```python
def validate_license(self, key):
    response = requests.post(f"{self.server_url}/validate", ...)

    if response.status_code == 200:
        result = response.json()
        is_valid = result.get('valid', False)
        return is_valid, result
    else:
        error_msg = f'Servidor retornou {response.status_code}: {response.text}'
        return False, {'message': error_msg}
```

### 2. `activate_license()` - v3 linha 1680

**v3**:
```python
def activate(self, key):
    response = requests.post(f"{ACTIVATION_SERVER}/activate", ...)

    if response.status_code == 200:
        result = response.json()
        if result.get('valid', False):
            self.save_license(key)
            return True, "Ativação realizada com sucesso!"
        else:
            error_msg = result.get('message', 'Erro desconhecido')
            return False, error_msg
    elif response.status_code == 403:
        return False, "Chave inválida, expirada ou já usada"
    elif response.status_code == 400:
        return False, "Dados de ativação inválidos"
```

**v4** (atualizado):
```python
def activate_license(self, key):
    response = requests.post(f"{self.server_url}/activate", ...)

    if response.status_code == 200:
        result = response.json()
        if result.get('valid', False):
            self.save_license(key)
            return True, "Ativação realizada com sucesso!"
        else:
            error_msg = result.get('message', 'Erro desconhecido')
            return False, error_msg
    elif response.status_code == 403:
        return False, "Chave inválida, expirada ou já usada"
    elif response.status_code == 400:
        return False, "Dados de ativação inválidos"
```

## 📊 Comparação de Tratamento de Erros

| Cenário | v3 | v4 | Status |
|---------|----|----|--------|
| Status 200 + valid=true | ✅ Retorna True | ✅ Retorna True | ✅ IGUAL |
| Status 200 + valid=false | ❌ Retorna False com message | ❌ Retorna False com message | ✅ IGUAL |
| Status 400 | ❌ "Dados inválidos" | ❌ "Dados inválidos" | ✅ IGUAL |
| Status 403 | ❌ "Chave já usada" | ❌ "Chave já usada" | ✅ IGUAL |
| ConnectionError | ❌ "Erro de conexão" | ❌ "Erro de conexão" | ✅ IGUAL |
| Timeout | ❌ "Timeout" | ❌ "Timeout" | ✅ IGUAL |

## 🎯 Diferenças Corrigidas

### ❌ Antes (v4 inicial)
```python
# main.py - ERRADO
valid, data = license_manager.activate_license(license_key)
if not valid:
    valid, data = license_manager.validate_license(license_key)  # Fallback
```

### ✅ Depois (v4 atualizado)
```python
# main.py - CORRETO (igual v3)
if license_key:
    valid, data = license_manager.validate_license(license_key)
```

### Explicação
- **Dialog** chama `activate()` para salvar a chave no servidor
- **check_license** após dialog chama `validate()` para confirmar
- Não há fallback - cada método tem seu propósito específico

## 🧪 Testes de Validação

### Teste 1: Chave Salva
```bash
cd fishing_bot_v4
python -c "
from utils.license_manager import LicenseManager
lm = LicenseManager()
key = lm.load_license()
valid, data = lm.validate_license(key)
print('Resultado:', 'VALIDA' if valid else 'INVALIDA')
"
```

### Teste 2: Nova Ativação
```bash
cd fishing_bot_v4
python test_new_license.py PROD-XXXX-YYYY-ZZZZ
```

### Teste 3: Fluxo Completo
```bash
cd fishing_bot_v4
python main.py
```

## 📝 Mensagens de Log

### v3
```
🔐 Verificando licença...
🔑 Licença encontrada, validando...
🔍 Validando chave: O9QY229LF0...
📥 Status Code: 200
✅ Validação: Válida
📅 Expira em: 2025-10-28T14:30:23.452Z
📊 Status: active
```

### v4 (atualizado - IDÊNTICO)
```
🔐 Verificando licença...
🔑 Licença encontrada, validando...
🔍 Validando chave: O9QY229LF0...
📥 Status Code: 200
✅ Validação: Válida
📅 Expira em: 2025-10-28T14:30:23.452Z
📊 Status: active
```

## ✅ Checklist de Migração

- [x] `validate_license()` retorna exatamente como v3
- [x] `activate_license()` retorna exatamente como v3
- [x] Tratamento de erros HTTP idêntico (400, 403, 200)
- [x] Mensagens de log compatíveis
- [x] Exceções tratadas igualmente (ConnectionError, Timeout)
- [x] LicenseDialog chama `activate()` (não validate)
- [x] main.py chama `validate()` após dialog
- [x] `_safe_print()` em todos os prints com emoji
- [x] User-Agent atualizado para v4.0
- [x] Timeout de 15 segundos mantido

## 🎉 Resultado

**O sistema de licença v4 está 100% compatível com a lógica funcional do v3!**

Todas as mudanças foram implementadas para seguir **exatamente** o mesmo fluxo:
1. `check_license()` → `validate()` para chaves salvas
2. `LicenseDialog` → `activate()` para chaves novas
3. `main.py` após dialog → `validate()` para confirmar

Status: ✅ **CONCLUÍDO**
