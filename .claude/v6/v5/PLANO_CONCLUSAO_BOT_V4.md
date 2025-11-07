# 🎯 PLANO DE CONCLUSÃO - ULTIMATE FISHING BOT V4.0

## 📋 VISÃO GERAL
Concluir o bot v4.0 reutilizando as funcionalidades COMPROVADAMENTE FUNCIONAIS do botpesca.py (v3), mas com arquitetura modular limpa.

## ✅ FUNCIONALIDADES FUNCIONAIS DO V3 PARA MIGRAR

### 🎣 1. DETECÇÃO DE PEIXE (PRIORIDADE MÁXIMA)
**Funções do v3 para extrair:**
- `detect_fish_caught_template()` - Linha 14691
- `wait_for_fish_caught_template()` - Template matching com timeout
- `setup_catch_template()` - Configuração inicial

**Implementação no v4:**
```python
# fishing_bot_v4/core/template_engine.py
def detect_fish_caught(self) -> Tuple[bool, float]:
    """Detectar peixe usando APENAS template matching (funciona no v3)"""
    # Copiar lógica exata de detect_fish_caught_template()
    # Template: templates/catch.png
    # Threshold: 0.6-0.8 (configurável)
```

### 🔄 2. SISTEMA DE VARAS (SEGUNDA PRIORIDADE)
**Funções do v3 para extrair:**
- `perform_rod_switch_sequence_SLOTS_REAIS()` - Troca inteligente
- `get_next_rod_with_bait()` - Próxima vara com isca
- `check_rod_status()` - Status da vara (com/sem isca/quebrada)

**Implementação no v4:**
```python
# fishing_bot_v4/core/rod_manager.py (CRIAR NOVO)
class RodManager:
    def __init__(self):
        self.rod_pairs = [(1,2), (3,4), (5,6)]
        self.current_pair = 0
        self.rod_uses = {1:20, 2:20, 3:20, 4:20, 5:20, 6:20}
    
    def switch_rod(self):
        # Copiar lógica de perform_rod_switch_sequence_SLOTS_REAIS()
```

### 🍖 3. SISTEMA DE ALIMENTAÇÃO (TERCEIRA PRIORIDADE) 
**Funções do v3 para extrair:**
- `find_and_click_food_automatically()` - Linha 16596
- `f6_feeding_handler()` - Handler da tecla F6
- Coordenadas: slot1=[1306,858], slot2=[1403,877], eat=[1083,373]

**Completar no v4:**
```python
# fishing_bot_v4/core/feeding_system.py
def execute_feeding(self):
    """Executar alimentação completa"""
    # 1. Abrir baú via ChestManager
    # 2. Detectar comida via templates
    # 3. Clicar nas posições corretas
    # 4. Fechar baú
```

### 🧹 4. AUTO-CLEAN (QUARTA PRIORIDADE)
**Funções do v3 para extrair:**
- `auto_clean_inventory()` - Limpeza automática
- Templates de peixes: salmon.png, sardine.png, etc.
- Lógica de transferência para baú

**Criar no v4:**
```python
# fishing_bot_v4/core/inventory_manager.py (CRIAR NOVO)
class InventoryManager:
    def auto_clean(self):
        # 1. Detectar peixes no inventário
        # 2. Abrir baú
        # 3. Transferir peixes
        # 4. Fechar baú
```

## 📐 ARQUITETURA DE IMPLEMENTAÇÃO

### FASE 1: CORE MÍNIMO (1-2 dias)
```
fishing_bot_v4/
├── core/
│   ├── template_engine.py     ← COMPLETAR detect_fish_caught()
│   ├── fishing_engine.py      ← IMPLEMENTAR ciclo básico
│   └── input_manager.py       ← ADICIONAR clicks e teclas
```

**Tarefas:**
1. ✅ Copiar `detect_fish_caught_template()` do v3
2. ✅ Implementar ciclo básico de pesca
3. ✅ Adicionar controle de mouse/teclado
4. ✅ Testar detecção básica

### FASE 2: SISTEMA DE VARAS (2-3 dias)
```
fishing_bot_v4/
├── core/
│   ├── rod_manager.py        ← CRIAR NOVO
│   └── template_engine.py    ← ADICIONAR detecção de varas
```

