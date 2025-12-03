# Como Funciona o Sistema de Macro do Baú

## Visão Geral

O bot tem **2 tipos de macro** para abrir baú:

1. **Macro PADRÃO (Standard)** - Código dentro do programa
2. **Macro PERSONALIZADO (Custom)** - Arquivo externo (.pkl)

---

## 1. Macro PADRÃO (Standard) ✅ Recomendado

### Como funciona:

O macro padrão está **hardcoded** no arquivo [chest_manager.py](core/chest_manager.py:225-315), método `execute_standard_macro()`.

### Sequência do macro padrão:

```
1. Soltar ALT (preventivo - garantir que não está preso)
2. Liberar botões do mouse (segurança)
3. Pressionar ALT (ativa freelook)
4. Aguardar 0.5s
5. Mover câmera (DX horizontal + DY vertical)
6. Pressionar E (interagir)
7. Aguardar 0.5s
8. ALT permanece pressionado até fechar baú
```

### Valores configuráveis:

No arquivo `config.json` (ou `default_config.json`):

```json
{
  "chest_side": "left",           // Lado do baú: "left" ou "right"
  "chest_distance": 300,          // Distância horizontal (pixels)
  "chest_vertical_offset": 200    // Movimento para baixo (pixels)
}
```

### Como os valores afetam o movimento:

**chest_side="left"**:
```
DX = +300  (move câmera para ESQUERDA)
DY = +200  (move câmera para BAIXO)
```

**chest_side="right"**:
```
DX = -300  (move câmera para DIREITA)
DY = +200  (move câmera para BAIXO)
```

> ⚠️ **IMPORTANTE**: O eixo X é **invertido** durante ALT (freelook):
> - Valor POSITIVO = esquerda
> - Valor NEGATIVO = direita

---

## 2. Macro PERSONALIZADO (Custom)

### Arquivos de macro externo:

Quando você grava um macro personalizado, ele é salvo em arquivos `.pkl`:

```
📁 Pasta do .exe/
├── left_macro.pkl          ← Macro padrão esquerda
├── right_macro.pkl         ← Macro padrão direita
├── custom_left_macro.pkl   ← SEU macro personalizado (esquerda)
└── custom_right_macro.pkl  ← SEU macro personalizado (direita)
```

### Formato do arquivo .pkl:

É um arquivo binário Python (pickle) que contém uma lista de comandos:

```python
[
    {'action': 'key_down', 'key': 'alt'},
    {'action': 'sleep', 'duration': 0.5},
    {'action': 'move', 'x': 660, 'y': 540, 'duration': 0.5},
    {'action': 'sleep', 'duration': 0.3},
    {'action': 'key', 'key': 'e'},
    {'action': 'sleep', 'duration': 0.5},
    {'action': 'key_up', 'key': 'alt'}
]
```

### Comandos suportados:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `move` | Mover mouse para posição | `{'action': 'move', 'x': 960, 'y': 540, 'duration': 0.5}` |
| `click` | Clicar mouse | `{'action': 'click', 'button': 'left'}` |
| `key` | Pressionar e soltar tecla | `{'action': 'key', 'key': 'e'}` |
| `key_down` | Pressionar tecla (sem soltar) | `{'action': 'key_down', 'key': 'alt'}` |
| `key_up` | Soltar tecla | `{'action': 'key_up', 'key': 'alt'}` |
| `sleep` | Aguardar | `{'action': 'sleep', 'duration': 0.5}` |

---

## Onde fica a configuração no .exe?

### Durante desenvolvimento (Python):

```
📁 v5/
├── config/
│   └── default_config.json  ← Valores padrão
├── data/
│   └── config.json          ← Valores do usuário (sobrescreve padrão)
├── left_macro.pkl           ← Macro personalizado (se existir)
└── right_macro.pkl          ← Macro personalizado (se existir)
```

### No .exe compilado (Nuitka):

```
📁 Onde está o .exe/
├── FishingMageBot.exe
└── (arquivos de config vão para AppData)

📁 C:\Users\[Usuario]\AppData\Roaming\FishingMageBot\
├── config.json              ← Config do usuário (lado do baú, distance, etc)
├── left_macro.pkl           ← Macro personalizado esquerda (se gravar)
└── right_macro.pkl          ← Macro personalizado direita (se gravar)
```

