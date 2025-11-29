# 🔄 FLUXOGRAMA COMPLETO - AUTENTICAÇÃO E RECUPERAÇÃO

## 📊 FLUXO PRINCIPAL (Bot Inicializa)

```
┌────────────────────────────────────────────────────────────┐
│ USUÁRIO ABRE FishingMageBOT.exe                           │
└─────────────────────┬──────────────────────────────────────┘
                      ↓
                 main.py inicia
                      ↓
          ┌───────────────────────┐
          │ license_manager       │
          │ .check_license()      │
          └───────────┬───────────┘
                      ↓
          ┌───────────────────────┐
          │ Tem license.key       │
          │ salva?                │
          └───────┬───────┬───────┘
                  │       │
              SIM │       │ NÃO
                  ↓       ↓
         ┌────────────┐  ┌──────────────────┐
         │ VALIDAR    │  │ UnifiedAuthDialog│
         │ com        │  │ APARECE          │
         │ Keymaster  │  └────────┬─────────┘
         └─────┬──────┘           ↓
               ↓              (Ver Fluxo B)
   POST /validate (Keymaster)
               ↓
   ┌───────────┴────────────┐
   │                        │
 VÁLIDA                 INVÁLIDA
   ↓                        ↓
┌──────────────┐    ┌────────────────┐
│ Conectar ao  │    │ UnifiedAuth    │
│ servidor     │    │ Dialog APARECE │
│ direto       │    └────────┬───────┘
└──────┬───────┘             ↓
       ↓                 (Ver Fluxo B)
   ✅ BOT INICIA


─────────────────────────────────────────────────────────────

FLUXO B: UnifiedAuthDialog (Ativar ou Validar?)

┌────────────────────────────────────────────────────────────┐
│ UnifiedAuthDialog APARECE                                  │
└─────────────────────┬──────────────────────────────────────┘
                      ↓
          Usuário preenche:
          - Login (escolhe)
          - Senha (escolhe)
          - License Key (cola)
                      ↓
          Clica "Ativar"
                      ↓
    ┌─────────────────────────────┐
    │ DECISÃO INTELIGENTE:        │
    │ saved_key = load_license()  │
    │ license_key = input         │
    └─────────────┬───────────────┘
                  ↓
    ┌─────────────┴──────────────┐
    │                            │
saved_key == license_key    saved_key != license_key
    │                            │
    ↓                            ↓
┌─────────────────┐      ┌──────────────────┐
│ VALIDAR         │      │ ATIVAR           │
│ (já ativada)    │      │ (nova ou mudou)  │
└────────┬────────┘      └────────┬─────────┘
         ↓                        ↓
   validate_license()       activate_license()
         ↓                        ↓
   POST /validate           POST /activate
   (Keymaster)              (Keymaster)
         ↓                        ↓
   ┌─────┴──────┐          ┌──────┴──────┐
   │            │          │             │
 VÁLIDA     INVÁLIDA     ATIVA       REJEITA
   ↓            ↓          ↓             ↓
   │            │          │             │
   │     ┌──────┴──────────┴─────┐       │
   │     │ MOTIVOS DE REJEIÇÃO:  │       │
   │     │ - License expirada    │       │
   │     │ - HWID já vinculado   │       │
   │     │ - Key inválida        │       │
   │     └───────────────────────┘       │
   │                                     │
   └──────────┬──────────────────────────┘
              ↓
    ┌─────────┴──────────┐
    │ Conectar ao        │
    │ Servidor           │
    │ POST /auth/activate│
    └─────────┬──────────┘
              ↓
    Servidor valida NOVAMENTE
    com Keymaster
              ↓
    Cria/atualiza registro
    no banco (login + senha)
              ↓
    Retorna token
              ↓
    ✅ BOT CONECTADO!
```

---

## 🔑 RECUPERAÇÃO DE SENHA

### **CENÁRIO 1: Mesmo PC (Auto-Reset)**

```
┌────────────────────────────────────────────────────────────┐
│ USUÁRIO ESQUECEU SENHA (mesmo PC)                         │
└─────────────────────┬──────────────────────────────────────┘
                      ↓
          Cliente chama:
          POST /auth/reset-password
          {
            "license_key": "AAAA-BBBB",
            "hwid": "abc123...",
            "new_password": "nova123"
          }
                      ↓
    ┌─────────────────────────────┐
    │ SERVIDOR VALIDA:            │
    │ 1. License key com Keymaster│
    │ 2. HWID no banco            │
    └─────────────┬───────────────┘
                  ↓
    ┌─────────────┴──────────────┐
    │                            │
  HWID BATE                  HWID NÃO BATE
    ↓                            ↓
┌─────────────────┐      ┌──────────────────┐
│ UPDATE password │      │ ❌ BLOQUEADO     │
│ no banco        │      │ "HWID incorreto" │
└────────┬────────┘      │ Precisa admin!   │
         ↓               └──────────────────┘
   ✅ SENHA RESETADA!
```

### **CENÁRIO 2: Outro PC (Admin Reset)**

