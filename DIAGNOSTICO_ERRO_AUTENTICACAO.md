# 🔬 Diagnóstico: Erro de Autenticação HTTP 400

## 📋 Resumo do Problema

**Sintoma:** Cliente do usuário "thiago" não consegue conectar ao servidor com erro HTTP 400

**Causa Raiz:** License key `MAMZ-LQCC-...` está sendo **rejeitada pelo Keymaster**

---

## ✅ O Que ESTÁ Funcionando

Logs do servidor confirmam funcionamento correto:

```
INFO:server:🔍 Validando com Keymaster: OF5Y-ZPOI-...
INFO:server:✅ Keymaster: License válida!
INFO:server:✅ Keymaster validou: OF5Y-ZPOI-... (Plan: basic)
INFO:server:🔗 HWID vinculado pela primeira vez:
INFO:server:   License: OF5Y-ZPOI-...
INFO:server:   Login: BALINHA
INFO:server:   PC: DESKTOP-Q5GCMOD
INFO:server:   HWID: be10ce58a64d16ce...
INFO:server:✅ Ativação bem-sucedida: BALINHA
INFO:     10.11.0.61:33184 - "POST /auth/activate HTTP/1.1" 200 OK
```

**Conclusão:**
- ✅ Servidor online e funcional
- ✅ Endpoint `/auth/activate` funcionando
- ✅ Keymaster acessível e validando
- ✅ HWID binding funcionando
- ✅ License `OF5Y-ZPOI-...` (usuário BALINHA) → **VÁLIDA**

---

## ❌ O Que NÃO Está Funcionando

Cliente do usuário "thiago" falhando:

```
🌐 Conectando ao servidor multi-usuário...
   URL: https://private-serverpesca.pbzgje.easypanel.host
   Login: thiago
   🔑 HWID: 26ac9cc77f1aa50a...
   💻 PC: DESKTOP-6HL0A7T
   🔐 Autenticando (servidor valida com Keymaster)...
   ❌ Falha na ativação: Erro na validação (HTTP 400)
```

Script de debug revelou:

```json
{
  "success": false,
  "message": "Erro na validação (HTTP 400)",
  "token": null,
  "rules": null
}
```

**Conclusão:**
- ❌ License `MAMZ-LQCC-...` (usuário thiago) → **INVÁLIDA**
- ❌ Keymaster retornando HTTP 400
- ❌ Servidor propagando erro do Keymaster

---

## 🔍 Análise Detalhada

### Comparação de Usuários

| Aspecto | BALINHA (✅ Funcionou) | thiago (❌ Falhou) |
|---------|------------------------|-------------------|
| Login | BALINHA | thiago |
| PC | DESKTOP-Q5GCMOD | DESKTOP-6HL0A7T |
| HWID | be10ce58a64d16ce... | 26ac9cc77f1aa50a... |
| License | OF5Y-ZPOI-... | MAMZ-LQCC-... |
| Status | ✅ Keymaster validou | ❌ Keymaster rejeitou (HTTP 400) |
| Resultado | 200 OK + token | 400 Bad Request |

### Possíveis Causas do HTTP 400 do Keymaster

1. **License Inválida ou Expirada**
   - License `MAMZ-LQCC-...` pode estar expirada
   - License pode ter sido revogada
   - License pode ser inválida (não existe no sistema)

2. **HWID Vinculado a Outro PC**
   - License pode estar vinculada ao HWID `be10ce58a64d16ce...` (PC do BALINHA)
   - Tentativa de usar em `26ac9cc77f1aa50a...` (PC do thiago) está sendo bloqueada
   - Sistema de anti-compartilhamento ativo

3. **License Já em Uso**
   - License pode estar ativa em outra sessão
   - Limite de sessões simultâneas atingido

4. **Formato Incorreto**
   - License com formato incorreto
   - Caracteres especiais ou espaços

---

## 🛠️ Soluções

### Solução 1: Verificar License no Keymaster

**Acessar painel do Keymaster:**
```
URL: https://private-keygen.pbzgje.easypanel.host
```

**Verificar license `MAMZ-LQCC-...`:**
- Status: Ativa/Expirada/Revogada?
- Expira em: Data de expiração
- HWID vinculado: Qual PC está vinculado?
- Plano: Basic/Pro/Enterprise?

### Solução 2: Desvincular HWID

Se a license está vinculada a outro PC:

