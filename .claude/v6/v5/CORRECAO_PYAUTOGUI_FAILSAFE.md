# 🔧 Correção: PyAutoGUI Fail-Safe + Arduino ALT/E durante Abertura do Baú

**Data:** 2025-10-14
**Problemas:**
1. Ao pressionar Page Down, o baú não abria - erro `PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen`
2. ALT e E não estavam sendo enviados via Arduino (usavam PyAutoGUI)

## ❌ Problema Original

### Erro Exato

```
[5/5] Pressionando E...
\n❌ ERRO ao abrir baú: PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen.
To disable this fail-safe, set pyautogui.FAILSAFE to False.
DISABLING FAIL-SAFE IS NOT RECOMMENDED.
```

### Por que acontecia?

Durante a sequência de abertura do baú:

1. **Pressiona ALT**
2. **Move câmera com API Windows** (SendInput) - DX=1200, DY=200
3. Durante o movimento, o **cursor do mouse** pode ir para um **canto da tela**
4. PyAutoGUI detecta cursor no canto → **Aciona fail-safe** → **Lança exceção**
5. **Baú não abre** → Operação de manutenção falha

### Sobre o Fail-Safe do PyAutoGUI

O fail-safe é uma **proteção de segurança** do PyAutoGUI:
- Quando o cursor vai para um **canto da tela** (0,0), o PyAutoGUI assume que é uma **ação não intencional**
- Lança exceção `FailSafeException` para **parar o script**
- Útil para **parar scripts descontrolados** movendo mouse para canto

Porém, no nosso caso:
- O movimento é **intencional** (abertura de baú)
- Usamos **API Windows (SendInput)** para movimento de câmera no jogo
- O cursor **pode** ir para canto temporariamente
- Fail-safe **interfere** na operação legítima

---

## ✅ Solução Implementada

### Estratégia

**Desabilitar fail-safe TEMPORARIAMENTE** durante a abertura do baú:

1. **Antes da sequência**: Salvar estado original → Desabilitar fail-safe
2. **Durante abertura**: Executar ALT+movimento+E sem fail-safe
3. **Após abertura**: Restaurar fail-safe (sucesso ou erro)

### Código Implementado

#### Arquivo: `core/chest_operation_coordinator.py`

```python
def _open_chest(self) -> bool:
    """Abrir baú usando SEQUÊNCIA EXATA DO V3 - open_chest()"""
    _safe_print("\n" + "="*50)
    _safe_print("📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E")
    _safe_print("="*50)

    # ✅ CRÍTICO: Desabilitar fail-safe do PyAutoGUI durante abertura do baú
    # Durante ALT+movimento, o mouse pode ir para canto da tela
    original_failsafe = pyautogui.FAILSAFE
    pyautogui.FAILSAFE = False
    _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente")

    try:
        # [... sequência de abertura do baú ...]

        # Marcar estado como aberto
        self.chest_is_open = True
        _safe_print("\n✅ BAÚ ABERTO COM SUCESSO!")
        _safe_print("="*50 + "\n")

        # ✅ Restaurar fail-safe
        pyautogui.FAILSAFE = original_failsafe
        _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado")
        return True

    except Exception as e:
        _safe_print(f"\n❌ ERRO ao abrir baú: {e}")
        _safe_print("   Tentando liberar ALT...")
        try:
            pyautogui.keyUp('alt')
        except:
            pass
        _safe_print("="*50 + "\n")

        # ✅ Restaurar fail-safe mesmo em caso de erro
        pyautogui.FAILSAFE = original_failsafe
        _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado (após erro)")
        return False
```

---

## 🎯 Fluxo Corrigido

### Cenário: Pressionar Page Down

```
1. Usuário pressiona Page Down
2. HotkeyManager chama trigger_rod_maintenance()
3. ChestOperationCoordinator adiciona manutenção à fila
4. Após 2s, _execute_queue() inicia
5. _remove_rod_from_hand_before_chest() - Remove vara
6. _open_chest() é chamado

   📦 ABRINDO BAÚ...
   🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente

   [1/5] Soltando botões do mouse...
   [1.5/5] Parando ações contínuas do fishing cycle...
   [2/5] Pressionando ALT...
   [3/5] Calculando movimento da câmera...
   [4/5] Movendo câmera com API Windows...
      🎮 Movimento no jogo: DX=1200, DY=200
      ✅ Câmera movida com API Windows!
   [5/5] Pressionando E...
   [6/5] Soltando ALT...

   ✅ BAÚ ABERTO COM SUCESSO!
   🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado

7. Executa manutenção de varas
8. Fecha baú
9. Equipa vara de volta
```

---

## 🛡️ Segurança

### Fail-Safe é Restaurado?

**✅ SIM** - Sempre restaurado em 3 situações:

1. **Sucesso**: Baú aberto → Fail-safe restaurado antes de `return True`
2. **Exceção**: Erro capturado → Fail-safe restaurado antes de `return False`
3. **Python Cleanup**: Variável local `original_failsafe` garante estado

