# 🧪 Teste Page Down - Manutenção de Varas

## Como Testar

### 1. Iniciar Bot
```bash
cd fishing_bot_v4
python main.py
```

### 2. Verificar Console na Inicialização
Procurar por estas linhas:
```
🎣 FishingEngine inicializado com componentes:
  📋 TemplateEngine: ✅
  🖱️ InputManager: ✅
  🎣 RodManager: ✅
  🍖 FeedingSystem: ✅
  📦 InventoryManager: ✅
  🎁 ChestManager: ✅
  🏪 ChestCoordinator: ✅    ← DEVE TER ISSO!
```

**Se `ChestCoordinator: ❌`** → Problema na inicialização

### 3. Pressionar Page Down
Observar mensagens no console:

#### Cenário 1: Funcionando
```
🔧 [PAGE DOWN] Trigger de manutenção de vara ativado
🔧 [PAGE DOWN] SISTEMA DE MANUTENÇÃO COORDENADA ATIVADO
✅ [PAGE DOWN] Manutenção coordenada executada com sucesso!
✅ [PAGE DOWN] Manutenção de vara executada com sucesso
```

#### Cenário 2: FishingEngine não disponível
```
🔧 [PAGE DOWN] Trigger de manutenção de vara ativado
⚠️ [PAGE DOWN] FishingEngine não disponível
❌ [PAGE DOWN] Falha na manutenção de vara
```

#### Cenário 3: RodManager não disponível
```
🔧 [PAGE DOWN] Trigger de manutenção de vara ativado
🔧 [PAGE DOWN] SISTEMA DE MANUTENÇÃO COORDENADA ATIVADO (pode não aparecer)
⚠️ [PAGE DOWN] RodManager não disponível
❌ [PAGE DOWN] Falha na manutenção de vara
```

#### Cenário 4: Erro na execução
```
🔧 [PAGE DOWN] Trigger de manutenção de vara ativado
❌ [PAGE DOWN] Erro no sistema de manutenção: [erro aqui]
[Traceback completo]
```

---

## O Que Cada Mensagem Significa

### ⚠️ FishingEngine não disponível
**Causa:** FishingEngine não foi criado na UI
**Solução:** Verificar inicialização na UI (linhas 317-327)

### ⚠️ RodManager não disponível
**Causa:** `self.chest_coordinator` ou `self.rod_manager` é None
**Solução:** Verificar:
1. RodManager foi passado ao FishingEngine?
2. ChestCoordinator foi inicializado?

### ❌ Erro no sistema de manutenção
**Causa:** Exception durante execução
**Solução:** Ver traceback completo no console

---

## Qual É a Mensagem que Você Vê?

Por favor, pressione **Page Down** e copie TODA a saída do console aqui.

Exemplo do que procurar:
```
🔧 [PAGE DOWN] ...
... outras mensagens ...
```

Com essa informação consigo identificar exatamente onde está falhando!

---

## Debug Adicional

Se quiser mais detalhes, adicione estas linhas temporariamente:

### No arquivo `ui/main_window.py`, linha 463:
```python
def trigger_rod_maintenance(self):
    """Trigger de manutenção de vara (PAGE DOWN) - Igual ao botpesca.py"""
    try:
        print("🔧 [DEBUG] trigger_rod_maintenance chamado")
        print(f"🔧 [DEBUG] self tem fishing_engine? {hasattr(self, 'fishing_engine')}")
        print(f"🔧 [DEBUG] fishing_engine existe? {self.fishing_engine is not None if hasattr(self, 'fishing_engine') else False}")

        if hasattr(self, 'fishing_engine') and self.fishing_engine:
            print("🔧 [PAGE DOWN] Trigger de manutenção de vara ativado")

            # DEBUG ADICIONAL
            print(f"🔧 [DEBUG] fishing_engine.chest_coordinator? {self.fishing_engine.chest_coordinator is not None}")
            print(f"🔧 [DEBUG] fishing_engine.rod_manager? {self.fishing_engine.rod_manager is not None}")

            success = self.fishing_engine.trigger_rod_maintenance()
            if success:
                print("✅ [PAGE DOWN] Manutenção de vara executada com sucesso")
            else:
                print("❌ [PAGE DOWN] Falha na manutenção de vara")
        else:
            print("⚠️ [PAGE DOWN] FishingEngine não disponível")
    except Exception as e:
        print(f"❌ [PAGE DOWN] Erro no trigger de manutenção: {e}")
        import traceback
        traceback.print_exc()
```

Isso vai imprimir MUITO mais detalhes para identificar o problema!