# 🔧 FIX: Remover Poluição de Logs (A/S/D e Mouse)

## 📊 Problema

Logs de movimentação (A/S/D) e cliques do mouse estão poluindo o console:

```
   🔼 [KEY_UP] Tentando soltar 'a'...
   📊 [KEY_UP] Estado atual: {'a', 'alt'}
   🔓 [KEY_UP] 'a' está em force_release_keys - SEMPRE solta!
   📤 [KEY_UP] Enviando comando: KEY_UP:a
   📥 [KEY_UP] Resposta: OK:KEY_UP:a
   🗑️  [KEY_UP] Removido 'a' do state
   ✅ [KEY_UP] 'a' SOLTO com sucesso!
🎯 [REL] Pressionando botão left (Mouse relativo)...
✅ [REL] Botão left pressionado (SEM drift!)
🎯 [REL] Soltando botão left (Mouse relativo)...
✅ [REL] Botão left solto
```

**Quantidade:** ~100 linhas por ciclo de pesca!

## ✅ Solução: Adicionar Flag de Verbosidade

### Opção 1: Remover Completamente (SIMPLES)

Comentar os logs verbosos em `arduino_input_manager.py`.

**Vantagens:**
- ✅ Rápido (5 minutos)
- ✅ Efetivo imediatamente
- ✅ Console limpo

**Desvantagens:**
- ❌ Perde informação de debug
- ❌ Difícil diagnosticar problemas futuros

### Opção 2: Sistema de Verbosidade (RECOMENDADO)

Adicionar configuração `input_logging_verbosity` em `config.json`:

```json
{
  "input_logging": {
    "verbosity": "minimal",  // "off", "minimal", "normal", "debug"
    "log_to_file": true,     // Se true, salva em data/logs/input_ops.log
    "show_on_console": false // Se true, mostra no console também
  }
}
```

**Vantagens:**
- ✅ Flexível
- ✅ Mantém logs em arquivo para debug
- ✅ Console limpo
- ✅ Pode re-habilitar quando necessário

**Desvantagens:**
- ❌ Mais código para implementar (~30 minutos)

### Opção 3: Remover Apenas Logs de Movimento (INTERMEDIÁRIO)

Manter logs de:
- ✅ Abertura/fechamento de baú
- ✅ Troca de vara
- ✅ Detecção de peixe

Remover logs de:
- ❌ A/S/D individuais
- ❌ Mouse down/up individuais
- ❌ KEY_UP/KEY_DOWN individuais

**Vantagens:**
- ✅ Rápido (~10 minutos)
- ✅ Mantém logs importantes
- ✅ Remove poluição

## 🔧 Implementação: Opção 3 (RECOMENDADO PARA AGORA)

### Passo 1: Identificar Logs Verbosos

**Arquivo:** `arduino_input_manager.py`

**Linhas para comentar/remover:**

```python
# key_up() - linhas 450-487
_safe_print(f"   🔼 [KEY_UP] Tentando soltar '{key_normalized}'...")  # ← REMOVER
_safe_print(f"   📊 [KEY_UP] Estado atual: {self.keyboard_state['keys_down']}")  # ← REMOVER
_safe_print(f"   🔓 [KEY_UP] '{key_normalized}' está em force_release_keys - SEMPRE solta!")  # ← REMOVER
_safe_print(f"   📤 [KEY_UP] Enviando comando: KEY_UP:{key_normalized}")  # ← REMOVER
_safe_print(f"   📥 [KEY_UP] Resposta: {response}")  # ← REMOVER
_safe_print(f"   🗑️  [KEY_UP] Removido '{key_normalized}' do state")  # ← REMOVER
_safe_print(f"   ✅ [KEY_UP] '{key_normalized}' SOLTO com sucesso!")  # ← REMOVER

# key_down() - linhas 380-420 (similar)
_safe_print(f"   🔽 [KEY_DOWN] Tentando pressionar '{key_normalized}'...")  # ← REMOVER
_safe_print(f"   📊 [KEY_DOWN] Estado atual: {self.keyboard_state['keys_down']}")  # ← REMOVER
_safe_print(f"   📤 [KEY_DOWN] Enviando comando: KEY_DOWN:{key_normalized}")  # ← REMOVER
_safe_print(f"   📥 [KEY_DOWN] Resposta: {response}")  # ← REMOVER
_safe_print(f"   ✅ [KEY_DOWN] '{key_normalized}' PRESSIONADO com sucesso!")  # ← REMOVER

# mouse_down_relative() - linhas 710-720
_safe_print(f"🎯 [REL] Pressionando botão {button} (Mouse relativo)...")  # ← MANTER (importante)
_safe_print(f"   📤 Comando: MOUSE_DOWN_REL:{button}")  # ← REMOVER
_safe_print(f"   📥 Resposta: {response}")  # ← REMOVER
_safe_print(f"✅ [REL] Botão {button} pressionado (SEM drift!)")  # ← SIMPLIFICAR

# mouse_up_relative() - linhas 730-740
_safe_print(f"🎯 [REL] Soltando botão {button} (Mouse relativo)...")  # ← MANTER
_safe_print(f"   📤 Comando: MOUSE_UP_REL:{button}")  # ← REMOVER
_safe_print(f"   📥 Resposta: {response}")  # ← REMOVER
_safe_print(f"✅ [REL] Botão {button} solto")  # ← SIMPLIFICAR
```