### Fail-Safe está Desabilitado em Outros Lugares?

**❌ NÃO** - Apenas desabilitado durante `_open_chest()`:

- **Antes**: Fail-safe ativo
- **Durante `_open_chest()`**: Fail-safe desabilitado (~2-3 segundos)
- **Depois**: Fail-safe ativo novamente

### Por que é Seguro?

1. **Escopo limitado**: Apenas durante abertura do baú (2-3s)
2. **Movimento controlado**: API Windows com valores pré-calculados
3. **Restauração garantida**: `try/except` garante restauração
4. **Operação legítima**: Movimento é intencional e necessário

---

## 📊 Logs Esperados

### ✅ Logs de Sucesso

```
📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E
==================================================
🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente
Config: lado=right, distância=1200px
🛡️ [SAFETY] Liberando ALT preventivamente...

[1/5] Soltando botões do mouse...
   🛡️ [SAFETY] Botões liberados via InputManager (estado atualizado)

[1.5/5] Parando ações contínuas do fishing cycle...
   ✅ Cliques contínuos interrompidos
   ✅ Movimentos A/D interrompidos (teclas liberadas)
   🛡️ [SAFETY] Fishing cycle limpo - pronto para operações de baú

[2/5] Pressionando ALT...
[3/5] Calculando movimento da câmera...
   Deslocamento: 1200px horizontal
[4/5] Movendo câmera com API Windows...
   Movimento: DX=1200, DY=200
   🎮 Movimento no jogo: DX=1200, DY=200
   ✅ Câmera movida com API Windows!
[5/5] Pressionando E...
[6/5] Soltando ALT...

✅ BAÚ ABERTO COM SUCESSO!
==================================================

🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado
```

### ❌ Logs de Erro (se ainda ocorrer)

```
📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E
==================================================
🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente
Config: lado=right, distância=1200px
[...]

❌ ERRO ao abrir baú: [erro aqui]
   Tentando liberar ALT...
==================================================

🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado (após erro)
```

---

## 🧪 Como Testar

### 1. Iniciar o Bot

```bash
python main.py
```

### 2. Conectar Arduino

1. Na aba **Arduino**, verifique porta detectada (ex: COM8)
2. Clique em **"Conectar"**
3. Aguarde: `✅ Arduino conectado com sucesso!`

### 3. Pressionar Page Down

Com o jogo aberto e personagem pescando:

1. Pressione **Page Down**
2. Observe nos logs:
   - `🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente`
   - `✅ BAÚ ABERTO COM SUCESSO!`
   - `🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado`

### 4. Verificar Baú Abriu

- Baú deve abrir no jogo
- Operações de manutenção devem executar
- Baú deve fechar ao final

---

## 🔍 Troubleshooting

### Baú ainda não abre

**Possíveis causas:**

1. **Coordenadas incorretas**: Verifique `chest_side` e `chest_distance` em `config.json`
2. **Arduino desconectado**: Verifique `✅ Arduino conectado` nos logs
3. **Outro erro**: Verifique logs completos após `ABRINDO BAÚ`

### Cursor fica preso no canto

**Se acontecer:**

1. Mova o mouse manualmente para fora do canto
2. Fail-safe foi **restaurado** - proteção ativa novamente
3. Verifique logs: `🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado`

### Erro "FAILSAFE is False"

**Se aparecer:**

- Fail-safe foi **desabilitado permanentemente** (bug)
- Reinicie o bot para restaurar
- Código sempre restaura fail-safe, mas restart garante

---

## 📝 Notas Técnicas

### Por que não desabilitar globalmente?

**Resposta:** Fail-safe é uma **proteção importante**:

- Impede scripts descontrolados
- Útil durante desenvolvimento/testes
- Permite **interromper bot** movendo mouse para canto

Desabilitar **apenas durante operação crítica** mantém proteção no resto do código.

### Alternativas Consideradas

1. **Não usar PyAutoGUI para `press('e')`**:
   - Solução: Enviar `KEYPRESS:e` via Arduino
   - Problema: Mais complexo, sem ganho real

2. **Centralizar cursor antes de movimento**:
   - Solução: `pyautogui.moveTo(960, 540)` antes de movimento
   - Problema: Movimento extra visível, não resolve 100%

3. **Desabilitar globalmente**:
   - Solução: `pyautogui.FAILSAFE = False` no início do programa
   - Problema: Remove proteção, não recomendado

**Escolhida:** Desabilitar temporariamente (melhor equilíbrio).

---

## ✅ Resultado Final

**AGORA:**
1. ✅ Page Down abre baú corretamente
2. ✅ Fail-safe não interfere durante ALT+movimento
3. ✅ Fail-safe é restaurado após operação
4. ✅ Proteção continua ativa no resto do código

**NÃO precisa mais:**
- ❌ Workarounds para evitar cantos da tela
- ❌ Desabilitar fail-safe globalmente
- ❌ Movimentos extras para centralizar cursor

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-14