```
┌────────────────────────────────────────────────────────────┐
│ USUÁRIO MUDOU DE PC OU LICENSE EXPIRADA                   │
└─────────────────────┬──────────────────────────────────────┘
                      ↓
          Usuário contata Admin
                      ↓
          Admin acessa:
          https://server.com/admin
                      ↓
          Digita senha admin
                      ↓
          Busca usuário pela license key
                      ↓
          Clica "Reset Senha"
                      ↓
          POST /admin/api/reset-password
          (Header: admin_password)
          {
            "license_key": "AAAA-BBBB",
            "new_password": "nova123"
          }
                      ↓
    ┌─────────────────────────────┐
    │ SERVIDOR VALIDA:            │
    │ - Senha admin correta?      │
    │ - License existe no banco?  │
    └─────────────┬───────────────┘
                  ↓
          UPDATE password
          (SEM verificar HWID!)
                  ↓
          ✅ SENHA RESETADA!
                  ↓
          Admin envia nova senha
          para o usuário
```

---

## 🚨 CENÁRIOS DE ERRO

### **ERRO 1: License Expirada**

```
Bot inicia → validate_license()
    ↓
POST /validate (Keymaster)
    ↓
Keymaster: ❌ "License expirou em 2024-12-31"
    ↓
UnifiedAuthDialog APARECE
    ↓
Mensagem: "Sua license expirou. Cole uma nova license key."
    ↓
Usuário cola NOVA key (DIFERENTE)
    ↓
activate_license()
    ↓
POST /activate
    ↓
✅ Nova license ativada!
```

---

### **ERRO 2: Tentativa de Uso em Outro PC**

```
Usuário tenta usar no PC-2
    ↓
Bot inicia → validate_license()
    ↓
POST /validate (Keymaster)
    ↓
Keymaster: ❌ "HWID não corresponde"
    ↓
UnifiedAuthDialog APARECE
    ↓
Usuário cola MESMA key
    ↓
activate_license()
    ↓
POST /activate
    ↓
Keymaster vê: Já ativada para HWID-1
HWID-2 != HWID-1
    ↓
❌ "License já vinculada a outro PC"
    ↓
Opções:
1. Comprar nova license
2. Pedir ao admin para resetar HWID
```

---

### **ERRO 3: Reset de Senha em PC Diferente**

```
Usuário esqueceu senha e está em PC diferente
    ↓
POST /auth/reset-password
{
  "license_key": "AAAA-BBBB",
  "hwid": "xyz789...",  ← HWID diferente
  "new_password": "nova123"
}
    ↓
Servidor consulta banco:
SELECT hwid FROM hwid_bindings WHERE license_key = 'AAAA-BBBB'
    ↓
HWID salvo: "abc123..."
HWID recebido: "xyz789..."
    ↓
❌ HWID NÃO CORRESPONDE!
    ↓
Retorna HTTP 403:
"HWID não corresponde! Este não é o PC vinculado."
    ↓
Usuário precisa:
1. Ir ao PC original
2. OU pedir ao admin
```

---

## 📊 TABELA RESUMO

### **Quando UnifiedAuthDialog APARECE:**

| Situação | Motivo | Ação do Dialog |
|----------|--------|----------------|
| Primeira vez no bot | Sem license.key salva | ATIVAR nova key |
| License expirada | validate() falhou | ATIVAR nova key (diferente) |
| HWID incorreto | validate() falhou | Tentar ATIVAR → Bloqueado |
| Conexão falhou | Erro ao conectar servidor | VALIDAR ou ATIVAR |

### **Quando Auto-Reset FUNCIONA:**

| Requisito | Status | Observação |
|-----------|--------|------------|
| License válida no Keymaster | ✅ SIM | Não pode estar expirada |
| HWID corresponde | ✅ SIM | Mesmo PC onde ativou |
| Nova senha (min 6 chars) | ✅ SIM | - |

### **Quando Precisa Admin:**

| Situação | Auto-Reset | Admin Reset |
|----------|------------|-------------|
| Mesmo PC, license válida | ✅ | ✅ |
| Outro PC | ❌ | ✅ |
| License expirada | ❌ | ✅ |
| Perdeu acesso ao PC original | ❌ | ✅ |

---

## ✅ CONFIRMAÇÕES

### **Sua pergunta:**
> "Se a key não validar no Keymaster por estar vencida ou em outro HWID, ela vai abrir o AuthDialog correto para ativação da nova key, confere?"

### **RESPOSTA: ✅ SIM! EXATAMENTE!**

**Fluxo completo:**
```
1. Bot inicia
2. validate_license() chama Keymaster
3. Keymaster retorna: ❌ INVÁLIDA (expirada OU HWID errado)
4. ✅ UnifiedAuthDialog APARECE
5. Usuário cola nova key (diferente)
6. saved_key != new_key
7. ✅ Chama activate_license()
8. POST /activate no Keymaster
9. ✅ Nova license ativada!
```

**Se HWID errado:**
```
1-4. (igual acima)
5. Usuário cola MESMA key
6. Dialog tenta activate_license()
7. POST /activate
8. Keymaster: ❌ "Já ativada para outro HWID"
9. ❌ BLOQUEADO - Precisa comprar nova license
```

---

## 🎯 CONCLUSÃO FINAL

✅ **Sistema 100% funcional com:**
- Auto-reset no mesmo PC (HWID + Keymaster)
- Bloqueio em outro PC (precisa admin)
- Dialog inteligente (ativa OU valida conforme necessário)
- Renovação automática (detecta key diferente)
- Anti-compartilhamento (HWID binding)

**Nenhuma mudança necessária!** 🎉
