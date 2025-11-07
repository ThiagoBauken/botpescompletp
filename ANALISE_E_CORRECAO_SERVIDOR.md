# 🔍 Análise Técnica: Erros do Servidor e Soluções

## 📋 Resumo Executivo

Identificados **2 problemas distintos** no servidor:

1. **⚠️ DeprecationWarnings do FastAPI** (linhas 1202 e 1211 do server.py)
   - **Severidade:** Baixa (apenas warnings, não impede funcionamento)
   - **Causa:** Uso de `@app.on_event()` deprecado
   - **Solução:** Migrar para `lifespan` handlers

2. **❌ Erro HTTP 400 na autenticação**
   - **Severidade:** Alta (impede conexão ao servidor)
   - **Causa:** Endpoint `/auth/activate` retornando Bad Request
   - **Solução:** Requer investigação no código do servidor

---

## 🐛 Problema 1: DeprecationWarnings do FastAPI

### 📝 Descrição do Erro

```
/app/server.py:1202: DeprecationWarning:
    on_event is deprecated, use lifespan event handlers instead.
@app.on_event("startup")

/app/server.py:1211: DeprecationWarning:
    on_event is deprecated, use lifespan event handlers instead.
@app.on_event("shutdown")
```

### 🔎 Causa

O FastAPI versões 0.93.0+ deprecou `@app.on_event()` em favor do pattern `lifespan` para melhor controle de ciclo de vida.

### ✅ Solução

**ANTES (código atual com warnings):**
```python
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Código de inicialização
    print("🚀 Servidor iniciando...")
    # Conectar ao banco de dados
    # Inicializar cache
    # Etc.

@app.on_event("shutdown")
async def shutdown_event():
    # Código de limpeza
    print("🛑 Servidor encerrando...")
    # Fechar conexões
    # Salvar estado
    # Etc.
```

**DEPOIS (código corrigido sem warnings):**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP ===
    print("🚀 Servidor iniciando...")
    # Conectar ao banco de dados
    # Inicializar cache
    # Etc.

    yield  # Servidor roda aqui

    # === SHUTDOWN ===
    print("🛑 Servidor encerrando...")
    # Fechar conexões
    # Salvar estado
    # Etc.

app = FastAPI(lifespan=lifespan)
```

### 📝 Instruções de Aplicação

1. **Localizar o código atual** (linhas ~1202 e ~1211 do server.py):
   ```python
   @app.on_event("startup")
   async def startup_event():
       # ... código ...

   @app.on_event("shutdown")
   async def shutdown_event():
       # ... código ...
   ```

2. **Importar asynccontextmanager** (adicionar no topo do arquivo):
   ```python
   from contextlib import asynccontextmanager
   ```

3. **Criar função lifespan** (substituir os decoradores):
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Copiar código do startup_event() aqui

       yield

       # Copiar código do shutdown_event() aqui
   ```

4. **Modificar criação do FastAPI** (onde `app = FastAPI()` está):
   ```python
   app = FastAPI(lifespan=lifespan)
   ```

5. **Remover decoradores antigos** (deletar as funções com `@app.on_event`)

### 📚 Referências

