# 🔍 DEBUG: Problema chest_side abrindo sempre na direita

## 🐛 Problema Reportado

> **Usuário:** "voce editou algo que deu problema antes alternava entre esquerda e direita so dava problema ao salvar um e reiniciar ai meio que trocava os polos, porem agora tudo abre na direita mesmo estando configurado esquerda"

**Status:** Config.json tem `"chest_side": "left"` mas baú abre na DIREITA

---

## ✅ Logs de Debug Adicionados

### Arquivo: `core/chest_operation_coordinator.py`

**Linha 483-487:** Debug de leitura
```python
# ✅ DEBUG CRÍTICO: Mostrar EXATAMENTE o que foi lido
_safe_print(f"\n🔍 [DEBUG] ConfigManager.get('chest_side') retornou: '{chest_side}' (tipo: {type(chest_side).__name__})")
_safe_print(f"🔍 [DEBUG] Comparação: chest_side == 'left' ? {chest_side == 'left'}")
_safe_print(f"🔍 [DEBUG] Comparação: chest_side == 'right' ? {chest_side == 'right'}")
_safe_print(f"Config: lado={chest_side}, distância={chest_distance}px")
```

**Linha 547-556:** Debug de movimento
```python
# ✅ DEBUG: Mostrar decisão
_safe_print(f"   🔍 [DEBUG] chest_side atual: '{chest_side}'")

if chest_side == 'left':
    delta_x = -chest_distance  # Movimento para esquerda (NEGATIVO)
    _safe_print(f"   ✅ [DEBUG] Detectado 'left' → delta_x = {delta_x} (NEGATIVO = esquerda)")
else:
    delta_x = chest_distance   # Movimento para direita (POSITIVO)
    _safe_print(f"   ⚠️ [DEBUG] NÃO detectado 'left', usando direita → delta_x = {delta_x} (POSITIVO = direita)")

_safe_print(f"   Deslocamento final: {delta_x}px horizontal")
```

---

## 🧪 Como Testar e Ver o Problema

```bash
cd C:\Users\Thiago\Desktop\v5
python main.py
```

### Teste 1: Feeding (F6)

**Passos:**
1. Verificar `data/config.json` - deve ter `"chest_side": "left"`
2. Pressionar `F6` (feeding)

**Logs esperados (SE ESTIVER FUNCIONANDO):**
```
📦 ABRINDO BAÚ...

🔍 [DEBUG] ConfigManager.get('chest_side') retornou: 'left' (tipo: str)
🔍 [DEBUG] Comparação: chest_side == 'left' ? True
🔍 [DEBUG] Comparação: chest_side == 'right' ? False
Config: lado=left, distância=1200px

[3/5] Calculando movimento da câmera...
   🔍 [DEBUG] chest_side atual: 'left'
   ✅ [DEBUG] Detectado 'left' → delta_x = -1200 (NEGATIVO = esquerda)
   Deslocamento final: -1200px horizontal

[4/5] Movendo câmera via Arduino...
   Movimento: DX=-1200, DY=200
```

**Logs esperados (SE ESTIVER COM BUG):**
```
📦 ABRINDO BAÚ...

🔍 [DEBUG] ConfigManager.get('chest_side') retornou: 'right' (tipo: str)
🔍 [DEBUG] Comparação: chest_side == 'left' ? False
🔍 [DEBUG] Comparação: chest_side == 'right' ? True
Config: lado=right, distância=1200px

[3/5] Calculando movimento da câmera...
   🔍 [DEBUG] chest_side atual: 'right'
   ⚠️ [DEBUG] NÃO detectado 'left', usando direita → delta_x = 1200 (POSITIVO = direita)
   Deslocamento final: 1200px horizontal

[4/5] Movendo câmera via Arduino...
   Movimento: DX=1200, DY=200
```

---

## 🎯 O Que Procurar nos Logs

### Cenário 1: ConfigManager retorna valor errado

Se os logs mostrarem:
```
🔍 [DEBUG] ConfigManager.get('chest_side') retornou: 'right'
```

**Mas config.json tem "left"**, então o problema é:
- ❌ ConfigManager não está lendo do arquivo correto
- ❌ Há um cache ou valor default sobrescrevendo
- ❌ Há outro local salvando 'right'

### Cenário 2: Comparação falha

Se os logs mostrarem:
```
🔍 [DEBUG] ConfigManager.get('chest_side') retornou: 'left'
🔍 [DEBUG] Comparação: chest_side == 'left' ? False  ← ❌ BUG!
```

**Então o problema é:**
- ❌ Espaços extras: `'left '` vs `'left'`
- ❌ Codificação diferente
- ❌ Tipo diferente (não é string)

### Cenário 3: Movimento invertido

Se os logs mostrarem:
```
✅ [DEBUG] Detectado 'left' → delta_x = -1200
```

**Mas baú abre na DIREITA**, então:
- ❌ Movimento negativo está indo para DIREITA (lógica invertida no Arduino)
- ❌ Sistema de coordenadas invertido

---

## 📝 Próximos Passos

**APÓS RODAR O TESTE:**

1. **Copiar TODOS os logs** do console (especialmente as linhas com 🔍 [DEBUG])
2. **Enviar os logs** para identificar o problema exato
3. **Verificar** qual dos 3 cenários acima está acontecendo

---

## ✅ Status

**Debug logs:** ✅ ADICIONADOS

**Próximo passo:** 🧪 TESTAR e analisar logs

**Aguardando:** Logs do usuário para identificar causa raiz

---

**Data:** 2025-10-27
**Arquivo modificado:** `core/chest_operation_coordinator.py`