**Tarefas:**
1. ✅ Criar classe RodManager
2. ✅ Migrar lógica de troca de varas
3. ✅ Adicionar templates: VARANOBAUCI.png, enbausi.png, varaquebrada.png
4. ✅ Implementar detecção de status

### FASE 3: SISTEMAS AUXILIARES (2-3 dias)
```
fishing_bot_v4/
├── core/
│   ├── inventory_manager.py  ← CRIAR NOVO
│   └── feeding_system.py     ← COMPLETAR
```

**Tarefas:**
1. ✅ Completar FeedingSystem
2. ✅ Criar InventoryManager
3. ✅ Integrar com ChestManager
4. ✅ Adicionar auto-clean

### FASE 4: INTEGRAÇÃO FINAL (1-2 dias)
**Tarefas:**
1. ✅ Conectar todos os módulos
2. ✅ Adicionar hotkeys funcionais
3. ✅ Atualizar UI para refletir status
4. ✅ Testes completos

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. COMPLETAR template_engine.py
```python
# Adicionar ao template_engine.py existente

def detect_fish_caught(self, threshold=0.7) -> Tuple[bool, float]:
    """Detectar peixe capturado - COPIAR DO V3"""
    try:
        # Capturar tela
        screenshot = self.capture_screen()
        
        # Carregar template catch.png
        template = self.template_cache.get('catch')
        if template is None:
            return False, 0.0
        
        # Template matching (EXATO como v3)
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            return True, max_val
            
        return False, max_val
        
    except Exception as e:
        print(f"Erro na detecção: {e}")
        return False, 0.0

def detect_rod_status(self, slot: int) -> str:
    """Detectar status da vara no slot"""
    # Detectar VARANOBAUCI.png → "com_isca"
    # Detectar enbausi.png → "sem_isca"  
    # Detectar varaquebrada.png → "quebrada"
    # Nada detectado → "vazio"
```

### 2. COMPLETAR fishing_engine.py
```python
# Adicionar ao fishing_engine.py existente

def fishing_cycle(self):
    """Ciclo principal de pesca - BASEADO NO V3"""
    while self.is_running:
        try:
            # 1. Verificar se precisa trocar vara
            if self.rod_manager and self.rod_manager.needs_switch():
                self.rod_manager.switch_rod()
            
            # 2. Lançar linha (botão direito)
            self.input_manager.mouse_down(button='right')
            time.sleep(1.6)  # Tempo do v3
            self.input_manager.mouse_up(button='right')
            
            # 3. Fase rápida de cliques
            self.execute_fast_phase()
            
            # 4. Aguardar peixe com timeout
            start_time = time.time()
            timeout = self.config_manager.get('cycle_timeout', 122)
            
            while time.time() - start_time < timeout:
                if self.is_paused or not self.is_running:
                    break
                    
                # Detectar peixe
                found, confidence = self.template_engine.detect_fish_caught()
                if found:
                    print(f"🎣 Peixe detectado! Confiança: {confidence:.2f}")
                    self.on_fish_caught()
                    break
                
                # Continuar clicando
                self.input_manager.click()
                time.sleep(0.1)
            
            # 5. Verificar timeout
            if time.time() - start_time >= timeout:
                print("⏱️ Timeout alcançado, reiniciando ciclo")
                
        except Exception as e:
            print(f"Erro no ciclo: {e}")
            time.sleep(1)

def execute_fast_phase(self):
    """Fase rápida de cliques - COPIAR DO V3"""
    # Implementar lógica de executar_fase_rapida_com_tempo()
    pass
```