> ✅ **PORTABILIDADE**: Os arquivos `.pkl` ficam no `AppData`, então:
> - **SIM, funcionam** após reiniciar o .exe
> - **SIM, persistem** entre sessões
> - **NÃO, não viajam** com o .exe (cada PC tem seus próprios)

---

## Como escolher entre Standard e Custom?

No arquivo `config.json`:

```json
{
  "macro_type": "standard"  // ou "custom"
}
```

**Recomendação**: Use **"standard"** (mais confiável)

Se `custom` não existir → Fallback automático para `standard`

---

## Troubleshooting

### Problema: "Macro não funciona no PC dele"

**Causa 1: Valores incorretos**
```json
// Testar valores menores primeiro
{
  "chest_side": "left",
  "chest_distance": 250,        // Era 300
  "chest_vertical_offset": 180  // Era 200
}
```

**Causa 2: Sensibilidade do mouse diferente**

Se sensibilidade ALTA no jogo → valores MENORES
Se sensibilidade BAIXA no jogo → valores MAIORES

**Causa 3: Templates faltando**

Baú não está sendo detectado/aberto corretamente

---

## Debug: Ver movimento em tempo real

Com as correções que fiz, os logs agora mostram:

```
🧭 [CHEST] Lado do baú: 'left' → normalizado: 'left'
📐 [CHEST] Movimento calculado:
   Horizontal (DX): +300 (←esquerda)
   Vertical (DY): +200 (↓baixo)
   Config atual: distance=300, vertical_offset=200

📹 [CHEST] MOVIMENTO DA CÂMERA (FREELOOK):
   🎮 Modo: ALT + Movimento Relativo
   ➡️  Deslocamento: DX=+300, DY=+200
   ⚠️  Cursor invisível durante ALT!
```

---

## Como copiar macro entre PCs?

### Método 1: Copiar arquivos .pkl

**No seu PC (que funciona)**:
```
C:\Users\Thiago\AppData\Roaming\FishingMageBot\
├── left_macro.pkl   ← Copiar este
└── right_macro.pkl  ← Copiar este
```

**No PC dele**:
```
Colar em:
C:\Users\[Nome]\AppData\Roaming\FishingMageBot\
```

### Método 2: Ajustar config manualmente

Mais confiável! Editar `config.json`:

```json
{
  "chest_side": "left",
  "chest_distance": 300,
  "chest_vertical_offset": 200,
  "macro_type": "standard"
}
```

Testar valores até funcionar.

---

## FAQ

**Q: "O macro .pkl viaja com o .exe?"**
A: **NÃO**. Fica no AppData do usuário.

**Q: "Posso forçar usar macro padrão?"**
A: Sim, edite config: `"macro_type": "standard"`

**Q: "Como gravar novo macro?"**
A: Pressione F3 (default) para iniciar gravação.

**Q: "Macro funciona com Arduino?"**
A: **SIM**! O código usa `input_manager`, que pode ser Arduino ou PyAutoGUI.

**Q: "Por que ALT fica pressionado?"**
A: Durante operações de baú, ALT (freelook) deve permanecer ativo. É solto apenas ao fechar baú (antes do TAB).

---

## Código-fonte relevante

- [chest_manager.py:168-223](core/chest_manager.py#L168-L223) - Cálculo de movimento
- [chest_manager.py:225-315](core/chest_manager.py#L225-L315) - Macro padrão
- [chest_manager.py:335-402](core/chest_manager.py#L335-L402) - Macro personalizado
- [chest_manager.py:60-74](core/chest_manager.py#L60-L74) - Arquivos de macro

---

## Resumo Final

| Aspecto | Standard Macro | Custom Macro |
|---------|---------------|--------------|
| Onde está | Código (dentro do .exe) | Arquivo .pkl (AppData) |
| Portabilidade | ✅ Sempre funciona | ❌ Específico por PC |
| Configurável | ✅ Via config.json | ❌ Precisa regravar |
| Recomendado | ✅ **SIM** | ⚠️ Só se necessário |

**Use macro STANDARD com config ajustada!**
