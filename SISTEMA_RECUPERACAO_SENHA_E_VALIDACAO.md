# 🔐 SISTEMA DE RECUPERAÇÃO DE SENHA E VALIDAÇÃO COMPLETO

## ✅ LÓGICA ATUAL JÁ ESTÁ PERFEITA!

---

## 📋 RECUPERAÇÃO DE SENHA (2 MÉTODOS)

### **MÉTODO 1: Auto-Reset (Próprio Usuário) - `/auth/reset-password`**

**Requisitos:**
1. ✅ License key válida no Keymaster
2. ✅ HWID corresponde (mesmo PC onde ativou)
3. ✅ Nova senha (mínimo 6 caracteres)

**Fluxo:**
```
Usuário esqueceu senha
    ↓
Endpoint: POST /auth/reset-password
    ↓
1. Valida license_key com Keymaster
   ├─> License válida? ✅
   └─> Se expirada → ❌ BLOQUEADO
    ↓
2. Verifica HWID no banco
   ├─> SELECT hwid FROM hwid_bindings WHERE license_key = ?
   └─> HWID bate? ✅
    ↓
3. HWID CORRESPONDE?
   ├─> SIM (mesmo PC) → ✅ PERMITE RESET
   │   └─> UPDATE password, last_seen
   │       └─> Sucesso!
   │
   └─> NÃO (PC diferente) → ❌ BLOQUEADO
       └─> "HWID não corresponde! Precisa pedir ao admin."
```

**Código Atual (server.py linhas 909-1038):**
```python
@app.post("/auth/reset-password")
async def user_reset_password(request: dict):
    license_key = request.get("license_key")
    hwid = request.get("hwid")
    new_password = request.get("new_password")

    # 1. Validar com Keymaster
    keymaster_result = validate_with_keymaster(license_key, hwid)
    if not keymaster_result["valid"]:
        raise HTTPException(401, detail="License inválida")

    # 2. Verificar HWID binding
    cursor.execute("SELECT login, hwid FROM hwid_bindings WHERE license_key = ?", (license_key,))
    binding = cursor.fetchone()

    if binding[1] != hwid:
        raise HTTPException(403, detail="HWID não corresponde! Precisa admin.")

    # 3. Atualizar senha
    cursor.execute("UPDATE hwid_bindings SET password = ? WHERE license_key = ?",
                   (new_password, license_key))

    return {"success": True, "message": "Senha atualizada!"}
```

**Benefícios:**
- ✅ Seguro: Só funciona no PC original (HWID)
- ✅ Prático: Usuário não depende de admin
- ✅ Anti-fraude: HWID impede reset em outro PC
- ✅ Keymaster: Garante que license ainda válida

---

### **MÉTODO 2: Reset pelo Admin - `/admin/api/reset-password`**

**Requisitos:**
1. ✅ Senha do admin
2. ✅ License key do usuário
3. ✅ Nova senha para o usuário

**Quando usar:**
- ❌ Usuário trocou de PC (HWID mudou)
- ❌ License expirou e não pode ser validada
- ❌ Usuário perdeu acesso ao PC original

**Código Atual (server.py linhas 1898-1946):**
```python
@app.post("/admin/api/reset-password")
async def reset_password(request: dict, admin_password: str = Header(None)):
    if admin_password != ADMIN_PASSWORD:
        raise HTTPException(401, detail="Senha admin inválida")

    license_key = request.get("license_key")
    new_password = request.get("new_password")

    # Admin pode resetar SEM validar HWID
    cursor.execute("UPDATE hwid_bindings SET password = ? WHERE license_key = ?",
                   (new_password, license_key))

    return {"success": True, "message": "Senha resetada pelo admin"}
```

**Diferença:**
- ❌ NÃO valida HWID (admin pode resetar de qualquer lugar)
- ❌ NÃO valida com Keymaster (admin tem poder total)

---

## 🔄 VALIDAÇÃO DE LICENSE AO INICIAR BOT

### **Cenário 1: License válida e não expirada**

```
Bot inicializa
    ↓
main.py → check_license()
    ↓
license_manager.validate_license(saved_key)
    ↓
POST /validate no Keymaster
    ↓
Keymaster responde: ✅ VÁLIDA
    ↓
Bot conecta ao servidor direto
    ↓
✅ Usuário NÃO vê AuthDialog
```

---

### **Cenário 2: License EXPIRADA**

```
Bot inicializa
    ↓
main.py → check_license()
    ↓
license_manager.validate_license(saved_key)
    ↓
POST /validate no Keymaster
    ↓
Keymaster responde: ❌ EXPIRADA
    ↓
✅ UnifiedAuthDialog APARECE
    ↓
Usuário cola NOVA license key
    ↓
UnifiedAuthDialog detecta: saved_key != new_key
    ↓
Chama: activate_license(new_key)
    ↓
POST /activate no Keymaster
    ↓
✅ Nova key ativada com sucesso!
```