### 3. CRIAR rod_manager.py
```python
# fishing_bot_v4/core/rod_manager.py

class RodManager:
    """Sistema de Gerenciamento de Varas"""
    
    def __init__(self, template_engine, input_manager, config_manager):
        self.template_engine = template_engine
        self.input_manager = input_manager
        self.config_manager = config_manager
        
        # Configuração de varas (do v3)
        self.rod_pairs = [(1,2), (3,4), (5,6)]
        self.current_pair_index = 0
        self.current_rod_in_pair = 0
        
        # Contador de usos
        self.rod_uses = {
            1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 20
        }
        
        # Status das varas
        self.rod_status = {
            1: "unknown", 2: "unknown", 3: "unknown",
            4: "unknown", 5: "unknown", 6: "unknown"
        }
    
    def get_current_rod(self) -> int:
        """Obter vara atual"""
        pair = self.rod_pairs[self.current_pair_index]
        return pair[self.current_rod_in_pair]
    
    def needs_switch(self) -> bool:
        """Verificar se precisa trocar vara"""
        current = self.get_current_rod()
        return self.rod_uses[current] <= 0
    
    def switch_rod(self):
        """Trocar para próxima vara com isca"""
        # COPIAR LÓGICA DE perform_rod_switch_sequence_SLOTS_REAIS()
        print(f"🔄 Trocando vara...")
        
        # Tecla Tab para abrir inventário
        self.input_manager.press_key('tab')
        time.sleep(0.5)
        
        # Detectar status de todas as varas
        self.update_all_rod_status()
        
        # Encontrar próxima vara com isca
        next_rod = self.find_next_rod_with_bait()
        
        if next_rod:
            # Clicar na vara
            self.click_on_rod_slot(next_rod)
            print(f"✅ Trocado para vara {next_rod}")
        
        # Fechar inventário
        self.input_manager.press_key('tab')
    
    def update_all_rod_status(self):
        """Atualizar status de todas as varas"""
        for slot in range(1, 7):
            status = self.template_engine.detect_rod_status(slot)
            self.rod_status[slot] = status
            print(f"  Vara {slot}: {status}")
    
    def find_next_rod_with_bait(self) -> Optional[int]:
        """Encontrar próxima vara com isca"""
        # Priorizar varas do par atual
        current_pair = self.rod_pairs[self.current_pair_index]
        
        for rod in current_pair:
            if self.rod_status[rod] == "com_isca":
                return rod
        
        # Se não houver no par, procurar em outros pares
        for pair in self.rod_pairs:
            if pair != current_pair:
                for rod in pair:
                    if self.rod_status[rod] == "com_isca":
                        return rod
        
        return None
    
    def click_on_rod_slot(self, slot: int):
        """Clicar no slot da vara"""
        # Coordenadas do v3
        slot_positions = {
            1: (709, 1005), 2: (805, 1005), 3: (899, 1005),
            4: (992, 1005), 5: (1092, 1005), 6: (1188, 1005)
        }
        
        if slot in slot_positions:
            x, y = slot_positions[slot]
            self.input_manager.click(x, y)
```

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### ✅ SEMANA 1: FUNCIONALIDADE BÁSICA
- [ ] **Dia 1-2**: Completar TemplateEngine
  - [ ] Migrar detect_fish_caught_template()
  - [ ] Adicionar detect_rod_status()
  - [ ] Testar detecção com catch.png
  
- [ ] **Dia 3-4**: Completar FishingEngine  
  - [ ] Implementar fishing_cycle()
  - [ ] Adicionar execute_fast_phase()
  - [ ] Integrar com TemplateEngine
  
- [ ] **Dia 5**: Criar RodManager
  - [ ] Implementar sistema de varas
  - [ ] Migrar lógica de troca
  - [ ] Testar com interface

### ✅ SEMANA 2: SISTEMAS AUXILIARES
- [ ] **Dia 6-7**: Completar FeedingSystem
  - [ ] Implementar execute_feeding()
  - [ ] Adicionar detecção de comida
  - [ ] Integrar F6 hotkey
  
- [ ] **Dia 8-9**: Criar InventoryManager
  - [ ] Implementar auto_clean()
  - [ ] Adicionar detecção de peixes
  - [ ] Configurar intervalos
  
- [ ] **Dia 10**: Integração Final
  - [ ] Conectar todos os sistemas
  - [ ] Atualizar UI
  - [ ] Testes completos

## 🎯 RESULTADO ESPERADO

Ao final de 2 semanas, teremos:
1. **Bot 100% funcional** com todas as features do v3
2. **Arquitetura modular** e manutenível
3. **Código limpo** sem as 27,000 linhas de caos
4. **Pronto para evolução** para sistema distribuído

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **AGORA**: Completar `template_engine.py` com detect_fish_caught()
2. **HOJE**: Testar detecção básica de peixes
3. **AMANHÃ**: Implementar ciclo de pesca em `fishing_engine.py`
4. **ESTA SEMANA**: Ter bot pescando com sucesso

---

**IMPORTANTE**: Usar SEMPRE o código do botpesca.py como referência, copiando as partes que FUNCIONAM e adaptando para a arquitetura modular.