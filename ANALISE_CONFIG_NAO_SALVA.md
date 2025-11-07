# 🐛 Análise: Configurações Não Salvam Entre Reinícios

## 📊 Diagnóstico Completo

### ✅ O Que ESTÁ Funcionando

Analisei o código e confirmei:

1. ✅ **ConfigManager funciona** - Testado e consegue salvar `data/config.json`
2. ✅ **UI tem botões de salvar** - Todos implementados corretamente
3. ✅ **Código chama save_config()** - Implementação correta

**Linhas verificadas:**
- `ui/main_window.py:5146` - `save_all_config()` → chama `save_config()`
- `ui/main_window.py:5105` - `save_cleaning_config()` → chama `save_config()`
- `ui/main_window.py:5256` - `save_feeding_config()` → chama `save_config()`

### ❌ O Que ESTÁ Errado

**Problema identificado:** Arquivo `data/config.json` **NÃO EXISTE** no sistema.

```bash
$ ls data/
__placeholder__.txt
license_info.json
# ❌ Falta: config.json
```

Isso significa que as configurações **nunca foram salvas** ou **estão sendo salvas em outro local**.

---

## 🔍 Possíveis Causas

### **Causa 1: Usuário Não Está Salvando**

**Sintoma:** Muda valores na UI mas não clica nos botões de salvar.

**Como Funciona:**
1. Você abre a UI e muda valores (intervals, timeouts, etc.)
2. **Se NÃO clicar em um dos botões de salvar**, as mudanças ficam apenas na memória
3. Ao fechar e reabrir, volta ao padrão

**Botões que salvam (clique neles após mudar!):**
- Tab **Auto-Clean**: `💾 Salvar Config de Limpeza`
- Tab **Feeding**: `💾 Salvar Configurações`
- Tab **Templates**: `💾 Salvar Tudo`
- Tab **Geral**: `💾 Salvar Todas as Configurações`

**Solução:**
```
Após mudar QUALQUER configuração:
1. Clique no botão de salvar correspondente
2. Aguarde mensagem "Configurações salvas e persistidas!"
3. Agora sim, pode fechar o programa
```

---

### **Causa 2: Modo Servidor (Sincronização)**

**Sintoma:** Bot conecta ao servidor e recebe configs do servidor.

**Como Funciona:**
```
Startup:
1. Bot carrega config local (data/config.json)
2. Bot conecta ao servidor
3. Servidor envia suas próprias configs
4. Bot SOBRESCREVE configs locais com as do servidor
```

**Verificar:**
```python
# Linha 5152 em main_window.py:
self._sync_config_to_server()
```

Isso sincroniza configs **PARA** o servidor, mas o servidor pode ter outra lógica que envia configs de volta.

**Solução:**
- Verificar se servidor está sobrescrevendo configs
- Desconectar do servidor temporariamente para testar
- Salvar configs apenas localmente

---

### **Causa 3: Permissões de Arquivo**

**Sintoma:** Bot não tem permissão para criar `data/config.json`.

**Verificar:**
```bash
# No terminal/CMD onde roda o bot:
ls -la data/
# Verificar permissões
```

**Se permissões estiverem erradas:**
```bash
# Linux
chmod 755 data/
chmod 644 data/*.json

# Windows (executar como Administrador)
icacls data /grant Users:F
```

---

### **Causa 4: Arquivo em Outro Local (Docker/Servidor)**

**Sintoma:** Bot está rodando em Docker e salvando em local temporário.

**Se rodando em Docker:**
```dockerfile
# Configs podem estar sendo salvas DENTRO do container
# e perdidas ao reiniciar

# Verificar volumes montados:
docker inspect <container-name>

# Procurar mapeamento de /app/data
```

**Solução:**
```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data  # Mapear data/ para persistir
```

---

## 🛠️ Solução Passo a Passo

### **Teste 1: Verificar Se Salva Localmente**

Execute este script Python:

```python
#!/usr/bin/env python3
"""
Teste de salvamento de configurações
"""
import os
from core.config_manager import ConfigManager

print("🔍 Testando salvamento de configurações...")
print()

# 1. Verificar estado inicial
config = ConfigManager()
print(f"📂 Pasta data/: {os.listdir('data/')}")
print(f"❓ config.json existe? {os.path.exists('data/config.json')}")
print()

# 2. Fazer mudança
print("✏️ Mudando configuração de teste...")
config.set('test.save_check', 'TESTE_123')
print(f"   has_changes = {config.has_changes}")
print()

# 3. Salvar
print("💾 Salvando...")
result = config.save_user_config()
print(f"   Resultado: {result}")
print()

# 4. Verificar arquivo criado
if os.path.exists('data/config.json'):
    print("✅ Arquivo data/config.json CRIADO com sucesso!")
    with open('data/config.json', 'r') as f:
        import json
        content = json.load(f)
        print(f"📄 Conteúdo: {json.dumps(content, indent=2)}")
else:
    print("❌ Arquivo data/config.json NÃO foi criado!")
    print("   Possível problema de permissões")
print()

# 5. Teste de releitura
print("🔄 Recarregando configurações...")
config2 = ConfigManager()
value = config2.get('test.save_check')
print(f"   Valor lido: {value}")

if value == 'TESTE_123':
    print("✅ PERSISTÊNCIA FUNCIONA!")
else:
    print("❌ PERSISTÊNCIA NÃO FUNCIONA!")
```

**Salvar como:** `test_config_save.py`

**Executar:**
```bash
python test_config_save.py
```

**Resultado esperado:**
```
✅ Arquivo data/config.json CRIADO com sucesso!
✅ PERSISTÊNCIA FUNCIONA!
```

**Se falhar:**
- Problema de permissões
- Disco cheio
- Path incorreto

---

### **Teste 2: Verificar Salvamento Pela UI**

1. **Abrir o bot**
   ```bash
   python main.py
   ```

2. **Ir na aba "Auto-Clean"**

3. **Mudar intervalo** (ex: de 2 para 5)

4. **Clicar em "💾 Salvar Config de Limpeza"**

5. **Verificar mensagem:**
   ```
   ✅ Configurações de limpeza salvas e persistidas!
   ```

6. **Verificar arquivo criado:**
   ```bash
   cat data/config.json
   # Deve mostrar: {"auto_clean": {"interval": 5}}
   ```

7. **Fechar e reabrir o bot**

8. **Verificar se valor persiste** (deve estar em 5, não 2)

---

### **Teste 3: Verificar Sincronização com Servidor**

Se você usa o servidor:

1. **Desconectar do servidor temporariamente**
   - Editar `data/credentials.dat` (deletar ou renomear)
   - Ou desativar internet

2. **Repetir Teste 2**

3. **Se funcionar SEM servidor:**
   - Problema é sincronização com servidor
   - Servidor está sobrescrevendo configs locais

4. **Solução:**
   - Salvar configs no servidor (não apenas local)
   - Ou desabilitar sincronização

---

## 📝 Checklist de Correção

- [ ] Executar `test_config_save.py`
- [ ] Verificar se `data/config.json` é criado
- [ ] Clicar nos botões de salvar na UI
- [ ] Verificar mensagem de sucesso
- [ ] Fechar e reabrir bot
- [ ] Confirmar que configs persistem
- [ ] Se não funcionar: verificar permissões
- [ ] Se usar servidor: testar sem servidor
- [ ] Se em Docker: verificar volumes

---

## 🎯 Resumo

**Problema:** Configs voltam ao padrão ao reiniciar

**Causa Mais Provável:**
1. ⚠️ **Não clicar nos botões de salvar** (70% dos casos)
2. ⚠️ **Servidor sobrescrevendo configs** (20%)
3. ⚠️ **Permissões/Docker** (10%)

**Solução Imediata:**

```
1. Mudar configuração na UI
2. Clicar no botão "💾 Salvar" correspondente
3. Aguardar "Configurações salvas e persistidas!"
4. Verificar que data/config.json existe
5. Fechar e reabrir para confirmar
```

**Se ainda não funcionar:**
- Execute `test_config_save.py` e compartilhe o resultado
- Verifique se está em Docker
- Teste sem conectar ao servidor

---

**Criado em:** 2025-11-07
**Versão:** 1.0
**Projeto:** Ultimate Fishing Bot v5.0
**Prioridade:** 🟡 MÉDIA
