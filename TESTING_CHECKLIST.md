# 🧪 Checklist de Testes - Ultimate Fishing Bot v4.0

**Data:** 2025-09-29
**Versão:** 4.0

---

## 📋 PREPARAÇÃO

### Ambiente
- [ ] Python 3.8+ instalado
- [ ] Todas as dependências instaladas (`pip install -r requirements.txt`)
- [ ] Jogo aberto e em posição de pesca
- [ ] Resolução 1920x1080 (ou ajustada no config)
- [ ] Templates na pasta `templates/`

### Configuração Inicial
- [ ] `config.json` criado (ou usar default)
- [ ] Coordenadas configuradas na UI
- [ ] Templates de confiança ajustados
- [ ] Lado do baú configurado (esquerdo/direito)

---

## 🧪 TESTES DE COMPONENTES INDIVIDUAIS

### 1. TemplateEngine
**Objetivo:** Verificar detecção de templates

**Testes:**
- [ ] **Detecção de peixe (catch.png)**
  - Abrir inventário
  - Verificar log: "🐟 Peixe detectado! Confiança: X.XXX"

- [ ] **Detecção de vara (VARANOBAUCI.png)**
  - Abrir inventário
  - Verificar log: "🎯 Vara no slot X: com_isca"

- [ ] **Detecção de inventário (inventory.png)**
  - Abrir inventário (TAB)
  - Verificar log: "📦 Inventário detectado como ABERTO"

- [ ] **Detecção de baú (loot.png)**
  - Abrir baú
  - Verificar log: "🎁 Baú detectado como ABERTO"

**Resultado Esperado:** Todos os templates detectados com confiança > threshold

---

### 2. InputManager
**Objetivo:** Verificar controle de mouse e teclado

**Testes:**
- [ ] **Mouse down/up**
  - Verificar clique funciona
  - Verificar botão direito funciona

- [ ] **Cliques contínuos**
  - Verificar loop de cliques (fase rápida)
  - Verificar interval correto (~0.1s)

- [ ] **Movimentos A/D**
  - Verificar movimento esquerda (A)
  - Verificar movimento direita (D)
  - Verificar alternância A/D

- [ ] **Emergency stop**
  - Pressionar ESC
  - Verificar que todos os inputs são liberados

**Resultado Esperado:** Todos os inputs funcionam corretamente

---

### 3. HotkeyManager
**Objetivo:** Verificar funcionamento dos hotkeys globais

**Testes:**
- [ ] **F9 - Iniciar Bot**
  - Pressionar F9
  - Verificar log: "🚀 [F9] Iniciando bot..."
  - Verificar bot inicia pesca

- [ ] **F1 - Pausar/Despausar**
  - Bot rodando, pressionar F1
  - Verificar log: "⏸️ [F1] Bot pausado"
  - Pressionar F1 novamente
  - Verificar log: "▶️ [F1] Bot despausado"

- [ ] **F2 - Parar Bot**
  - Bot rodando, pressionar F2
  - Verificar log: "🛑 [F2] Parando bot..."
  - Verificar bot para completamente

- [ ] **ESC - Emergency Stop**
  - Bot rodando, pressionar ESC
  - Verificar log: "🚨 [ESC] PARADA DE EMERGÊNCIA!"
  - Verificar todos os inputs liberados

- [ ] **F4 - Toggle UI**
  - Pressionar F4
  - Verificar UI oculta
  - Pressionar F4 novamente
  - Verificar UI restaura

- [ ] **F6 - Alimentação Manual**
  - Pressionar F6
  - Verificar log: "🍖 [F6] Executando alimentação manual..."
  - Verificar baú abre e alimentação executa

- [ ] **F5 - Limpeza Manual**
  - Pressionar F5
  - Verificar log: "🧹 [F5] Executando limpeza manual..."
  - Verificar inventário é limpo no baú

- [ ] **Page Down - Manutenção**
  - Pressionar Page Down
  - Verificar log: "🔧 [Page Down] Executando manutenção de varas..."
  - Verificar manutenção completa executa

