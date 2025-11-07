# 🐛 Bugs Corrigidos - Alimentação e Limpeza

**Data:** 2025-10-29
**Problema:** F9 não acionou alimentação nem limpeza após capturar peixe

---

## 🔴 CAUSA RAIZ

Dois erros no `DetectionHandler` **bloqueavam** completamente os comandos do servidor:

### Erro #1: Parâmetro Incorreto
```python
# ❌ ERRADO (linha 64, 74):
food_result = self.template_engine.detect_template("filefrito", confidence=0.75)
eat_result = self.template_engine.detect_template("eat", confidence=0.75)

# ✅ CORRETO:
food_result = self.template_engine.detect_template("filefrito", confidence_threshold=0.75)
eat_result = self.template_engine.detect_template("eat", confidence_threshold=0.75)
```

**Resultado:** `TypeError: got an unexpected keyword argument 'confidence'`

---

### Erro #2: Método Inexistente
```python
# ❌ ERRADO (linha 111):
results = self.template_engine.detect_multiple_instances(...)

# ✅ CORRETO:
# Implementado scan manual com cv2.matchTemplate
```

**Resultado:** `AttributeError: 'TemplateEngine' object has no attribute 'detect_multiple_instances'`

---

## 📋 FLUXO DO ERRO (Logs Reais)

```
1. 🐟 Cliente capturou peixe #1
   └─> 📤 Envia "fish_caught" ao servidor

2. 🖥️ Servidor processa:
   - ✅ Contador: 0 → 1 peixe
   - ✅ Verifica: should_feed() = True (a cada 1 peixe)
   - ✅ Verifica: should_clean() = True (a cada 1 peixe)
   - ✅ Envia: "request_template_detection" (feeding)
   - ✅ Envia: "request_inventory_scan" (cleaning)

3. 💻 Cliente tenta processar:
   - ❌ ERRO: confidence (TypeError)
   - ❌ ERRO: detect_multiple_instances (AttributeError)
   - ❌ RESULTADO: Nenhum dado retornado ao servidor

4. 🖥️ Servidor aguarda resposta:
   - ⏳ Espera 2 segundos...
   - ❌ Nenhuma resposta do cliente
   - 📋 Conclusão: "will_open_chest = False"

5. 💻 Cliente decide:
   - ℹ️ Servidor não pediu nada
   - 🔄 Trocar vara e continuar pescando
```

---

## ✅ CORREÇÕES APLICADAS

### 1. Corrigido Parâmetro `confidence_threshold`
**Arquivo:** `client/detection_handler.py:64, 74`

```diff
- food_result = self.template_engine.detect_template("filefrito", confidence=0.75)
+ food_result = self.template_engine.detect_template("filefrito", confidence_threshold=0.75)

- eat_result = self.template_engine.detect_template("eat", confidence=0.75)
+ eat_result = self.template_engine.detect_template("eat", confidence_threshold=0.75)
```

---

### 2. Implementado Scan Manual com OpenCV
**Arquivo:** `client/detection_handler.py:107-140`

```python
# Capturar screenshot uma vez
screenshot = self.template_engine.capture_screen()

# Importar OpenCV
import cv2
import numpy as np

# Para cada tipo de peixe
for template_name in fish_templates:
    template = self.template_engine.template_cache[template_name.lower()]

    # Match template (detecta MÚLTIPLAS instâncias)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # Threshold 0.7
    locations = np.where(result >= 0.7)

    # Adicionar todas as detecções
    for pt in zip(*locations[::-1]):
        x = pt[0] + template.shape[1] // 2
        y = pt[1] + template.shape[0] // 2
        all_detections.append((x, y))
```

**Vantagem:** Detecta MÚLTIPLOS peixes do mesmo tipo (ex: 5 salmões)

---

## 🧪 COMO TESTAR

### 1. Iniciar Servidor
```bash
cd server
python server.py
```

Verificar: Sem erros de inicialização

---

### 2. Configurar Cliente para Teste Rápido
Na interface:
- **Alimentação:** A cada **1 peixe**
- **Limpeza:** A cada **1 peixe**

---

### 3. Apertar F9 e Capturar 1 Peixe

