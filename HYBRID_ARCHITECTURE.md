# 🎯 Arquitetura Híbrida - Cliente/Servidor

## 📋 Visão Geral

Sistema com arquitetura **HÍBRIDA** onde:
- **CLIENTE** executa ciclo de pesca e troca de varas localmente
- **SERVIDOR** controla operações de baú (feeding, cleaning, maintenance)

---

## ✅ O QUE FUNCIONA OFFLINE (Cliente Local - SEMPRE)

### 1. Ciclo de Pesca Completo
```
✅ Cliques de mouse (esquerdo/direito)
✅ Movimentos de câmera (A/D)
✅ Detecção de peixe capturado (template matching local)
✅ Contagem de peixes
✅ Estatísticas em tempo real
```

**Localização:** `core/fishing_engine.py`
- `_execute_complete_fishing_cycle()`
- `_execute_rapid_phase_v3()`
- `_execute_slow_phase_v3()`
- `_detect_fish_caught()`

### 2. Troca de Varas DENTRO do Par (Timing Crítico <1s)
```
✅ Par 1: Vara 1 ↔ Vara 2
✅ Par 2: Vara 3 ↔ Vara 4
✅ Par 3: Vara 5 ↔ Vara 6
```

**Localização:** `core/rod_manager.py`
- `switch_to_pair_partner()`
- Executa localmente via hotkey TAB
- Timing crítico: <1 segundo entre detecção e troca

### 3. Troca de PARES (Híbrido - Local OU Servidor)
```
✅ Par 1 → Par 2 (pode ser decidido localmente OU pelo servidor)
✅ Par 2 → Par 3 (pode ser decidido localmente OU pelo servidor)
```

**Localização:** `core/rod_manager.py`
- Pode ser acionado por servidor via comando `switch_rod_pair`
- Pode ser acionado localmente se rod manager detectar necessidade

### 4. Operações Manuais via Hotkeys (SEMPRE Funcionam)
```
F6  - Feeding manual
F5  - Cleaning manual
Page Down - Rod maintenance manual
TAB - Troca de vara no par
```

---

## 🌐 O QUE REQUER SERVIDOR (Online - Automático)

### 1. Feeding Automático
**Decisão:** Servidor decide quando alimentar (a cada N peixes)
**Detecção:** Cliente detecta comida e botão eat
**Construção:** Servidor constrói sequência completa
**Execução:** Cliente executa cegamente

**Fluxo:**
```
Cliente → send_fish_caught(rod_uses, current_rod)
Servidor → session.should_feed() → TRUE
Servidor → send request_template_detection(["filefrito", "eat"])
Cliente → detecta coordenadas
Cliente → send_feeding_locations_detected(food_loc, eat_loc)
Servidor → ActionSequenceBuilder.build_feeding_sequence()
Servidor → send execute_sequence(actions, operation="feeding")
Cliente → ActionExecutor.execute_sequence()
Cliente → send_sequence_completed("feeding")
```

### 2. Cleaning Automático
**Decisão:** Servidor decide quando limpar (a cada N peixes)
**Detecção:** Cliente escaneia inventário e detecta peixes
**Construção:** Servidor constrói sequência de right-clicks
**Execução:** Cliente executa transferências para baú

**Fluxo:**
```
Cliente → send_fish_caught()
Servidor → session.should_clean() → TRUE
Servidor → send request_inventory_scan()
Cliente → scan_inventory() com NMS
Cliente → send_fish_locations_detected(fish_list)
Servidor → ActionSequenceBuilder.build_cleaning_sequence(fish_list)
Servidor → send execute_sequence(actions, operation="cleaning")
Cliente → executa right-clicks + drags
Cliente → send_sequence_completed("cleaning")
```

### 3. Maintenance Automático (Varas Quebradas/Sem Isca)
**Decisão:** Servidor decide quando fazer manutenção (após N timeouts)
**Detecção:** Cliente analisa slots de varas e itens do baú
**Construção:** Servidor decide quais varas trocar e iscas adicionar
**Execução:** Cliente executa substituições