- [ ] **TAB - Troca de Vara**
  - Pressionar TAB
  - Verificar log: "🔄 [TAB] Executando troca manual de vara..."
  - Verificar inventário abre e vara troca

**Resultado Esperado:** Todos os hotkeys funcionam e executam ações corretas

---

### 4. ChestManager
**Objetivo:** Verificar abertura/fechamento de baú

**Testes:**
- [ ] **Macro Padrão - Lado Esquerdo**
  - Configurar chest_side: "left"
  - Abrir baú via sistema
  - Verificar baú abre no lado esquerdo

- [ ] **Macro Padrão - Lado Direito**
  - Configurar chest_side: "right"
  - Abrir baú via sistema
  - Verificar baú abre no lado direito

- [ ] **Distância Configurável**
  - Configurar chest_distance: 300
  - Abrir baú
  - Verificar câmera move distância correta

- [ ] **Fechamento de Baú**
  - Baú aberto
  - Fechar via sistema
  - Verificar TAB é pressionado e baú fecha

**Resultado Esperado:** Baú abre/fecha corretamente em ambos os lados

---

### 5. FeedingSystem
**Objetivo:** Verificar sistema de alimentação

**Testes:**
- [ ] **Detecção Automática de Comida**
  - Colocar filé frito no baú
  - Executar F6
  - Verificar log: "✅ filefrito encontrado"

- [ ] **Detecção do Botão Eat**
  - Clicar em comida
  - Verificar log: "✅ Botão 'eat' detectado"

- [ ] **Loop de Alimentação**
  - Configurar feeds_per_session: 2
  - Executar F6
  - Verificar come 2 vezes

- [ ] **Trigger Automático - Peixes**
  - Configurar trigger_catches: 3
  - Pescar 3 peixes
  - Verificar alimentação automática executa

- [ ] **Busca no Inventário**
  - Comida só no inventário (não no baú)
  - Executar F6
  - Verificar busca no inventário funciona

**Resultado Esperado:** Sistema de alimentação funciona completamente

---

### 6. InventoryManager
**Objetivo:** Verificar limpeza de inventário

**Testes:**
- [ ] **Detecção de Peixes**
  - Inventário com peixes
  - Executar F5
  - Verificar log: "🔍 Detectando peixes..."

- [ ] **Transferência para Baú**
  - Peixes no inventário
  - Executar F5
  - Verificar peixes transferidos para baú

- [ ] **Preservar Iscas**
  - Iscas e peixes no inventário
  - Executar F5
  - Verificar iscas permanecem no inventário

- [ ] **Trigger Automático**
  - Configurar auto_clean_interval: 1
  - Pescar 1 peixe
  - Verificar limpeza automática executa

**Resultado Esperado:** Limpeza funciona e preserva iscas

---

### 7. RodManager
**Objetivo:** Verificar sistema de varas

**Testes:**
- [ ] **Detecção de Status**
  - Varas com diferentes status no inventário
  - Abrir inventário
  - Verificar log: "✅ Slot X: com_isca/sem_isca/quebrada"

- [ ] **Troca Automática**
  - Vara atual sem usos
  - Verificar troca automática executa
  - Verificar vara com isca é selecionada

- [ ] **Troca Manual (TAB)**
  - Pressionar TAB
  - Verificar inventário abre
  - Verificar vara troca

- [ ] **Sistema de Pares**
  - Verificar vara 1 e 2 são par
  - Verificar troca prioriza par atual
  - Verificar troca para outros pares se necessário

- [ ] **Manutenção Completa (Page Down)**
  - Pressionar Page Down
  - Verificar varas quebradas são trocadas
  - Verificar iscas são reabastecidas
  - Verificar slots vazios são preenchidos

**Resultado Esperado:** Sistema de varas funciona completamente

---

### 8. FishingEngine
**Objetivo:** Verificar ciclo completo de pesca

