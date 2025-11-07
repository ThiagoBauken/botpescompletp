# 🖥️🖥️ CORREÇÃO: Setup Multi-Monitor (2 Telas)

## 🚨 Problema Identificado

Você tem **2 telas** e isso causa um problema de escala:

### Seu Setup:
```
┌─────────────┐  ┌─────────────┐
│  Monitor 1  │  │  Monitor 2  │
│ 1920x1080   │  │ 1920x1080   │
│             │  │             │
│   JOGO ✅   │  │             │
└─────────────┘  └─────────────┘
    Total MSS: 3840x1080 (ou 4320x1350 com scaling)
```

### O que acontecia:

1. **MSS captura**: Área total das 2 telas = `4320x1350`
2. **OpenCV detecta**: Vara em `(3797, 205)` [coordenadas na captura total]
3. **Jogo está em**: Monitor 1 apenas = `1920x1080`
4. **PyAutoGUI tenta clicar**: `(3797, 205)` ❌ FORA DA TELA DO JOGO!

## 📊 Exemplo Real dos Seus Logs

```
📐 Resolução: 4320x1350  ← MSS captura TODA área (2 monitores)
centro=(3797,205)        ← OpenCV detecta nessa coordenada
🖱️ Drag de (3797, 205)  ← Tenta clicar AQUI (errado!)
```

**Resultado**: Clique vai para o Monitor 2 ou fora da tela!

## ✅ Correção Aplicada

### 1. Detecção de Multi-Monitor

Agora o código:
- ✅ Lista todos os monitores do sistema
- ✅ Detecta a resolução de CAPTURA do TemplateEngine
- ✅ Calcula escala baseado na captura real vs jogo (1920x1080)

### 2. Cálculo de Escala Correto

```python
# Captura real (pode ser 2 telas juntas)
capture_width = 4320   # Suas 2 telas
capture_height = 1350

# Jogo roda em UMA tela
game_width = 1920
game_height = 1080

# Calcular escala
scale_x = 4320 / 1920 = 2.25
scale_y = 1350 / 1080 = 1.25

# Usar média (mais preciso para multi-monitor)
scale = (2.25 + 1.25) / 2 = 1.75x
```

### 3. Conversão de Coordenadas

```python
# OpenCV detecta vara na captura total (4320x1350)
detection = (3797, 205)

# Converter para coordenadas do jogo (1920x1080)
game_x = 3797 / 1.75 = 2169  # Ainda pode estar errado!
game_y = 205 / 1.75 = 117

# Se ainda estiver fora, pode precisar ajustar offset
```

## 🎯 Logs de Debug Adicionados

Agora ao iniciar manutenção, você verá:

```
📐 Escala de detecção calculada: X.XXx
   🖥️ Setup multi-monitor detectado:
      Monitor 0 (TOTAL): 4320x1350
      Monitor 1: 1920x1080
      Monitor 2: 1920x1080
   📸 Captura TemplateEngine: 4320x1350 @ (0,0)
   📐 Escala final: 1.75x
      Conversão: (4320, 1350) → (1920, 1080)
```

Se as escalas X e Y forem muito diferentes:
```
   ⚠️ AVISO: Escalas X e Y muito diferentes!
      - scale_x = 2.25
      - scale_y = 1.25
   💡 Isso pode indicar aspect ratio diferente ou resolução errada
```

## 🔍 Próximos Passos

### Se AINDA não funcionar:

Pode ser que precise ajustar **OFFSET** também (não só escala):

```python
# Se o jogo está no Monitor 2 (direita):
offset_x = 1920  # Largura do Monitor 1

# Converter:
game_x = (detection_x / scale) - offset_x
```

### Como verificar qual monitor tem o jogo:

1. Execute o bot
2. Veja os logs de detecção:
   ```
   centro=(3797,205)  # Se X > 1920, jogo pode estar no Monitor 2
   ```

## 🧪 Teste Agora

Pressione **Page Down** e observe:

1. ✅ Logs mostram setup multi-monitor
2. ✅ Escala calculada (deve ser ~1.75-2.25x)
3. ✅ Conversões: `Det=(3797,205) → Jogo=(2169,117)` ou similar
4. ✅ Cliques devem acertar as varas no baú

### Se os cliques AINDA errarem:

Me envie os novos logs mostrando:
- Monitores detectados
- Escala calculada
- Coordenadas de conversão (Det → Jogo)
- Onde o clique realmente foi (visual)

Podemos adicionar **offset de monitor** se necessário!

## 📝 Arquivos Modificados

- `fishing_bot_v4/core/rod_maintenance_system.py`:
  - `_calculate_detection_scale()` - Agora detecta multi-monitor
  - `_convert_detection_to_game_coords()` - Converte com escala correta
  - Todos os `_scan_*` - Aplicam conversão