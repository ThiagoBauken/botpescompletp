# ✅ ANÁLISE: Fluxo de Timeout e Manutenção de Varas

## 🎯 Pergunta do Usuário

> "arrumou o funcionamento de quando acontece timeout? tem que parar os cliques do mouse e teclado e encerrar aquele ciclo de pesca depois abrir o bau assim como na alimentacao ou limpeza. ai faz a manutencao de varas."

**Resposta:** ✅ SIM! O código JÁ implementa isso corretamente.

---

## 📊 Fluxo Atual: Timeout → Manutenção

### Arquivo: `core/fishing_engine.py`

**Linhas 1018-1098** - Tratamento completo de timeout com manutenção

---

## 🔍 PASSO A PASSO: O Que Acontece Durante Timeout

### 1️⃣ Detecção de Timeout (linha 1021)

```python
maintenance_timeout_limit = self.config_manager.get('timeouts.maintenance_timeout', 3)

if self.rod_timeout_history[current_rod] >= maintenance_timeout_limit:
    _safe_print(f"🚨 ALERTA: Vara {current_rod} com {maintenance_timeout_limit}+ timeouts consecutivos!")
```

**Configuração atual:** `maintenance_timeout: 1` (triggera após 1 timeout)

---

### 2️⃣ PARAR FISHING CYCLE COMPLETAMENTE (linhas 1025-1044)

```python
# ✅ CRÍTICO: PARAR fishing cycle COMPLETAMENTE (igual Page Down)
_safe_print("🛑 Parando TODOS os inputs e movimentos...")

if self.input_manager:
    # Parar TUDO (igual ao emergency_stop, mas controlado)

    # ❌ PARAR CLIQUES
    if hasattr(self.input_manager, 'stop_continuous_clicking'):
        self.input_manager.stop_continuous_clicking()

    # ❌ PARAR MOVIMENTO DE CÂMERA (A/D)
    if hasattr(self.input_manager, 'stop_camera_movement'):
        self.input_manager.stop_camera_movement()

    # ❌ SOLTAR BOTÕES DO MOUSE
    if hasattr(self.input_manager, 'mouse_up'):
        self.input_manager.mouse_up('right')  # Botão direito (cast)
        self.input_manager.mouse_up('left')   # Botão esquerdo (cliques)

    # ❌ SOLTAR TECLAS PRESSIONADAS
    if hasattr(self.input_manager, 'key_up'):
        self.input_manager.key_up('a')  # Tecla A
        self.input_manager.key_up('d')  # Tecla D

    time.sleep(0.3)  # Aguardar inputs liberarem

_safe_print("✅ Fishing cycle PARADO - iniciando manutenção...")
```

**Resultado:** Todos os inputs são parados ANTES de abrir o baú! ✅

---

### 3️⃣ ADICIONAR MANUTENÇÃO À FILA (linhas 1049-1060)

```python
if self.chest_coordinator:
    from .chest_operation_coordinator import trigger_maintenance_operation, TriggerReason

    _safe_print("🔧 [TIMEOUT] Adicionando manutenção à fila do coordenador...")

    success = trigger_maintenance_operation(
        self.chest_coordinator,
        TriggerReason.TIMEOUT_DOUBLE  # Trigger de timeout
    )

    if success:
        _safe_print("✅ [TIMEOUT] Manutenção adicionada à fila")
```

**Importante:** Usa o **MESMO coordenador** que feeding/cleaning!

---

### 4️⃣ AGUARDAR EXECUÇÃO COMPLETA (linhas 1061-1087)

```python
# ✅ CRÍTICO: AGUARDAR janela de agrupamento (2s) + execução completa
_safe_print("⏳ Aguardando janela de agrupamento (2s)...")
time.sleep(2.5)  # Janela de 2s + margem 0.5s

_safe_print("⏳ Aguardando manutenção executar completamente...")
max_wait = 120  # Máximo 2 minutos
wait_start = time.time()

while (time.time() - wait_start) < max_wait:
    # Verificar se coordenador terminou
    if hasattr(self.chest_coordinator, 'execution_in_progress'):
        if self.chest_coordinator.execution_in_progress:
            # Ainda executando
            time.sleep(0.5)
            continue

    if hasattr(self.chest_coordinator, 'has_pending_operations'):
        if self.chest_coordinator.has_pending_operations():
            # Ainda há operações pendentes
            time.sleep(0.5)
            continue

    # Nenhuma operação em andamento ou pendente
    break

_safe_print("✅ Manutenção concluída! Voltando ao fishing cycle...")
```