**Testes:**
- [ ] **Iniciar Pesca (F9)**
  - Pressionar F9
  - Verificar log: "🎣 FASE 1: Iniciando pesca..."
  - Verificar botão direito pressionado

- [ ] **Fase Rápida**
  - Verificar log: "⚡ FASE 2: Fase rápida (7.5s)"
  - Verificar cliques contínuos por 7.5s
  - Verificar detecção de peixe durante fase

- [ ] **Fase Lenta**
  - Após fase rápida
  - Verificar log: "🐢 FASE 3: Fase lenta"
  - Verificar movimentos A/D
  - Verificar cliques contínuos
  - Verificar detecção de peixe

- [ ] **Captura de Peixe**
  - Peixe detectado
  - Verificar log: "🐟 Peixe capturado!"
  - Verificar sequência de captura (soltar direito, aguardar 3s)

- [ ] **Timeout de Ciclo**
  - Ciclo sem captura
  - Aguardar 122s
  - Verificar log: "⏰ Timeout de 122s alcançado"

- [ ] **Sistema de Prioridades**
  - Múltiplas tarefas pendentes
  - Verificar ordem: Feeding > Rod Switch > Cleaning

- [ ] **Estatísticas**
  - Verificar contadores:
    - fish_caught
    - fishing_time
    - catches_per_hour

**Resultado Esperado:** Ciclo completo funciona de ponta a ponta

---

## 🎯 TESTES DE INTEGRAÇÃO

### Cenário 1: Pesca Simples
**Objetivo:** Testar ciclo básico sem complicações

**Passos:**
1. [ ] Iniciar bot (F9)
2. [ ] Aguardar captura de 3 peixes
3. [ ] Verificar estatísticas corretas
4. [ ] Parar bot (F2)

**Resultado Esperado:**
- 3 peixes capturados
- Estatísticas corretas
- Bot para sem erros

---

### Cenário 2: Pesca com Alimentação
**Objetivo:** Testar trigger automático de alimentação

**Passos:**
1. [ ] Configurar trigger_catches: 2
2. [ ] Iniciar bot (F9)
3. [ ] Aguardar 2 peixes
4. [ ] Verificar alimentação automática executa
5. [ ] Aguardar mais 2 peixes
6. [ ] Verificar segunda alimentação

**Resultado Esperado:**
- Alimentação automática após 2 peixes
- Bot continua pescando após alimentação

---

### Cenário 3: Pesca com Limpeza
**Objetivo:** Testar auto-clean do inventário

**Passos:**
1. [ ] Configurar auto_clean_interval: 1
2. [ ] Iniciar bot (F9)
3. [ ] Aguardar 1 peixe
4. [ ] Verificar limpeza automática executa
5. [ ] Verificar inventário limpo

**Resultado Esperado:**
- Limpeza após cada peixe
- Peixes transferidos para baú

---

### Cenário 4: Troca Automática de Vara
**Objetivo:** Testar sistema de troca automática

**Passos:**
1. [ ] Configurar rod_uses para vara atual: 0
2. [ ] Iniciar bot (F9)
3. [ ] Verificar troca automática executa
4. [ ] Verificar vara com isca selecionada
5. [ ] Continuar pescando

**Resultado Esperado:**
- Troca automática funciona
- Vara correta selecionada
- Bot continua sem erros

---

### Cenário 5: Manutenção Completa
**Objetivo:** Testar Page Down com múltiplos problemas

**Passos:**
1. [ ] Criar situação com:
   - Vara quebrada
   - Vara sem isca
   - Slot vazio
2. [ ] Pressionar Page Down
3. [ ] Verificar todas as correções executam
4. [ ] Verificar baú fecha corretamente

**Resultado Esperado:**
- Varas quebradas trocadas
- Iscas reabastecidas
- Slots preenchidos
- Sistema volta ao normal

---

### Cenário 6: Uso de Todos os Hotkeys
**Objetivo:** Testar todos os hotkeys em sequência

