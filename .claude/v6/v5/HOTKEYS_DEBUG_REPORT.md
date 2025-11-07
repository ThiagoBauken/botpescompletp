# 🔧 Relatório de Debug - Problema das Hotkeys F9→TAB

## 🐛 Problema Identificado

**Sintoma**: Pressionar F9 executa função de TAB (troca de vara) ao invés de iniciar o bot

**Log Original**:
```
🔧 [TAB] Trigger manual de troca de vara ativado
==================================================
🔄 TROCA DE VARA INTELIGENTE - BASEADA NO V3
==================================================
```

## 🔍 Diagnóstico Realizado

### 1. Verificação do Mapeamento de Hotkeys ✅
- **Configuração**: F9 → `start_bot` está corretamente mapeada
- **Local**: `ui/main_window.py` linha 383
- **Status**: ✅ Configuração correta no código

### 2. Verificação do Método `start_bot` ✅
- **Existe**: ✅ Método existe em `main_window.py` linha 3161
- **Acessível**: ✅ Método público e acessível
- **Logs**: ✅ Adicionados logs de debug para rastreamento

### 3. Verificação do FishingEngine ✅
- **Método start()**: ✅ Existe e implementado
- **Validação**: ✅ Adicionados logs para debug de dependências
- **Thread**: ✅ Sistema de threading implementado

## 🔧 Correções Implementadas

### 1. **Limpeza de Hotkeys Conflitantes**
```python
# Limpar hotkeys existentes primeiro
try:
    keyboard.clear_all_hotkeys()
    print("🧹 Hotkeys anteriores limpas")
except Exception as e:
    print(f"⚠️ Erro ao limpar hotkeys: {e}")
```

### 2. **Logs de Debug Expandidos**
```python
def start_bot(self):
    print("🔧 [F9] start_bot() chamado - iniciando bot...")
    # ... resto do método
```

```python
print(f"  ✅ {hotkey.upper()}: {description} -> {method_name}")
if hotkey == 'f9':
    print(f"      🔍 F9 especialmente mapeado para: {method}")
```

### 3. **Tecla Alternativa F8**
```python
hotkeys_config = {
    'f8': ('start_bot', "🚀 Iniciar bot"),  # Temporariamente mudado de F9 para F8
    'f9': ('start_bot', "🚀 Iniciar bot"),  # Manter F9 também para teste
    # ...
}
```

### 4. **Debug do FishingEngine**
```python
print("🔍 Validando dependências...")
if not self._validate_dependencies():
    print("❌ Falha na validação de dependências")
    # ...
print("✅ Dependências validadas com sucesso")
```

## 🧪 Ferramentas de Debug Criadas

### 1. **test_hotkeys.py**
- Teste isolado de captura de teclas F9, TAB, F1
- Contador de chamadas para cada tecla
- Timeout automático de 30 segundos

### 2. **Logs Detalhados**
- Rastreamento de registro de hotkeys
- Debug de chamadas de métodos
- Validação de dependências do FishingEngine

## 🎯 Possíveis Causas do Problema

### 1. **Conflito de Hotkeys** (MAIS PROVÁVEL)
- Outro processo/aplicação capturando F9
- Hotkeys registradas em duplicata
- Conflito com sistema operacional

### 2. **Falha Silenciosa do start_bot**
- FishingEngine.start() falhando sem logs
- Dependências não validadas
- Thread não inicializando

### 3. **Problema na Biblioteca keyboard**
- Bug na captura de F9 especificamente
- Conflito com outras bibliotecas
- Problema de permissions

## ✅ Próximos Passos de Teste

### 1. **Testar F8 ao invés de F9**
```bash
# Executar bot e testar:
# - F8 para iniciar bot (deve funcionar)
# - F9 para iniciar bot (comparar comportamento)
```

### 2. **Executar test_hotkeys.py**
```bash
cd fishing_bot_v4
python test_hotkeys.py
# Pressionar F9, TAB, F1 e verificar contadores
```

### 3. **Verificar Logs de Inicialização**
```bash
# Observar saída durante inicialização:
# - "🔍 F9 especialmente mapeado para: <bound method>"
# - "🔧 [F9] start_bot() chamado - iniciando bot..."
```

## 📊 Status Atual

- ✅ **Diagnóstico**: Completo com logs e ferramentas
- ⏳ **Solução**: F8 como alternativa temporária
- 🔄 **Teste**: Aguardando feedback do usuário

## 🎯 Solução Recomendada

1. **Teste imediato**: Use **F8** ao invés de F9 para iniciar o bot
2. **Debug**: Execute `test_hotkeys.py` para isolar o problema
3. **Logs**: Observe logs detalhados para identificar falhas
4. **Correção final**: Baseada nos resultados dos testes

---

**Atualizado**: $(date)  
**Status**: 🔧 EM DEBUG ATIVO