**Fluxo:**
```
Cliente → timeout detectado
Cliente → send_timeout(current_rod)
Servidor → session.increment_timeout(rod) → Limite atingido
Servidor → send request_rod_analysis()
Cliente → analyze_rod_slots() + busca varas/iscas no baú
Cliente → send_rod_status_detected(rod_status, available_items)
Servidor → ActionSequenceBuilder.build_maintenance_sequence()
Servidor → send execute_sequence(actions, operation="maintenance")
Cliente → arrasta varas/iscas para slots
Cliente → send_sequence_completed("maintenance")
```

---

## 🔄 Modo Offline vs Online

### Modo ONLINE (Servidor Conectado)
```
✅ Pesca funciona localmente
✅ Troca de varas funciona localmente
✅ Feeding AUTOMÁTICO (servidor decide)
✅ Cleaning AUTOMÁTICO (servidor decide)
✅ Maintenance AUTOMÁTICO (servidor decide)
✅ Estatísticas sincronizadas com servidor
```

### Modo OFFLINE (Servidor Desconectado)
```
✅ Pesca funciona localmente
✅ Troca de varas funciona localmente
❌ Feeding MANUAL (hotkey F6)
❌ Cleaning MANUAL (hotkey F5)
❌ Maintenance MANUAL (hotkey Page Down)
⚠️ Bot avisa: "Servidor offline - Operações de baú são MANUAIS"
```

**Mensagem Exibida:**
```
📊 [OFFLINE] Peixe #15 capturado
   ℹ️ Servidor offline - Operações de baú são MANUAIS (F6=feed, F5=clean, PgDn=manutenção)
```

---

## 🛠️ Componentes e Responsabilidades

### Cliente (core/)

#### fishing_engine.py
```python
# ✅ SEMPRE LOCAL
- Ciclo de pesca completo
- Detecção de peixe capturado
- Contagem e estatísticas

# 🌐 HÍBRIDO (online/offline)
def increment_fish_count():
    if ws_client.is_connected():
        # ONLINE: Envia ao servidor
        ws_client.send_fish_caught(rod_uses, current_rod)
    else:
        # OFFLINE: Apenas loga, sem operações automáticas
        print("[OFFLINE] Peixe capturado - operações manuais")
```

#### rod_manager.py
```python
# ✅ SEMPRE LOCAL
- switch_to_pair_partner()  # Troca dentro do par (TAB)
- get_current_rod()
- track_rod_usage()

# 🌐 PODE SER SERVIDOR OU LOCAL
- Troca de pares (par 1 → par 2)
```

#### feeding_system.py
```python
# ✅ APENAS EXECUÇÃO (sem decisão)
def execute_feeding(force=False):
    """Executa feeding quando comandado"""
    # NÃO decide QUANDO executar
    # Apenas EXECUTA quando chamado (servidor ou hotkey F6)

# ❌ REMOVIDOS (decisão agora no servidor)
# should_trigger_feeding() - REMOVIDO
# increment_fish_count() - REMOVIDO
```

#### inventory_manager.py
```python
# ✅ APENAS EXECUÇÃO (sem decisão)
def execute_cleaning():
    """Executa limpeza quando comandada"""
    # NÃO decide QUANDO executar
    # Apenas EXECUTA quando chamado (servidor ou hotkey F5)

# ❌ REMOVIDOS (decisão agora no servidor)
# should_trigger_cleaning() - REMOVIDO
# increment_fish_count() - REMOVIDO
```

### Servidor (server/)

#### server.py - FishingSession
```python
class FishingSession:
    # 🔒 LÓGICA DE DECISÃO (PROTEGIDA)

    def should_feed(self) -> bool:
        """Decide quando alimentar (a cada N peixes)"""
        peixes_desde_ultimo = self.fish_count - self.last_feed_at
        return peixes_desde_ultimo >= self.user_config["feed_interval_fish"]

    def should_clean(self) -> bool:
        """Decide quando limpar (a cada N peixes)"""
        peixes_desde_ultimo = self.fish_count - self.last_clean_at
        return peixes_desde_ultimo >= self.user_config["clean_interval_fish"]

    def should_switch_rod_pair(self) -> bool:
        """Decide quando trocar par de varas"""
        current_pair = self.get_current_pair()
        rod1, rod2 = current_pair
        return (self.rod_uses[rod1] >= 20 and self.rod_uses[rod2] >= 20)
```