**Fluxo Esperado:**
```
🐟 Peixe #1 capturado
📤 Enviando ao servidor...
🖥️ Servidor: should_feed() = True, should_clean() = True
📥 Cliente recebe: request_template_detection
📥 Cliente recebe: request_inventory_scan
🔍 Cliente detecta comida: ✅ (sem erro de confidence)
🔍 Cliente escaneia inventário: ✅ (sem erro de detect_multiple_instances)
📤 Cliente envia coordenadas ao servidor
🖥️ Servidor constrói sequence de feeding
🖥️ Servidor constrói sequence de cleaning
📥 Cliente recebe: execute_sequence (feeding)
⚡ Cliente executa: Abre baú → Pega comida → Come → Fecha
📥 Cliente recebe: execute_sequence (cleaning)
⚡ Cliente executa: Abre baú → Transfere peixes → Fecha
```

---

### 4. Logs do Cliente (Esperado)

```
🐟 Peixe #1 capturado!
📤 Notificando servidor...

🔍 [SERVER→CLIENT] COMANDO REQUEST_TEMPLATE_DETECTION RECEBIDO
🔍 Detectando comida e botão eat...
   ✅ Comida detectada em (1306, 858)     ← SEM ERRO!
   ✅ Botão eat detectado em (1083, 373)  ← SEM ERRO!
📤 Enviando coordenadas ao servidor...

🔍 [SERVER→CLIENT] COMANDO REQUEST_INVENTORY_SCAN RECEBIDO
🔍 Escaneando inventário...
   🐟 SALMONN encontrado em (709, 700)    ← SEM ERRO!
   🐟 shark encontrado em (805, 700)
   📊 Total de detecções antes de NMS: 2
   📊 Após NMS: 2 peixes únicos           ← SEM ERRO!
📤 Enviando localizações ao servidor...

🔍 [SERVER→CLIENT] COMANDO EXECUTE_SEQUENCE RECEBIDO
⚡ Executando sequência: feeding (15 ações)
   ✅ Baú aberto
   ✅ Comida transferida
   ✅ Comido 2x
   ✅ Baú fechado

🔍 [SERVER→CLIENT] COMANDO EXECUTE_SEQUENCE RECEBIDO
⚡ Executando sequência: cleaning (8 ações)
   ✅ Baú aberto
   ✅ 2 peixes transferidos
   ✅ Baú fechado
```

---

### 5. Logs do Servidor (Esperado)

```
🐟 thiago: Peixe #1 capturado!
✅ thiago: should_feed() = True (trigger: fish_per_feed)
✅ thiago: should_clean() = True (trigger: clean_interval)
📤 Solicitando detecção de comida...
📤 Solicitando scan de inventário...

📥 thiago: Localizações de feeding recebidas
   Food: (1306, 858), Eat: (1083, 373)
✅ thiago: Sequência de feeding enviada (15 ações)

📥 thiago: 2 peixes detectados
✅ thiago: Sequência de cleaning enviada (8 ações)

✅ thiago: Sequência feeding concluída com sucesso
✅ thiago: Sequência cleaning concluída com sucesso
```

---

## 🎯 IMPACTO

**Antes (❌):**
- Cliente recebia comandos do servidor
- Erros de código bloqueavam execução
- Servidor não recebia resposta
- **NENHUMA operação de baú executada**

**Depois (✅):**
- Cliente recebe comandos do servidor
- Detecção funciona corretamente
- Servidor recebe coordenadas
- **Feeding e cleaning executados automaticamente**

---

## 📚 ARQUIVOS MODIFICADOS

- ✅ `client/detection_handler.py` (linhas 64, 74, 107-140)

---

## ⚠️ NOTAS TÉCNICAS

### Por que o scan não detectou múltiplos antes?

O método `detect_template()` do TemplateEngine retorna **apenas 1 resultado** (o melhor match). Para inventário com múltiplos peixes do mesmo tipo, precisamos de `cv2.matchTemplate` + threshold, que retorna **TODAS as localizações** acima da confiança.

### NMS (Non-Maximum Suppression)

O `_apply_nms()` remove detecções duplicadas (threshold: 50px). Isso evita contar o mesmo peixe 2x se ele tiver overlap de templates.

---

**Status:** ✅ PRONTO PARA TESTE
**Próximo Passo:** Apertar F9 e capturar 1 peixe para verificar