- [FastAPI Lifespan Events Documentation](https://fastapi.tiangolo.com/advanced/events/)
- [Migration Guide](https://fastapi.tiangolo.com/release-notes/#0930)

---

## 🚨 Problema 2: Erro HTTP 400 na Autenticação

### 📝 Descrição do Erro

```
🌐 Conectando ao servidor multi-usuário...
   URL: https://private-serverpesca.pbzgje.easypanel.host
   Login: thiago
   🔑 HWID: 26ac9cc77f1aa50a...
   💻 PC: DESKTOP-6HL0A7T
   🔐 Autenticando (servidor valida com Keymaster)...
   ❌ Falha na ativação: Erro na validação (HTTP 400)
```

### 🔎 Análise do Cliente

**Arquivo:** `client/server_connector.py:194-206`

O cliente está enviando corretamente:
```python
payload = {
    "login": "thiago",
    "password": "<senha>",
    "license_key": "MAMZ-LQCC-...",
    "hwid": "26ac9cc77f1aa50a0f5b0582c7f0f84a",
    "pc_name": "DESKTOP-6HL0A7T"
}

response = requests.post(
    "https://private-serverpesca.pbzgje.easypanel.host/auth/activate",
    json=payload,
    timeout=10
)
```

### 🤔 Possíveis Causas do HTTP 400

HTTP 400 (Bad Request) indica que o servidor recebeu a requisição mas não conseguiu processá-la. Possíveis razões:

#### 1. **Endpoint não implementado ou URL incorreta**
   - Servidor pode não ter o endpoint `/auth/activate`
   - Rota pode ter mudado para `/api/auth/activate` ou similar

#### 2. **Validação de campos falhando**
   - Servidor esperando campos adicionais
   - Campos em formato incorreto
   - Campos obrigatórios faltando

#### 3. **Problema na validação do Keymaster**
   - Servidor chamando Keymaster mas recebendo erro
   - Keymaster offline ou inacessível
   - License key inválida ou expirada

#### 4. **Problema de CORS ou headers**
   - Faltando header `Content-Type: application/json`
   - Problema de CORS no servidor

#### 5. **Versão incompatível da API**
   - Cliente usando versão antiga da API
   - Servidor atualizado mas cliente não

### 🔍 Como Investigar

Criamos um **script de debug** para você identificar o problema exato:

**Arquivo:** `debug_server_connection.py` (criar na raiz do projeto)

```python
#!/usr/bin/env python3
"""
🔍 Debug: Testar conexão com servidor e identificar problema HTTP 400
"""

import requests
import json
import sys
import os
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_connection():
    """Testar conexão com servidor e endpoints"""

    server_url = "https://private-serverpesca.pbzgje.easypanel.host"

    print("\n" + "="*60)
    print("🔍 DEBUG: Testando conexão com servidor")
    print("="*60)

    # 1. Testar se servidor está acessível
    print("\n1️⃣ Testando conectividade básica...")
    try:
        response = requests.get(server_url, timeout=5)
        print(f"   ✅ Servidor acessível (HTTP {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Servidor inacessível (Connection Error)")
        return
    except requests.exceptions.Timeout:
        print(f"   ❌ Servidor não respondeu (Timeout)")
        return

    # 2. Testar endpoint de health
    print("\n2️⃣ Testando endpoint /health...")
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        print(f"   HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Health check OK: {response.json()}")
        else:
            print(f"   ⚠️ Health check retornou: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 3. Testar endpoint /auth/activate
    print("\n3️⃣ Testando endpoint /auth/activate...")

    # Carregar credenciais reais
    try:
        from client.credential_manager import CredentialManager
        from utils.license_manager import LicenseManager

        cred_mgr = CredentialManager()
        credentials = cred_mgr.load_credentials()

        license_mgr = LicenseManager()
        hwid = license_mgr.get_hardware_id()

        if not credentials:
            print("   ⚠️ Credenciais não encontradas, usando valores de teste")
            login = "test@test.com"
            password = "test123"
            license_key = "TEST-KEY-1234"
        else:
            login = credentials['login']
            password = credentials['password']
            license_key = credentials['license_key']

        import platform
        pc_name = platform.node()

    except Exception as e:
        print(f"   ⚠️ Erro ao carregar credenciais: {e}")
        print("   Usando valores de teste...")
        login = "test@test.com"
        password = "test123"
        license_key = "TEST-KEY-1234"
        hwid = "test-hwid-123"
        pc_name = "TEST-PC"

    payload = {
        "login": login,
        "password": password,
        "license_key": license_key,
        "hwid": hwid,
        "pc_name": pc_name
    }

    print(f"\n   📤 Enviando payload:")
    print(f"      login: {login}")
    print(f"      password: {'*' * len(password)}")
    print(f"      license_key: {license_key[:10]}...")
    print(f"      hwid: {hwid[:16]}...")
    print(f"      pc_name: {pc_name}")

    try:
        response = requests.post(
            f"{server_url}/auth/activate",
            json=payload,
            timeout=10
        )

        print(f"\n   📥 Resposta do servidor:")
        print(f"      HTTP Status: {response.status_code}")
        print(f"      Headers: {dict(response.headers)}")

        # Tentar parsear JSON
        try:
            data = response.json()
            print(f"\n      Response Body (JSON):")
            print(json.dumps(data, indent=6))

            # Análise da resposta
            if response.status_code == 200:
                print("\n   ✅ SUCESSO! Autenticação funcionou")
                print(f"      Token: {data.get('token', 'N/A')[:20]}...")
            elif response.status_code == 400:
                print("\n   ❌ HTTP 400 - Bad Request")
                print(f"      Mensagem: {data.get('message', 'N/A')}")
                print(f"      Detalhes: {data.get('detail', 'N/A')}")

                # Sugestões de correção
                print("\n   💡 Possíveis causas:")
                if 'message' in data:
                    msg = data['message'].lower()
                    if 'license' in msg or 'key' in msg:
                        print("      • License key inválida ou expirada")
                        print("      • Verificar no Keymaster se a chave está ativa")
                    elif 'hwid' in msg:
                        print("      • HWID binding - licença vinculada a outro PC")
                        print("      • Desvincular no Keymaster ou usar PC original")
                    elif 'field' in msg or 'required' in msg:
                        print("      • Campos obrigatórios faltando no payload")
                        print("      • Servidor esperando formato diferente")
                else:
                    print("      • Validação de campos falhando")
                    print("      • Keymaster offline ou inacessível")
                    print("      • Versão incompatível da API")

        except json.JSONDecodeError:
            print(f"\n      Response Body (Text):")
            print(f"      {response.text[:500]}")
            print("\n   ⚠️ Resposta não é JSON válido")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Não foi possível conectar ao endpoint")
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout ao conectar (10s)")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

    # 4. Testar alternativas de endpoint
    print("\n4️⃣ Testando endpoints alternativos...")
    alternative_endpoints = [
        "/api/auth/activate",
        "/auth/login",
        "/api/auth/login",
        "/activate"
    ]

    for endpoint in alternative_endpoints:
        try:
            response = requests.post(
                f"{server_url}{endpoint}",
                json=payload,
                timeout=3
            )
            if response.status_code != 404:
                print(f"   ✅ {endpoint} existe (HTTP {response.status_code})")
        except:
            pass

    print("\n" + "="*60)
    print("🏁 Teste concluído")
    print("="*60)

if __name__ == "__main__":
    test_server_connection()
```

### 📋 Instruções de Uso do Script de Debug

1. **Salvar o script** como `debug_server_connection.py` na raiz do projeto

2. **Executar o script**:
   ```bash
   python debug_server_connection.py
   ```

3. **Analisar a saída** para identificar o problema exato:
   - HTTP 404 → Endpoint não existe (verificar rota)
   - HTTP 400 com mensagem → Ver mensagem de erro específica
   - HTTP 500 → Erro interno do servidor
   - Connection Error → Servidor offline

4. **Compartilhar a saída completa** se precisar de mais ajuda

---

## 🛠️ Soluções Possíveis para HTTP 400

### Solução 1: Verificar Logs do Servidor

**No servidor (via SSH ou painel):**
```bash
# Ver logs em tempo real
docker logs -f <container-name>

# Ou no Easypanel: Services → Seu serviço → Logs
```

**Procurar por:**
- Mensagens de erro relacionadas a `/auth/activate`
- Erros de validação de campos
- Erros do Keymaster
- Stack traces

### Solução 2: Verificar Implementação do Endpoint

**Arquivo esperado:** `server/server.py` (linha ~335)

```python
@app.post("/auth/activate")
async def activate_user(request: ActivationRequest):
    """
    Endpoint de ativação com validação Keymaster
    """
    try:
        # Validar com Keymaster
        keymaster_result = validate_with_keymaster(
            request.license_key,
            request.hwid
        )

        if not keymaster_result["valid"]:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": keymaster_result["message"]
                }
            )

        # ... resto do código ...

    except Exception as e:
        logger.error(f"Erro em /auth/activate: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Erro na validação: {str(e)}"
            }
        )
```

**Verificar:**
- ✅ Endpoint existe e está acessível
- ✅ `ActivationRequest` model tem todos os campos corretos
- ✅ `validate_with_keymaster()` função está funcionando
- ✅ Tratamento de erros está retornando mensagens úteis

### Solução 3: Adicionar Logging Detalhado

**No servidor, adicionar logs antes da validação:**

```python
@app.post("/auth/activate")
async def activate_user(request: ActivationRequest):
    # 🔍 LOG: Adicionar debug
    logger.info(f"📥 Recebido /auth/activate:")
    logger.info(f"   Login: {request.login}")
    logger.info(f"   License: {request.license_key[:10]}...")
    logger.info(f"   HWID: {request.hwid[:16]}...")
    logger.info(f"   PC: {request.pc_name}")

    try:
        # Validar com Keymaster
        logger.info("🔍 Validando com Keymaster...")
        keymaster_result = validate_with_keymaster(...)
        logger.info(f"📤 Keymaster response: {keymaster_result}")

        # ... resto ...
```

### Solução 4: Verificar Keymaster

**Testar diretamente a API do Keymaster:**

```bash
curl -X POST https://private-keygen.pbzgje.easypanel.host/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "MAMZ-LQCC-...",
    "hwid": "26ac9cc77f1aa50a0f5b0582c7f0f84a"
  }'
```

**Verificar:**
- ✅ Keymaster está acessível
- ✅ License key é válida
- ✅ HWID está permitido
- ✅ Resposta é `{"valid": true, ...}`

---

## 📝 Checklist de Correção

### Para o DeprecationWarning (FastAPI):

- [ ] Backup do `server.py` original
- [ ] Adicionar `from contextlib import asynccontextmanager`
- [ ] Criar função `lifespan(app: FastAPI)`
- [ ] Mover código de `startup_event()` para antes do `yield`
- [ ] Mover código de `shutdown_event()` para depois do `yield`
- [ ] Modificar `app = FastAPI(lifespan=lifespan)`
- [ ] Remover decoradores `@app.on_event()`
- [ ] Testar servidor reiniciando
- [ ] Verificar que warnings não aparecem mais

### Para o Erro HTTP 400:

- [ ] Executar `debug_server_connection.py`
- [ ] Verificar logs do servidor
- [ ] Confirmar que endpoint `/auth/activate` existe
- [ ] Verificar que Keymaster está acessível
- [ ] Verificar que license key é válida no Keymaster
- [ ] Verificar que HWID não está bloqueado
- [ ] Adicionar logs detalhados no servidor
- [ ] Testar novamente após correções

---

## 🆘 Suporte Adicional

Se após seguir este guia o problema persistir:

1. **Execute o script de debug** e salve a saída completa
2. **Colete os logs do servidor** (últimas 50 linhas)
3. **Verifique status do Keymaster** (se está online)
4. **Compartilhe:**
   - Saída do `debug_server_connection.py`
   - Logs do servidor (sem dados sensíveis)
   - Versão do FastAPI no servidor
   - Versão do Python no servidor

---

**Criado em:** 2025-11-07
**Versão:** 1.0
**Projeto:** Ultimate Fishing Bot v5.0
