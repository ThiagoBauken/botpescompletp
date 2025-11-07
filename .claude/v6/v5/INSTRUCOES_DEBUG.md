# 🛡️ INSTRUÇÕES DE DEBUG - CAPTURAR BUG DO ALT/CURSOR

## ✅ O QUE FOI IMPLEMENTADO

Foi criado um **sistema de logging ultra-detalhado** que salva TUDO em arquivo, mesmo se o programa crashar ou você desligar o PC na mão.

### Arquivos de Log Criados

Quando você rodar o bot, será criado automaticamente um arquivo em:

```
data/logs/FULL_DEBUG_2025-XX-XX_HH-MM-SS.log
```

**IMPORTANTE:** O arquivo tem timestamp único no nome, então cada execução cria um arquivo novo.

## 🎯 COMO REPRODUZIR O BUG

Siga estes passos EXATAMENTE:

1. **Inicie o bot normalmente:**
   ```
   python main.py
   ```

2. **Pressione F9** para iniciar a pesca

3. **Aguarde capturar 1 peixe**

4. **O sistema vai automaticamente:**
   - Ativar alimentação (após 1 peixe configurado)
   - Fila de limpeza será acionada
   - Fila de manutenção será acionada

5. **Observe quando o bug ocorrer:**
   - ALT ficará pressionado
   - Cursor se moverá para um ponto específico da tela
   - Sistema ficará travado/bugado

6. **Quando o bug acontecer:**
   - **DESLIGAR O PC NA MÃO** (sem fechar o programa)
   - Ou pressione ESC para emergency stop e feche o programa

## 📂 ONDE ENCONTRAR O LOG

Após reinicar o PC/programa:

1. Vá para a pasta: `c:\Users\Thiago\Desktop\v5\data\logs\`

2. Procure pelo arquivo mais recente: `FULL_DEBUG_YYYY-MM-DD_HH-MM-SS.log`

3. **ENVIE ESSE ARQUIVO COMPLETO**

## 🔍 O QUE O LOG VAI MOSTRAR

O log contém informações EXTREMAMENTE detalhadas:

### 1. Estado do InputManager
```
[TIMESTAMP] [INFO    ] [INPUT_MGR          ] [Thread:MainThread ] Inicializando InputManager...
[TIMESTAMP] [STATE   ] [INPUT_MGR          ] Mouse State, Keyboard State, etc.
```

### 2. Teclas Pressionadas/Liberadas
```
[TIMESTAMP] [INFO    ] [INPUT_KEY          ] Pressionando tecla 'alt'...
[TIMESTAMP] [CRITICAL] [INPUT_KEY          ] Tecla 'alt' NÃO foi liberada!
```

### 3. Operações de Drag (Movimento de Cursor)
```
[TIMESTAMP] [INFO    ] [INPUT_DRAG         ] DRAG INICIADO: (x1, y1) → (x2, y2)
[TIMESTAMP] [DEBUG   ] [INPUT_DRAG         ] PASSO 1: Movendo para posição inicial...
[TIMESTAMP] [DEBUG   ] [INPUT_DRAG         ] PASSO 2: Segurando botão esquerdo...
```

### 4. Sistema de Alimentação (Onde o ALT é usado)
```
[TIMESTAMP] [INFO    ] [FEEDING_CHEST      ] ═══ INICIANDO ABERTURA DE BAÚ ═══
[TIMESTAMP] [CRITICAL] [FEEDING_CHEST      ] PRESSIONANDO ALT - PONTO CRÍTICO!
[TIMESTAMP] [STATE   ] [FEEDING_CHEST      ] alt_pressed: True, timestamp: XXXX
[TIMESTAMP] [CRITICAL] [FEEDING_CHEST      ] LIBERANDO ALT - PONTO CRÍTICO!
```

### 5. Emergency Stop
```
[TIMESTAMP] [WARNING ] [INPUT_EMERGENCY    ] EMERGENCY STOP ACIONADO!
[TIMESTAMP] [STATE   ] [INPUT_EMERGENCY    ] before_stop: {...}
[TIMESTAMP] [INFO    ] [INPUT_EMERGENCY    ] Liberando ALT, CTRL, SHIFT explicitamente...
```

## 🚨 SINAIS DO BUG NO LOG

Procure por estas sequências NO ARQUIVO DE LOG:

### ⚠️ SINAL 1: ALT não liberado
```
[TIMESTAMP] [CRITICAL] [FEEDING_CHEST] PRESSIONANDO ALT - PONTO CRÍTICO!
... (operações)
[TIMESTAMP] [ERROR   ] [FEEDING_CHEST] ERRO NA ABERTURA DO BAÚ: ...
[TIMESTAMP] [WARNING ] [FEEDING_CHEST] FINALLY: ALT ainda pressionado, liberando forçadamente...
```

### ⚠️ SINAL 2: Drag travado
```
[TIMESTAMP] [INFO    ] [INPUT_DRAG] DRAG INICIADO: ...
[TIMESTAMP] [DEBUG   ] [INPUT_DRAG] PASSO 2: Segurando botão esquerdo...
... (sem PASSO 4: Soltando botão)
```

### ⚠️ SINAL 3: Teclas não liberadas
```
[TIMESTAMP] [WARNING] [INPUT_KEY] Tecla 'alt' já estava pressionada!
[TIMESTAMP] [STATE  ] [INPUT_KEY] keys_down: ['alt', ...]
```

## 📤 O QUE ENVIAR

Envie o arquivo **COMPLETO** `FULL_DEBUG_YYYY-MM-DD_HH-MM-SS.log` que foi criado durante a execução onde o bug ocorreu.

**NÃO edite o arquivo!** Envie ele completo para análise.

## 💡 DICAS

1. **O arquivo é flush imediato:** Mesmo se o programa crashar ou você desligar na mão, as últimas linhas escritas ESTARÃO NO ARQUIVO.

2. **Procure por CRITICAL e ERROR:** Use Ctrl+F no arquivo para buscar essas palavras.

3. **Timestamp preciso:** Cada linha tem timestamp com milissegundos, então você pode ver EXATAMENTE quando o bug ocorreu.

4. **Thread tracking:** Cada linha mostra qual thread executou, útil para identificar deadlocks.

## 🎯 PRÓXIMOS PASSOS

Após receber o log, vou:

1. Identificar EXATAMENTE onde o ALT ficou preso
2. Ver se foi na alimentação, limpeza ou manutenção
3. Verificar se houve exception não tratada
4. Identificar qual operação não liberou o input corretamente
5. **CORRIGIR O BUG** com base nas evidências concretas!

---

## 🔧 COMANDOS ÚTEIS

### Ver o log em tempo real (Windows PowerShell):
```powershell
Get-Content "data\logs\FULL_DEBUG_*.log" -Wait -Tail 50
```

### Buscar por erros no log:
```powershell
Select-String -Path "data\logs\FULL_DEBUG_*.log" -Pattern "ERROR|CRITICAL"
```

### Contar linhas do log:
```powershell
(Get-Content "data\logs\FULL_DEBUG_*.log").Count
```

---

**Boa sorte na captura do bug! Com esse log detalhado, vamos encontrar o problema! 🎯**