#### action_sequences.py - ActionSequenceBuilder
```python
class ActionSequenceBuilder:
    # 🏗️ CONSTRUÇÃO DE SEQUÊNCIAS COMPLETAS

    def build_feeding_sequence(food_loc, eat_loc):
        """Constrói 15+ ações atômicas para feeding"""
        actions = [
            {"type": "stop_continuous_clicking"},
            {"type": "key_down", "key": "alt"},
            {"type": "move_camera", "dx": -1200, "dy": -200},
            {"type": "key_press", "key": "e"},
            # ... mais ações
        ]
        return actions

    def build_cleaning_sequence(fish_locations):
        """Constrói sequência de right-clicks para limpar"""

    def build_maintenance_sequence(rod_status, available_items):
        """Constrói sequência de substituição de varas/iscas"""
```

---

## 📊 Comparação: O Que Mudou

### ANTES (v3 - Tudo Local)
```
❌ Cliente decidia tudo:
   - Quando alimentar (should_trigger_feeding)
   - Quando limpar (should_trigger_cleaning)
   - Quando fazer manutenção
   - Como executar operações

❌ Lógica espalhada em múltiplos arquivos
❌ Difícil de atualizar regras
❌ Impossível controlar múltiplos clientes
```

### DEPOIS (v5 - Híbrido)
```
✅ Cliente EXECUTA:
   - Pesca (sempre local)
   - Troca de varas (sempre local)
   - Sequências recebidas do servidor

✅ Servidor DECIDE:
   - Quando alimentar
   - Quando limpar
   - Quando fazer manutenção
   - Como construir sequências

✅ Benefícios:
   - Regras centralizadas
   - Fácil atualizar lógica
   - Controle de múltiplos clientes
   - Cliente funciona offline (sem automações)
```

---

## 🎯 Casos de Uso

### Caso 1: Usuário com Servidor (Recomendado)
```bash
# Servidor rodando (EasyPanel ou local)
python main.py  # Cliente conecta e funciona com automações
```

**Resultado:**
- ✅ Pesca automaticamente
- ✅ Alimenta automaticamente a cada 2 peixes
- ✅ Limpa automaticamente a cada 1 peixe
- ✅ Faz manutenção automaticamente após 3 timeouts

### Caso 2: Usuário Sem Servidor (Fallback)
```bash
# Servidor offline ou não disponível
python main.py  # Cliente funciona em modo manual
```

**Resultado:**
- ✅ Pesca automaticamente
- ⚠️ Usuário precisa apertar F6 para alimentar
- ⚠️ Usuário precisa apertar F5 para limpar
- ⚠️ Usuário precisa apertar Page Down para manutenção

### Caso 3: Servidor Cai Durante Uso
```bash
# Servidor estava conectado, mas caiu
```

**Resultado:**
- ✅ Bot CONTINUA pescando localmente
- ⚠️ Mostra mensagem: "Servidor offline - Operações manuais"
- ⚠️ Automações param, hotkeys ainda funcionam
- ✅ Se servidor voltar, reconecta automaticamente

---

## 📝 Notas Importantes

1. **Prioridade 1:** Ciclo de pesca SEMPRE local (latência zero)
2. **Prioridade 2:** Troca de varas SEMPRE local (timing crítico)
3. **Prioridade 3:** Operações de baú controladas por servidor (não críticas)
4. **Fallback:** Cliente funciona offline, mas SEM automações de baú
5. **Hotkeys:** Sempre funcionam (online ou offline) para operações manuais

---

**Versão:** v5.0 (Hybrid Architecture)
**Última Atualização:** 2025-10-29
**Status:** ✅ Implementado e Funcional