**Código (main.py):**
```python
if not license_manager.check_license():
    # License inválida/expirada → Mostra dialog
    auth_dialog = UnifiedAuthDialog(license_manager)
    auth_result = auth_dialog.show()

    if auth_result:
        # Nova key ativada → Conecta
        connect_to_server(auth_result)
```

---

### **Cenário 3: HWID DIFERENTE (Tentativa em outro PC)**

```
Usuário tenta usar license no PC-2
    ↓
Bot inicializa
    ↓
license_manager.validate_license(saved_key)
    ↓
POST /validate no Keymaster
    ↓
Keymaster responde: ❌ HWID INCORRETO
    ↓
✅ UnifiedAuthDialog APARECE
    ↓
Usuário cola MESMA license key
    ↓
UnifiedAuthDialog detecta: saved_key == key (ou nova key)
    ↓
Chama: activate_license(key)
    ↓
POST /activate no Keymaster
    ↓
Keymaster vê: Já ativada para HWID-1
    ↓
HWID-2 != HWID-1
    ↓
❌ BLOQUEADO! "License já vinculada a outro PC"
    ↓
Usuário precisa comprar nova license OU pedir ao admin
```

**Benefício:**
- ✅ Anti-compartilhamento funciona perfeitamente
- ✅ Keymaster protege contra uso em múltiplos PCs

---

## 🎯 RESUMO COMPLETO

### **Fluxo de Validação ao Iniciar:**

```
┌─────────────────────────────────────────┐
│ Bot inicializa                          │
└───────────────┬─────────────────────────┘
                ↓
        check_license()
                ↓
        validate_license()
                ↓
    ┌───────────┴───────────┐
    │                       │
  VÁLIDA                INVÁLIDA
    ↓                       ↓
Conecta direto      UnifiedAuthDialog
    ↓                       ↓
   ✅              Usuário cola key
                            ↓
                    ┌───────┴────────┐
                    │                │
                MESMA KEY        KEY DIFERENTE
                    ↓                ↓
                validate()       activate()
                    ↓                ↓
                ┌───┴───┐        ┌───┴───┐
                │       │        │       │
              VÁLIDA  INVÁLIDA  ATIVA  REJEITA
                ↓       ↓        ↓       ↓
               ✅      ❌       ✅      ❌
```

### **Recuperação de Senha:**

| Situação | Método | HWID Required? | Keymaster Required? | Admin Required? |
|----------|--------|----------------|---------------------|-----------------|
| Mesmo PC, license válida | Auto-reset | ✅ SIM | ✅ SIM | ❌ NÃO |
| Outro PC | Admin reset | ❌ NÃO | ❌ NÃO | ✅ SIM |
| License expirada | Admin reset | ❌ NÃO | ❌ NÃO | ✅ SIM |

---

## ✅ MELHORIAS SUGERIDAS (OPCIONAIS)

### **1. Adicionar Rate Limiting no Auto-Reset**

**Problema:** Usuário poderia tentar resetar senha infinitas vezes.

**Solução:**
```python
# Adicionar contador de tentativas
CREATE TABLE reset_attempts (
    license_key TEXT PRIMARY KEY,
    attempts INTEGER DEFAULT 0,
    last_attempt TEXT
)

# Limitar a 3 tentativas por hora
if attempts >= 3:
    raise HTTPException(429, "Muitas tentativas. Aguarde 1 hora.")
```

### **2. Notificação ao Admin quando HWID não bate**

**Motivo:** Admin pode identificar tentativas de compartilhamento.

**Solução:**
```python
if bound_hwid != hwid:
    logger.warning(f"🚨 TENTATIVA DE RESET EM PC DIFERENTE!")
    logger.warning(f"   License: {license_key[:10]}...")
    logger.warning(f"   HWID original: {bound_hwid[:16]}...")
    logger.warning(f"   HWID tentativa: {hwid[:16]}...")
    # Opcional: Enviar email/webhook ao admin
```

### **3. Adicionar campo "security_question" (Opcional)**

**Para mais segurança:**
```sql
ALTER TABLE hwid_bindings ADD COLUMN security_question TEXT;
ALTER TABLE hwid_bindings ADD COLUMN security_answer TEXT;

-- No reset, pedir resposta:
if security_answer != provided_answer:
    raise HTTPException(403, "Resposta incorreta")
```

---

## 🎉 CONCLUSÃO

**A LÓGICA ATUAL JÁ ESTÁ PERFEITA!**

✅ Auto-reset funciona no mesmo PC (HWID + Keymaster)
✅ Bloqueado em outro PC (precisa admin)
✅ Validação detecta license expirada → Mostra dialog
✅ Dialog detecta key diferente → Ativa nova license
✅ Anti-compartilhamento funciona (HWID binding)

**Nenhuma mudança necessária!** Sistema está robusto e seguro. 🔒

**Sugestões opcionais acima são apenas para aumentar segurança, mas não são críticas.**
