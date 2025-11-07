# ⚡ TESTE RÁPIDO DE VALIDAÇÃO

**Use este guia para validar rapidamente se o sistema está funcionando.**

---

## 🚀 TESTE 1: Sistema Funciona Offline (2 minutos)

### Objetivo
Validar que bot funciona sem servidor (modo offline)

### Passos
1. **NÃO iniciar servidor**
2. Abrir terminal
3. Executar: `python main.py`
4. Pressionar F9

### Resultado Esperado
```
✅ Bot inicia normalmente
✅ Ciclo de pesca funciona
⚠️ Log mostra: "Servidor desconectado, modo offline"
✅ Bot continua pescando normalmente
```

### Se falhar
- Verificar se `main.py` existe
- Verificar dependências: `pip install -r requirements.txt`

---

## 🌐 TESTE 2: Cliente Envia Dados ao Servidor (3 minutos)

### Objetivo
Validar que cliente envia `current_rod` e `rod_uses` corretamente

### Passos
1. Terminal 1: `python server/server.py`
2. Terminal 2: `python main.py`
3. Fazer login com license_key válida
4. Pressionar F9
5. Pescar 1 peixe
6. Verificar logs

### Resultado Esperado

**LOG DO CLIENTE:**
```
🌐 [ENGINE→WS] fish_caught enviado (vara 1: 1 usos)
```

**LOG DO SERVIDOR:**
```
🐟 usuario@mail.com: Peixe #1 capturado!
🎣 usuario@mail.com: Vara 1 usada (1/20 usos)
```

### Se falhar
- Verificar se servidor está rodando na porta 8122
- Verificar se cliente conectou ao WebSocket
- Verificar arquivo: `core/fishing_engine.py:1453`

---

## 🍖 TESTE 3: Servidor Decide Alimentação (2 minutos)

### Objetivo
Validar que servidor decide quando alimentar (não o cliente)

### Passos
1. Servidor rodando
2. Cliente conectado
3. Pescar 1 peixe (configuração padrão: alimentar a cada 1 peixe)
4. Verificar logs

### Resultado Esperado

**LOG DO SERVIDOR:**
```
🍖 usuario@mail.com: Trigger de feeding (1 peixes)
🍖 usuario@mail.com: Comando FEED enviado
```

**LOG DO CLIENTE:**
```
🍖 [SERVIDOR] Comando de feeding recebido
   Executando feeding...
   ✅ Feeding executado com sucesso
```

### Se falhar
- Verificar `DEFAULT_RULES["feed_interval_fish"]` no servidor
- Verificar callback registrado: `client/server_connector.py:283`
- Verificar método: `feeding_system.execute_feeding(force=True)`

---

## 🧹 TESTE 4: Servidor Decide Limpeza (2 minutos)

### Objetivo
Validar que servidor decide quando limpar

### Passos
1. Pescar 2 peixes (configuração padrão: limpar a cada 2 peixes)
2. Verificar logs

### Resultado Esperado

**LOG DO SERVIDOR:**
```
🧹 usuario@mail.com: Trigger de cleaning (2 peixes)
🧹 usuario@mail.com: Comando CLEAN enviado (com coordenadas do chest)
```

**LOG DO CLIENTE:**
```
🧹 [SERVIDOR] Comando de limpeza recebido
   📦 Coordenadas do chest: (1400, 500)
   Executando limpeza de inventário...
   ✅ Limpeza concluída, servidor notificado
```

### Se falhar
- Verificar `DEFAULT_RULES["clean_interval_fish"]` no servidor
- Verificar callback: `client/server_connector.py:284`

---

## 🎣 TESTE 5: Servidor Decide Troca de Vara (10 minutos)

### Objetivo
Validar que servidor decide quando trocar par de varas

