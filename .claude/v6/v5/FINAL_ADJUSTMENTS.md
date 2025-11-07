# 🎯 AJUSTES FINAIS - Sistema de Manutenção

## ✅ Progresso Atual

### O que está funcionando:
1. ✅ **Conversão de coordenadas correta** - `4320x1350 → 1920x1080`
2. ✅ **Detecção no BAÚ** - Pega varas corretas (não do inventário)
3. ✅ **Vara quebrada** - Remove isca e guarda perfeitamente
4. ✅ **Coordenadas mais próximas** - Cursor está "próximo" mas não perfeito

### Problemas restantes:
1. ⚠️ **Cursor acima e à esquerda do centro** - Falta ajuste fino
2. ⚠️ **Duplicatas** - Pega mesma vara 2x (1687,164 e 1687,238)

## 🔧 Correções Aplicadas

### 1. Aumentado threshold de duplicatas

**Antes:**
```python
detections = self._remove_close_detections(detections, min_distance=30)
```

**Agora:**
```python
detections = self._remove_close_detections(detections, min_distance=80)
```

**Motivo:** Com 2 monitores + escala, mesma vara pode ser detectada em posições levemente diferentes (diferença de 74px)

### 2. Sistema de coordenadas confirmado

O `rod_viewer_background.py` **JÁ retorna o CENTRO** do template:
```python
# Linha 369-370
center_x = x + template_width // 2
center_y = y + template_height // 2
```

Então as coordenadas `(3797, 205)` JÁ são do **CENTRO** da vara na captura MSS.

### 3. Conversão de escala aplicada corretamente

```python
# Captura MSS: 4320x1350
# Jogo: 1920x1080
scale_x = 4320 / 1920 = 2.25
scale_y = 1350 / 1080 = 1.25

# Conversão
game_x = 3797 / 2.25 = 1687 ✅
game_y = 205 / 1.25 = 164 ✅
```

## 🎯 Próximo Teste

Execute **Page Down** novamente e observe:

1. **Duplicatas removidas?**
   - Antes: `(1687,164)` e `(1687,238)` - mesma vara
   - Agora: Deve pegar apenas uma

2. **Cursor no centro?**
   - Se ainda estiver acima/esquerda, pode precisar de offset adicional
   - Mas teoricamente está correto (centro do template + conversão de escala)

## 💡 Se cursor ainda estiver deslocado

Pode ser que precise ajustar o offset baseado no tamanho do template na captura escalada:

```python
# Pegar tamanho do template
template_w, template_h = template.shape[:2]

# Aplicar offset proporcional à escala
offset_x = (template_w / 2) * (scale_x - 1)
offset_y = (template_h / 2) * (scale_y - 1)

final_x = game_x + offset_x
final_y = game_y + offset_y
```

Mas isso deve ser desnecessário se o `rod_viewer` já calcula o centro corretamente.

## 📊 Logs Esperados

```
🎣 Vara no BAÚ: varanobauci | Captura=(3797,205) → Jogo=(1687,164)
🎣 Vara no BAÚ: varanobauci | Captura=(3890,205) → Jogo=(1728,164)
🎣 Vara no BAÚ: varanobauci | Captura=(3983,205) → Jogo=(1770,164)
🎣 Vara no BAÚ: varanobauci | Captura=(4076,205) → Jogo=(1811,164)
❌ NÃO deve aparecer (1687,238) - deve ser removido como duplicata
```

## 🎮 Resultado Esperado

- ✅ 4-6 varas detectadas (sem duplicatas)
- ✅ Cursor deve clicar no CENTRO de cada vara
- ✅ Drag deve pegar a vara corretamente
- ✅ Slots preenchidos com varas diferentes