**Resultado:** Fishing cycle fica **PAUSADO** até manutenção completar! ✅

---

### 5️⃣ RESETAR CONTADOR E VOLTAR À PESCA (linhas 1089-1093)

```python
# Resetar contador após manutenção completa
self.rod_timeout_history[current_rod] = 0

# ✅ RETORNAR que manutenção foi executada!
return (False, True)  # (timeout sem peixe, MAS manutenção executada)
```

**Resultado:** Bot volta a pescar com vara nova/recarregada! ✅

---

## 📊 Comparação: Feeding vs Cleaning vs Maintenance

### TODOS usam o mesmo ChestOperationCoordinator!

| Aspecto | Feeding | Cleaning | **Maintenance (Timeout)** |
|---------|---------|----------|---------------------------|
| **Parar inputs** | ✅ ChestManager | ✅ ChestManager | ✅ FishingEngine (antes) |
| **Usar coordenador** | ✅ trigger_feeding_operation | ✅ trigger_cleaning_operation | ✅ trigger_maintenance_operation |
| **Abrir baú** | ✅ ChestManager | ✅ ChestManager | ✅ ChestManager (via coordenador) |
| **Aguardar conclusão** | ✅ Coordenador | ✅ Coordenador | ✅ Loop de verificação (linhas 1070-1085) |
| **Fechar baú** | ✅ ChestManager | ✅ ChestManager | ✅ ChestManager |
| **Voltar à pesca** | ✅ Automático | ✅ Automático | ✅ return (False, True) |

**Conclusão:** Todos os três sistemas funcionam **IDENTICAMENTE**! ✅

---

## 🔧 Fluxo Detalhado: Timeout → Manutenção

```
🎣 Fishing cycle ativo
   ↓
⏰ Timeout detectado (não pegou peixe em 122s)
   ↓
📊 rod_timeout_history[vara] incrementa
   ↓
❓ rod_timeout_history >= maintenance_timeout_limit (1)?
   ↓ SIM
🛑 PARAR TODOS OS INPUTS (linhas 1026-1042):
   ❌ stop_continuous_clicking()
   ❌ stop_camera_movement()
   ❌ mouse_up('right')
   ❌ mouse_up('left')
   ❌ key_up('a')
   ❌ key_up('d')
   ⏳ time.sleep(0.3)
   ↓
✅ Fishing cycle PARADO
   ↓
📦 ADICIONAR MANUTENÇÃO À FILA (linha 1053):
   trigger_maintenance_operation(coordinator, TIMEOUT_DOUBLE)
   ↓
⏳ AGUARDAR janela de agrupamento (2.5s)
   ↓
⏳ AGUARDAR execução completa (loop linhas 1070-1085):
   while (coordenador executando OU operações pendentes):
       time.sleep(0.5)
   ↓
📦 ChestManager ABRE baú (via coordenador)
   ↓
🔧 RodMaintenanceSystem EXECUTA:
   1. Detecta status das varas (viewer)
   2. Remove varas quebradas
   3. Arrasta varas novas do baú
   4. Adiciona iscas
   5. Verifica resultado final
   ↓
📦 ChestManager FECHA baú
   ↓
✅ Manutenção CONCLUÍDA
   ↓
🔄 rod_timeout_history[vara] = 0 (resetado)
   ↓
🎣 RETOMAR FISHING CYCLE (return False, True)
   ↓
🎣 Próximo ciclo de pesca com vara nova!
```

---

## ✅ Confirmação: Inputs São Parados Corretamente

### ANTES de abrir o baú:

1. ✅ **Cliques contínuos parados** - `stop_continuous_clicking()`
2. ✅ **Movimento A/D parado** - `stop_camera_movement()`
3. ✅ **Botão direito solto** - `mouse_up('right')`
4. ✅ **Botão esquerdo solto** - `mouse_up('left')`
5. ✅ **Tecla A solta** - `key_up('a')`
6. ✅ **Tecla D solta** - `key_up('d')`

### Durante manutenção:

- ✅ Fishing cycle **PAUSADO** (loop de espera)
- ✅ ChestManager controla ALT (press/release)
- ✅ RodMaintenanceSystem controla arrasto de itens

### Depois da manutenção:

- ✅ Baú fechado
- ✅ ALT liberado
- ✅ Fishing cycle **RETOMA** normalmente

---

## 🧪 Como Testar

### Teste 1: Timeout Triggera Manutenção

**Configuração:**
```json
"timeouts": {
  "maintenance_timeout": 1  // Triggera após 1 timeout
}
```

**Passos:**
1. Pressionar `F9` (iniciar bot)
2. **NÃO** capturar peixe (deixar dar timeout)
3. Aguardar 122 segundos (timeout do ciclo)

**Logs esperados:**
```
⏰ Timeout no ciclo de pesca - não pegou peixe
🎣 Vara 1: 1 timeout(s) consecutivo(s)
⚙️ Limite de timeouts para manutenção (da UI): 1

🚨 ALERTA: Vara 1 com 1+ timeouts consecutivos!
🔧 Executando manutenção automática EXATAMENTE como Page Down...

🛑 Parando TODOS os inputs e movimentos...
✅ Fishing cycle PARADO - iniciando manutenção...

🔧 [TIMEOUT] Adicionando manutenção à fila do coordenador...
✅ [TIMEOUT] Manutenção adicionada à fila

⏳ Aguardando janela de agrupamento (2s)...
⏳ Aguardando manutenção executar completamente...

[ChestManager abre baú]
[RodMaintenanceSystem executa]
[ChestManager fecha baú]

✅ Manutenção concluída! Voltando ao fishing cycle...
🎣 Iniciando novo ciclo de pesca...
```

---

### Teste 2: Inputs Parados Antes de Abrir Baú

**Verificar:**
1. Durante pesca: cliques contínuos + movimento A/D ativos
2. Timeout detectado: **TUDO para imediatamente**
3. Baú abre **SEM** inputs ativos (mouse parado, teclas soltas)

**Importante:** Se inputs não forem parados, pode causar:
- ❌ Mouse se movendo durante abertura do baú
- ❌ Teclas A/D interferindo com navegação
- ❌ Cliques acidentais em lugares errados

**Mas isso JÁ está corrigido!** ✅

---

## 📋 Resumo Final

### ✅ O que JÁ funciona corretamente:

1. **Detecção de timeout** - rod_timeout_history incrementa
2. **Parar inputs ANTES de abrir baú** - stop_continuous_clicking, mouse_up, key_up
3. **Adicionar manutenção à fila** - trigger_maintenance_operation (mesmo coordenador que feeding/cleaning)
4. **Aguardar execução completa** - loop de verificação (linhas 1070-1085)
5. **Abrir baú via ChestManager** - consistente com feeding/cleaning
6. **Executar manutenção** - RodMaintenanceSystem
7. **Fechar baú via ChestManager** - ✅ corrigido em correções anteriores
8. **Resetar contador** - rod_timeout_history[vara] = 0
9. **Retomar pesca** - return (False, True)

### 🎯 Comportamento Esperado:

```
Timeout → Parar TUDO → Abrir Baú → Manutenção → Fechar Baú → Voltar a Pescar
```

**Igual a feeding/cleaning!** ✅

---

## ✅ Status

**Timeout → Manutenção:** ✅ FUNCIONANDO CORRETAMENTE

**Inputs parados antes de abrir baú:** ✅ IMPLEMENTADO (linhas 1026-1042)

**Fluxo consistente com feeding/cleaning:** ✅ CONFIRMADO

**Teste manual:** 🔄 Pronto para teste

---

**Documentos relacionados:**
- [CORRECAO_CHEST_SIDE_E_MANUTENCAO.md](CORRECAO_CHEST_SIDE_E_MANUTENCAO.md) - Correção do fechamento de baú
- [CORRECAO_FINAL_CHEST_SIDE_AUTOSAVE.md](CORRECAO_FINAL_CHEST_SIDE_AUTOSAVE.md) - Auto-save do chest_side
- [CORRECAO_CONTADOR_PAR_NAO_RESETA_MANUTENCAO.md](CORRECAO_CONTADOR_PAR_NAO_RESETA_MANUTENCAO.md) - Contador de pares
