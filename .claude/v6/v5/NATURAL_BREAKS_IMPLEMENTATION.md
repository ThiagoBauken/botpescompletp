# ⚠️ **SISTEMA DE PAUSAS NATURAIS - NÃO IMPLEMENTADO NO V5**

## 🚨 **PROBLEMA**

O v5 **NÃO TEM** sistema de pausas naturais (anti-detecção), que existe no v3.

### **O que são Pausas Naturais?**

Pausas automáticas que simulam comportamento humano:
- **Por tempo:** Pausa a cada X minutos
- **Por pescas:** Pausa a cada Y peixes capturados
- **Duração aleatória:** Entre MIN e MAX segundos

**Exemplo:** Pausa de 15-45 minutos a cada 50 peixes capturados.

---

## 📋 **COMO FUNCIONA NO V3**

### **1. Configuração**

```python
'natural_breaks': {
    'enabled': True,
    'mode': 'catches',  # 'time' ou 'catches'
    'time_interval': 45,  # minutos
    'catches_interval': 50,  # peixes
    'pause_duration_min': 15,  # segundos
    'pause_duration_max': 45,  # segundos
    'last_break_time': 0,
    'catches_since_break': 0
}
```

### **2. Verificação (v3 linha 8876-8899)**

```python
def check_natural_break(self):
    """Verificar se é hora de fazer uma pausa natural"""
    if not self.anti_detection['enabled'] or not self.anti_detection['natural_breaks']['enabled']:
        return False

    breaks = self.anti_detection['natural_breaks']

    # Verificar por tempo
    if breaks['mode'] == 'time':
        time_since_break = time.time() - breaks['last_break_time']
        if time_since_break >= breaks['time_interval'] * 60:
            return True

    # Verificar por pescas
    elif breaks['mode'] == 'catches':
        if breaks['catches_since_break'] >= breaks['catches_interval']:
            return True

    return False
```

### **3. Execução (v3 linha 8960-8991)**

```python
def execute_natural_break(self):
    """Executar uma pausa natural"""
    breaks = self.anti_detection['natural_breaks']

    # Calcular duração da pausa (aleatória)
    pause_duration = random.uniform(
        breaks['pause_duration_min'],
        breaks['pause_duration_max']
    )

    print(f"\n☕ PAUSA NATURAL - Simulando comportamento humano...")
    print(f"   • Duração: {pause_duration:.1f} segundos")

    # Soltar todos os botões antes da pausa
    self.release_all_keys()

    # Executar a pausa
    start_time = time.time()
    while time.time() - start_time < pause_duration and self.running:
        time.sleep(0.5)

    # Atualizar contadores
    breaks['last_break_time'] = time.time()
    breaks['catches_since_break'] = 0

    print("   ✅ Pausa natural concluída, retomando...")
```

### **4. Chamada no Main Loop (v3 linha 10931-10933)**

```python
# Verificar se é hora de fazer pausa natural
if self.check_natural_break():
    self.execute_natural_break()

# Executar ciclo de pesca
self.executar_ciclo_completo_yolo()
```

---

## ❌ **PROBLEMA NO V3**

A pausa natural **NÃO RESPEITA** operações de baú em andamento:

**Cenário problemático:**
```
1. Peixe #50 capturado (trigger pausa)
2. Limpeza iniciada (baú aberto)
3. ❌ check_natural_break() retorna True
4. ❌ execute_natural_break() executa IMEDIATAMENTE
5. ❌ release_all_keys() fecha baú/inventário
6. ❌ Limpeza é interrompida!
```

---

## ✅ **SOLUÇÃO PARA V5**

### **Implementação Corrigida**

A pausa natural deve **RESPEITAR** o sistema de prioridades:

```python
# Loop principal
while not self.stop_event.is_set():
    # 1. Verificar pausa
    if self.is_paused:
        time.sleep(0.5)
        continue

    # 2. ✅ VERIFICAR PAUSA NATURAL (COM RESPEITO AOS MÓDULOS)
    if self._should_execute_natural_break():
        # Verificar se há operações em andamento
        if not self._is_safe_to_pause():
            _safe_print("⏸️ [PAUSA NATURAL] Operação em andamento - aguardando...")
            time.sleep(1.0)
            continue  # Aguardar próximo loop

        # Seguro para pausar
        self._execute_natural_break()
        continue

    # 3. PRIORIDADES (feeding/manutenção/limpeza)
    if self.process_priority_tasks():
        continue

    # 4. Troca de vara
    # ...

    # 5. Pesca
    # ...
```

### **Verificação de Segurança**

```python
def _is_safe_to_pause(self) -> bool:
    """Verificar se é seguro pausar (sem operações em andamento)"""
    # Verificar se baú/inventário está aberto
    inventory_open = self.game_state.get('inventory_open', False)
    chest_open = self.game_state.get('chest_open', False)

    if inventory_open or chest_open:
        return False

    # Verificar se há ação em progresso
    action_in_progress = self.game_state.get('action_in_progress', False)
    if action_in_progress:
        return False

    return True
```

---

## 📊 **COMPARAÇÃO**

| Aspecto | V3 | V5 (PROPOSTO) |
|---------|-----|---------------|
| **Pausa Natural** | ✅ Implementado | ❌ NÃO implementado |
| **Respeita Baú Aberto** | ❌ NÃO | ✅ SIM |
| **Respeita Limpeza** | ❌ NÃO | ✅ SIM |
| **Respeita Manutenção** | ❌ NÃO | ✅ SIM |
| **Respeita Feeding** | ❌ NÃO | ✅ SIM |
| **Segurança** | ⚠️ Pode interromper | ✅ Aguarda finalizar |

---

## 🎯 **ORDEM DE EXECUÇÃO CORRETA (V5)**

```
LOOP PRINCIPAL:
├─ 1. Verificar pausa (F1)
├─ 2. ✅ PAUSA NATURAL (com verificação de segurança):
│     ├─ needs_break? NÃO → continuar
│     ├─ needs_break? SIM:
│     │   ├─ is_safe_to_pause? NÃO → aguardar
│     │   └─ is_safe_to_pause? SIM → EXECUTAR PAUSA
│     └─ Após pausa → continuar loop
│
├─ 3. PRIORIDADES (sempre primeiro):
│     ├─ Feeding
│     ├─ Manutenção
│     └─ Limpeza
│
├─ 4. TROCA DE VARA (com verificação):
│     ├─ needs_switch? SIM
│     ├─ inventory_open? NÃO
│     ├─ chest_open? NÃO
│     └─ EXECUTAR TROCA
│
└─ 5. PESCA (só se tudo OK)
```

---

## 📝 **IMPLEMENTAÇÃO NECESSÁRIA**

### **Arquivos a Modificar:**

1. **`core/fishing_engine.py`**
   - Adicionar `_should_execute_natural_break()`
   - Adicionar `_is_safe_to_pause()`
   - Adicionar `_execute_natural_break()`
   - Adicionar chamada no loop principal

2. **`config/default_config.json`**
   - Adicionar seção `natural_breaks`

3. **`ui/main_window.py`**
   - Adicionar controles na aba Anti-Detection

---

**Status:** ❌ **NÃO IMPLEMENTADO NO V5**
**Prioridade:** 🔥 **CRÍTICA** (Anti-Detecção essencial)
**Complexidade:** ⭐⭐⭐ (Média - precisa integração com sistema de prioridades)