### Passo 2: Criar Versão Simplificada

**Antes:**
```python
def key_up(self, key: str) -> bool:
    key_normalized = key.lower()

    _safe_print(f"   🔼 [KEY_UP] Tentando soltar '{key_normalized}'...")
    _safe_print(f"   📊 [KEY_UP] Estado atual: {self.keyboard_state['keys_down']}")
    # ... 10 linhas de logs ...
    _safe_print(f"   ✅ [KEY_UP] '{key_normalized}' SOLTO com sucesso!")

    return success
```

**Depois:**
```python
def key_up(self, key: str) -> bool:
    key_normalized = key.lower()

    # ✅ Log silencioso - apenas erros críticos
    response = self._send_command(f"KEY_UP:{key_normalized}", timeout=1.0)
    success = response and "OK" in response

    if not success:
        _safe_print(f"❌ [KEY_UP] FALHA ao soltar '{key_normalized}'! Resposta: {response}")

    return success
```

### Passo 3: Logs Mantidos (Importantes)

**MANTER estes logs (são importantes):**

```python
# Abertura de baú
_safe_print("📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E")

# Troca de vara
_safe_print(f"🎣 Equipando vara do slot {slot}...")

# Detecção de peixe
_safe_print("🐟 PEIXE CAPTURADO!")

# Erros críticos
_safe_print(f"❌ Arduino desconectado! Tentando reconectar...")
```

## 📊 Resultado Esperado

### Console ANTES (poluído):
```
🎯 [REL] Pressionando botão left (Mouse relativo)...
   📤 Comando: MOUSE_DOWN_REL:left
   📥 Resposta: OK:MOUSE_DOWN_REL:left
✅ [REL] Botão left pressionado (SEM drift!)
   🔼 [KEY_UP] Tentando soltar 'a'...
   📊 [KEY_UP] Estado atual: {'a', 'alt'}
   🔓 [KEY_UP] 'a' está em force_release_keys - SEMPRE solta!
   📤 [KEY_UP] Enviando comando: KEY_UP:a
   📥 [KEY_UP] Resposta: OK:KEY_UP:a
   🗑️  [KEY_UP] Removido 'a' do state
   ✅ [KEY_UP] 'a' SOLTO com sucesso!
🎯 [REL] Pressionando botão left (Mouse relativo)...
   📤 Comando: MOUSE_DOWN_REL:left
   📥 Resposta: OK:MOUSE_DOWN_REL:left
✅ [REL] Botão left pressionado (SEM drift!)
[... 90 linhas similares ...]
```

### Console DEPOIS (limpo):
```
🎣 Iniciando pesca...
⚡ FASE 2: Fase rápida (7.65s de cliques)...
🐢 FASE 3: Iniciando fase lenta (A/D + S em ciclo + cliques)...
🐟 PEIXE CAPTURADO!
📦 Abrindo baú para feeding...
✅ Feeding concluído (2/2 foods)
🎣 Equipando vara do slot 2...
✅ Ciclo de pesca concluído
```

## 🚀 Implementação Rápida (5 minutos)

Vou criar um script que comenta automaticamente os logs verbosos:

```python
# reduce_input_logs.py
import re

# Ler arquivo
with open('core/arduino_input_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Padrões para comentar
patterns_to_comment = [
    r'_safe_print\(f"   🔼 \[KEY_UP\]',
    r'_safe_print\(f"   🔽 \[KEY_DOWN\]',
    r'_safe_print\(f"   📊 \[KEY_',
    r'_safe_print\(f"   🔓 \[KEY_',
    r'_safe_print\(f"   📤 \[KEY_',
    r'_safe_print\(f"   📥 \[KEY_',
    r'_safe_print\(f"   🗑️  \[KEY_',
    r'_safe_print\(f"   ✅ \[KEY_UP\] .* SOLTO com sucesso',
    r'_safe_print\(f"   ✅ \[KEY_DOWN\] .* PRESSIONADO com sucesso',
    r'_safe_print\(f"   📤 Comando: MOUSE_',
    r'_safe_print\(f"   📥 Resposta: \{response\}"',
]

# Comentar linhas que correspondem aos padrões
for pattern in patterns_to_comment:
    content = re.sub(
        f'^(\\s*)({pattern}.*?)$',
        r'\1# \2  # ← Log verboso desabilitado',
        content,
        flags=re.MULTILINE
    )

# Salvar
with open('core/arduino_input_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Logs verbosos comentados!")
```

## ⚠️ IMPORTANTE: Backup

Antes de aplicar, fazer backup:

```bash
cd C:\Users\Thiago\Desktop\v5
copy core\arduino_input_manager.py core\arduino_input_manager.py.backup
```

## 🎯 Alternativa Simples: Editar Manualmente

Se preferir, posso editar o arquivo diretamente removendo os logs verbosos.

**Quer que eu:**
1. ✅ Crie o script `reduce_input_logs.py` e execute automaticamente?
2. ✅ Edite manualmente o `arduino_input_manager.py`?
3. ✅ Apenas mostre quais linhas comentar e você edita?

---

**Recomendação:** Opção 2 (edição manual) é mais segura e rápida!