### Passos
1. Pescar 20 peixes com vara 1
2. Pescar 20 peixes com vara 2
3. No próximo peixe (peixe #41), servidor deve trocar para vara 3
4. Verificar logs

### Resultado Esperado

**LOG DO SERVIDOR (peixe #41):**
```
🔄 usuario@mail.com: Par (1, 2) esgotado (Vara 1: 20, Vara 2: 20)
🔄 usuario@mail.com: Mudança Par0 → Par2 (3, 4)
   Primeira vara do novo par: 3
   ✅ current_rod atualizado para: 3
🎣 usuario@mail.com: Comando SWITCH_ROD_PAIR enviado → Vara 3
```

**LOG DO CLIENTE:**
```
🎣 [SERVIDOR] Comando de troca de par recebido
   Vara alvo: 3
   Executando troca para vara 3...
   📤 Tirando vara 2 da mão (vai abrir baú)...
   📥 Equipando vara 3...
   ✅ Vara 3 equipada com sucesso
```

### Se falhar
- Verificar lógica: `server/server.py:285-305` (should_switch_rod_pair)
- Verificar callback: `client/server_connector.py:263-298`
- Verificar atualização: `server/server.py:327` (current_rod)

---

## 👥 TESTE 6: Multi-Usuário (5 minutos)

### Objetivo
Validar que 2 usuários funcionam independentemente

### Passos
1. Terminal 1: `python server/server.py`
2. Terminal 2: `python main.py` (Cliente A - license_key_A)
3. Terminal 3: `python main.py` (Cliente B - license_key_B)
4. Cliente A: Pressionar F9, pescar 1 peixe
5. Cliente B: Pressionar F9, pescar 3 peixes
6. Verificar logs do servidor

### Resultado Esperado

**LOG DO SERVIDOR:**
```
🎣 Nova sessão criada para: usuario_a@mail.com
🎣 Nova sessão criada para: usuario_b@mail.com

🐟 usuario_a@mail.com: Peixe #1 capturado!
🍖 usuario_a@mail.com: Comando FEED enviado

🐟 usuario_b@mail.com: Peixe #1 capturado!
🍖 usuario_b@mail.com: Comando FEED enviado

🐟 usuario_b@mail.com: Peixe #2 capturado!
🧹 usuario_b@mail.com: Comando CLEAN enviado

🐟 usuario_b@mail.com: Peixe #3 capturado!
🍖 usuario_b@mail.com: Comando FEED enviado
```

**Validação:**
- ✅ Usuário A tem fish_count=1
- ✅ Usuário B tem fish_count=3
- ✅ Comandos enviados ao usuário correto
- ✅ Sessões independentes

### Se falhar
- Verificar `active_sessions` no servidor
- Verificar WebSocket separado por license_key
- Verificar logs mostrando usuários diferentes

---

## 📊 CHECKLIST FINAL

Marque conforme testa:

- [ ] ✅ TESTE 1: Sistema funciona offline
- [ ] ✅ TESTE 2: Cliente envia dados ao servidor
- [ ] ✅ TESTE 3: Servidor decide alimentação
- [ ] ✅ TESTE 4: Servidor decide limpeza
- [ ] ✅ TESTE 5: Servidor decide troca de vara
- [ ] ✅ TESTE 6: Multi-usuário funciona

---

## 🐛 SOLUÇÃO DE PROBLEMAS COMUNS

### Problema: "WebSocket não conecta"
**Solução:**
```bash
# Verificar se servidor está rodando
curl http://localhost:8122/health

# Verificar porta no .env
cat .env | grep PORT
```

### Problema: "Callback não executa"
**Solução:**
- Verificar registro em `client/server_connector.py:283-286`
- Verificar logs do cliente: "Comando X recebido"

### Problema: "Servidor não envia comandos"
**Solução:**
- Verificar logs do servidor: "Trigger de X"
- Verificar `DEFAULT_RULES` no servidor
- Verificar fish_count sendo incrementado

### Problema: "Troca de vara não funciona"
**Solução:**
- Verificar que AMBAS varas do par atingiram 20 usos
- Verificar logs: "Par (X, Y) esgotado"
- Verificar callback recebe target_rod

---

## ⚡ TESTE RÁPIDO COMPLETO (15 minutos)

Execute TODOS os testes em sequência:

```bash
# 1. Teste Offline (2 min)
python main.py
# F9, pescar 1 peixe, verificar funciona

# 2. Iniciar Servidor (1 min)
python server/server.py

# 3. Cliente Conectado (2 min)
python main.py
# Login, F9, pescar 1 peixe

# 4. Verificar Alimentação (2 min)
# Deve alimentar após 1 peixe

# 5. Verificar Limpeza (2 min)
# Deve limpar após 2 peixes

# 6. Multi-Usuário (5 min)
# Abrir 2 clientes, pescar em ambos

# 7. Troca de Vara (opcional, 10 min)
# Pescar até 40 peixes para forçar troca
```

**Tempo total:** ~15 minutos
**Resultado esperado:** Todos os testes passam ✅

---

**Data:** 2025-10-28
**Versão:** 1.0
**Status:** Pronto para teste