**Passos:**
1. [ ] F9 - Iniciar bot
2. [ ] F6 - Alimentação manual (durante pesca)
3. [ ] F5 - Limpeza manual (durante pesca)
4. [ ] F1 - Pausar
5. [ ] F1 - Despausar
6. [ ] TAB - Troca manual de vara
7. [ ] Page Down - Manutenção
8. [ ] F4 - Ocultar UI
9. [ ] F4 - Restaurar UI
10. [ ] F2 - Parar bot
11. [ ] F9 - Iniciar novamente
12. [ ] ESC - Emergency stop

**Resultado Esperado:**
- Todos os hotkeys funcionam
- Nenhum conflito entre ações
- Bot responde corretamente

---

### Cenário 7: Pesca Longa (Stress Test)
**Objetivo:** Testar estabilidade em uso prolongado

**Passos:**
1. [ ] Configurar todos os sistemas automáticos
2. [ ] Iniciar bot (F9)
3. [ ] Deixar rodar por 30 minutos
4. [ ] Verificar estatísticas
5. [ ] Parar bot (F2)

**Resultado Esperado:**
- Nenhum crash ou erro
- Estatísticas corretas
- Memória estável (~200MB)
- CPU estável (5-15%)

---

## ❌ TESTES DE ERRO E RECUPERAÇÃO

### Erro 1: Template Não Encontrado
**Cenário:** Template catch.png não existe

**Passos:**
1. [ ] Remover catch.png
2. [ ] Iniciar bot (F9)
3. [ ] Verificar log de erro
4. [ ] Verificar bot não inicia

**Resultado Esperado:**
- Erro claro no log
- Bot não inicia
- Mensagem amigável na UI

---

### Erro 2: Baú Não Abre
**Cenário:** Coordenadas do baú incorretas

**Passos:**
1. [ ] Configurar chest_distance: 9999
2. [ ] Tentar alimentação (F6)
3. [ ] Verificar erro
4. [ ] Verificar recovery

**Resultado Esperado:**
- Erro detectado
- Tentativa de fechar baú
- Sistema não trava

---

### Erro 3: Emergency Stop Durante Ação
**Cenário:** ESC durante alimentação

**Passos:**
1. [ ] Iniciar alimentação (F6)
2. [ ] Durante execução, pressionar ESC
3. [ ] Verificar interrupção imediata
4. [ ] Verificar inputs liberados

**Resultado Esperado:**
- Ação interrompida imediatamente
- Todos os inputs liberados
- Sistema em estado limpo

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

### Obrigatórios (Bloqueadores)
- [ ] Todos os hotkeys funcionam
- [ ] FishingEngine completa ciclo sem erros
- [ ] RodManager troca varas corretamente
- [ ] FeedingSystem alimenta corretamente
- [ ] InventoryManager limpa sem perder iscas
- [ ] ChestManager abre/fecha baú

### Desejáveis (Não Bloqueadores)
- [ ] Performance < 15% CPU
- [ ] Memória < 300MB
- [ ] Todos os templates detectados
- [ ] UI responsiva
- [ ] Logs claros e informativos

### Opcionais (Melhorias Futuras)
- [ ] Sistema de macros (F8/F11)
- [ ] Recovery automático de erros
- [ ] Notificações de eventos
- [ ] Dashboard avançado

---

## ✅ CHECKLIST FINAL

### Antes de Lançar v4.0
- [ ] Todos os testes de componentes passaram
- [ ] Todos os testes de integração passaram
- [ ] Pelo menos 3 cenários testados em jogo real
- [ ] Nenhum erro bloqueador encontrado
- [ ] Performance dentro dos limites
- [ ] Documentação atualizada
- [ ] README com instruções claras

### Opcional (v4.1)
- [ ] Sistema de macros implementado
- [ ] Recovery robusto
- [ ] Testes automatizados
- [ ] CI/CD pipeline

---

**Última atualização:** 2025-09-29
**Versão do checklist:** 1.0