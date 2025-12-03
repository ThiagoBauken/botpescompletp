# Soluções para Problemas no PC dele

## Resumo dos 3 Problemas

| # | Problema | Causa | Solução |
|---|----------|-------|---------|
| 1 | Arduino não reconecta após reiniciar | Port não era salvo na config | ✅ CORRIGIDO - Agora salva e reconecta automaticamente |
| 2 | Baú left/right bugado e não vai para baixo | Valores inadequados + sem normalização | ✅ CORRIGIDO - Normaliza side + logs detalhados |
| 3 | Só guarda shark, não detecta outros peixes | Templates faltando ou confiança muito alta | ✅ Script de teste criado |

---

## Problema 1: Arduino não reconecta ✅ RESOLVIDO

### O que foi feito:

**Arquivo**: [arduino_input_manager.py](core/arduino_input_manager.py)

**Correção 1** (linha 203-210): Salvar port após conexão
```python
if self._ping():
    self.connected = True
    # ✅ NOVO: Salvar porta na config
    if self.config_manager:
        self.config_manager.set('arduino_port', self.port)
        self.config_manager.save_config()
        print(f"💾 Porta {self.port} salva para reconexão automática")
```

**Correção 2** (linha 104-113): Tentar reconectar no __init__
```python
# ✅ NOVO: Tentar reconectar automaticamente ao último port usado
if self.port:
    print(f"🔄 Tentando reconectar ao último Arduino usado ({self.port})...")
    if self._connect():
        print(f"✅ Reconectado automaticamente ao {self.port}")
```

### Como testar:
1. Conectar Arduino pela primeira vez
2. Fechar o bot
3. Abrir o bot novamente
4. Deve reconectar automaticamente em 2-3 segundos

---

## Problema 2: Baú left/right bugado ✅ RESOLVIDO

### O que foi feito:

**Arquivo**: [chest_manager.py](core/chest_manager.py:168-208)

**Correção 1**: Normalização de idioma (left/esquerda)
```python
# Aceita português e inglês
side_normalized = side.lower().strip()
if side_normalized in ['left', 'esquerda', 'esq', 'l']:
    side_normalized = 'left'
elif side_normalized in ['right', 'direita', 'dir', 'r']:
    side_normalized = 'right'
```

**Correção 2**: Garantir movimento vertical para baixo
```python
dy = vertical_offset if vertical_offset > 0 else abs(vertical_offset)
```

**Correção 3**: Avisos de valores inadequados
```python
if abs(dx) < 100:
    print(f"⚠️ Distance muito pequena: {abs(dx)}px (recomendado: 200-400px)")
if dy < 100:
    print(f"⚠️ Vertical offset muito pequeno: {dy}px (recomendado: 150-300px)")
```

**Correção 4**: Logs visuais com setas
```python
print(f"   Horizontal (DX): {dx:+d} ({'←esquerda' if dx > 0 else '→direita'})")
print(f"   Vertical (DY): {dy:+d} ({'↓baixo' if dy > 0 else '↑cima'})")
```

### Como ajustar para o PC dele:

**1. Valores iniciais recomendados** (`config.json`):
```json
{
  "chest_side": "left",
  "chest_distance": 300,
  "chest_vertical_offset": 200
}
```

**2. Se não funcionar, aumentar**:
```json
{
  "chest_distance": 400,
  "chest_vertical_offset": 250
}
```

**3. Se sensibilidade do mouse ALTA no jogo**:
```json
{
  "chest_distance": 200,
  "chest_vertical_offset": 150
}
```

### Teste manual:
1. Abrir jogo
2. Segurar ALT
3. Mover mouse ~300px para esquerda
4. Mover mouse ~200px para baixo
5. Pressionar E
6. Baú deve abrir!

---

## Problema 3: Só detecta shark ⚠️ PRECISA TESTAR

### Causas possíveis:

1. **Templates de peixe faltando**
   - Arquivos .png não existem no PC dele
   - Solução: Copiar pasta `templates/` inteira

2. **Confiança muito alta**
   - Templates configurados com threshold > 0.9
   - Solução: Reduzir para 0.70-0.75

3. **Qualidade diferente**
   - Jogo dele tem gráficos diferentes
   - Solução: Capturar novos templates

4. **Resolução diferente**
   - Não é 1920x1080
   - Solução: Ajustar resolução do jogo

### Script de teste criado:

**Arquivo**: [test_fish_detection.py](test_fish_detection.py)

**Como usar**:
```cmd
python test_fish_detection.py
```

**O que ele faz**:
1. ✅ Verifica quais templates existem
2. ✅ Verifica se confiança está adequada
3. ✅ Teste prático com tela ao vivo
4. ✅ Recomendações específicas