**Opção A: Via Painel do Keymaster**
1. Acessar painel admin
2. Buscar license `MAMZ-LQCC-...`
3. Clicar em "Desvincular HWID"
4. Tentar conectar novamente

**Opção B: Via API do Keymaster**
```bash
curl -X POST https://private-keygen.pbzgje.easypanel.host/unbind \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "MAMZ-LQCC-...",
    "admin_token": "seu-token-admin"
  }'
```

### Solução 3: Gerar Nova License

Se a license está expirada ou inválida:

1. Acessar painel do Keymaster
2. Gerar nova license para o usuário "thiago"
3. Atualizar credenciais no cliente:
   - Deletar `data/credentials.dat`
   - Reabrir bot e inserir nova license

### Solução 4: Verificar no Banco do Servidor

Se você tem acesso ao servidor, verificar o binding:

```python
# No servidor, verificar tabela hwid_bindings
import sqlite3

conn = sqlite3.connect('server.db')
cursor = conn.cursor()

# Verificar binding da license
cursor.execute("""
    SELECT license_key, hwid, pc_name, login, bound_at
    FROM hwid_bindings
    WHERE license_key = 'MAMZ-LQCC-...'
""")

binding = cursor.fetchone()
if binding:
    print(f"License vinculada a:")
    print(f"  HWID: {binding[1]}")
    print(f"  PC: {binding[2]}")
    print(f"  Login: {binding[3]}")
    print(f"  Data: {binding[4]}")
else:
    print("License não vinculada ainda")

conn.close()
```

---

## 🧪 Teste Rápido

Para confirmar o diagnóstico, teste **temporariamente** com a license que funciona:

```python
# No cliente, editar temporariamente data/credentials.dat
# Trocar MAMZ-LQCC-... por OF5Y-ZPOI-...
# (apenas para teste!)

# Se conectar com sucesso:
# → Confirma que problema é na license do thiago
# → Não é problema de código

# Se ainda falhar:
# → Problema pode ser de rede ou HWID
```

---

## 📋 Checklist de Resolução

- [ ] Acessar painel do Keymaster
- [ ] Verificar status da license `MAMZ-LQCC-...`
- [ ] Verificar se está expirada
- [ ] Verificar se está vinculada a outro PC
- [ ] Se vinculada: desvincular HWID
- [ ] Ou: gerar nova license para o usuário
- [ ] Atualizar credenciais no cliente
- [ ] Deletar `data/credentials.dat`
- [ ] Reabrir bot e inserir nova license
- [ ] Testar conexão novamente

---

## 💡 Prevenção Futura

### Para Evitar Esse Problema:

1. **Logs Mais Detalhados no Servidor**

   Modificar `server/server.py` para logar resposta completa do Keymaster:

   ```python
   @app.post("/auth/activate")
   async def activate_user(request: ActivationRequest):
       logger.info(f"📥 /auth/activate: {request.login}")

       # Validar com Keymaster
       keymaster_result = validate_with_keymaster(
           request.license_key,
           request.hwid
       )

       # ✅ ADICIONAR: Log detalhado
       logger.info(f"📤 Keymaster response completo:")
       logger.info(f"   Valid: {keymaster_result.get('valid')}")
       logger.info(f"   Message: {keymaster_result.get('message')}")
       logger.info(f"   Status: {keymaster_result.get('status')}")
       logger.info(f"   HTTP Code: {keymaster_result.get('http_code')}")

       if not keymaster_result["valid"]:
           # ✅ ADICIONAR: Retornar mensagem específica
           return ActivationResponse(
               success=False,
               message=f"Keymaster: {keymaster_result.get('message', 'Erro desconhecido')}"
           )
   ```

2. **Mensagens de Erro Mais Claras**

   Retornar mensagem específica ao cliente:
   - "License expirada em DD/MM/YYYY"
   - "License vinculada a outro PC (DESKTOP-XYZ)"
   - "License inválida (não encontrada)"

3. **Comando de Desvincular no Cliente**

   Adicionar botão na UI:
   ```
   [Desvincular HWID] → Chama API do servidor
   ```

---

## 🎯 Conclusão

**Problema:** License do usuário "thiago" (`MAMZ-LQCC-...`) está sendo **rejeitada pelo Keymaster**

**Não é problema de código**, mas sim de configuração da license no Keymaster.

**Ação Necessária:** Verificar e corrigir status da license no painel do Keymaster.

---

**Criado em:** 2025-11-07
**Versão:** 1.0
**Projeto:** Ultimate Fishing Bot v5.0