### Soluções rápidas:

**Solução 1**: Reduzir confiança de TODOS os peixes

Editar `config/default_config.json`:
```json
{
  "template_confidence": {
    "SALMONN": 0.75,      // Era 0.91
    "TROUTT": 0.75,       // Era 0.91
    "sardine": 0.70,      // Era 0.75
    "anchovy": 0.70,      // Era 0.72
    "yellowperch": 0.70,  // Era 0.71
    "herring": 0.70,      // Era 0.75
    "shark": 0.70,        // Era 0.75
    "catfish": 0.70,      // Era 0.75
    "roughy": 0.70        // Era 0.75
  }
}
```

**Solução 2**: Copiar pasta templates/ inteira

Do seu PC:
```
C:\Users\Thiago\Desktop\v5\templates\
```

Para o PC dele:
```
C:\[onde está o bot]\templates\
```

**Solução 3**: Aumentar logs de debug

Adicionar no início de `inventory_manager.py`:
```python
# Ver TODOS os peixes sendo detectados ou não
```

---

## Dependências Necessárias

### Visual C++ Redistributable ⚠️ CRÍTICO

**Problema**: Sem isso, numpy/opencv não funcionam!

**Download**:
- [VC++ 2015-2022 x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- [VC++ 2015-2022 x86](https://aka.ms/vs/17/release/vc_redist.x86.exe)
- [VC++ 2013 x64](https://aka.ms/highdpimfc2013x64enu)
- [VC++ 2013 x86](https://aka.ms/highdpimfc2013x86enu)

**Teste**:
```cmd
dir "C:\Windows\System32\vcruntime*.dll"
```

Deve listar vários arquivos!

### Resolução de Tela

**Recomendado**: 1920x1080

**Verificar**:
```cmd
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
```

---

## Checklist Completo

### No PC dele, verificar:

- [ ] Visual C++ Redistributable instalado (x64 e x86)
- [ ] Resolução: 1920x1080
- [ ] Pasta `templates/` completa (copiar do seu PC)
- [ ] Arduino conecta automaticamente após correção
- [ ] Config do baú ajustada:
  - [ ] `chest_side`: testado
  - [ ] `chest_distance`: ajustado
  - [ ] `chest_vertical_offset`: ajustado
- [ ] Executar `test_fish_detection.py`
- [ ] Reduzir confiança dos templates se necessário

### Comandos rápidos:

```cmd
REM 1. Verificar VC++
dir "C:\Windows\System32\vcruntime*.dll"

REM 2. Verificar resolução
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution

REM 3. Testar detecção de peixes
python test_fish_detection.py

REM 4. Ver logs em tempo real
type data\logs\fishing_bot_*.log
```

---

## Arquivos Criados

Novos arquivos de documentação:

1. **[REQUISITOS_SISTEMA.md](REQUISITOS_SISTEMA.md)**
   - Lista completa de dependências
   - Instalação passo a passo
   - Troubleshooting

2. **[EXPLICACAO_MACRO_BAU.md](EXPLICACAO_MACRO_BAU.md)**
   - Como funciona macro left/right
   - Onde ficam os arquivos
   - Como ajustar valores

3. **[test_fish_detection.py](test_fish_detection.py)**
   - Script de teste de detecção
   - Verifica templates
   - Teste prático

4. **[SOLUCOES_PROBLEMAS_PC_DELE.md](SOLUCOES_PROBLEMAS_PC_DELE.md)** (este arquivo)
   - Resumo de todos os problemas
   - Soluções aplicadas
   - Checklist completo

---

## Suporte

Se ainda não funcionar, coletar estas informações:

1. **Screenshot dos logs** quando:
   - Arduino conectar (ou não)
   - Tentar abrir baú (F6)
   - Executar limpeza

2. **Resultado de**:
   ```cmd
   python test_fish_detection.py
   ```

3. **Configuração atual**:
   - Conteúdo de `data/config.json`
   - Conteúdo de `config/default_config.json`

4. **Sistema**:
   ```cmd
   wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
   dir "C:\Windows\System32\vcruntime*.dll"
   dir templates\*.png
   ```

---

## Commits

Todas as correções foram commitadas:

```
39c446c - fix: Arduino auto-reconnect e corrigir chest side left/right
```

**Arquivos modificados**:
- `core/arduino_input_manager.py` (+31 linhas)
- `core/chest_manager.py` (+37 linhas)

**Arquivos criados**:
- `REQUISITOS_SISTEMA.md`
- `EXPLICACAO_MACRO_BAU.md`
- `test_fish_detection.py`
- `SOLUCOES_PROBLEMAS_PC_DELE.md`
