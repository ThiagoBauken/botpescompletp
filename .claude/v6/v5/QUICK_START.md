# 🚀 Guia Rápido - Ultimate Fishing Bot v4.0

**Versão:** 4.0
**Data:** 2025-09-29

---

## ⚡ Início Rápido (5 minutos)

### 1. Instalação
```bash
# 1. Clonar/baixar o repositório
cd D:\finalbot\fishing_bot_v4

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Verificar instalação
python -c "import cv2, numpy, mss, keyboard, pyautogui; print('✅ Tudo OK!')"
```

### 2. Primeira Execução
```bash
# Executar bot
python main.py
```

**O que vai acontecer:**
1. ✅ Licença de desenvolvimento será gerada automaticamente
2. ✅ Interface com 8 abas será aberta
3. ✅ Todos os componentes serão inicializados
4. ✅ Hotkeys globais serão habilitados
5. ✅ Sistema estará pronto para uso!

### 3. Configuração Básica (2 minutos)

#### Aba 1 - Geral
- Resolução: `1920x1080` (padrão)
- Idioma: Português/English/Русский

#### Aba 2 - Templates
- Deixar valores padrão (já otimizados)
- Ajustar apenas se detecção falhar

#### Aba 3 - Alimentação
- **Quantidade de comidas:** `2` (recomendado)
- **Trigger:** `3 peixes` (ou tempo se preferir)

#### Aba 4 - Auto-Clean
- **Intervalo:** `1 peixe` (limpa após cada captura)
- **Lado do baú:** `direito` (ou esquerdo)

#### Aba 6 - Baú
- **Lado:** `direito` (ou esquerdo conforme jogo)
- **Distância:** `300` (ajustar se necessário)

### 4. Iniciar Bot
```
1. Abrir jogo
2. Posicionar personagem para pesca
3. Pressionar F9
4. Bot começa a pescar automaticamente!
```

---

## ⌨️ Hotkeys - Decorar Estas!

| Tecla | Ação | Quando Usar |
|-------|------|-------------|
| **F9** | 🚀 Iniciar bot | Pronto para pescar |
| **F1** | ⏸️ Pausar/Despausar | Precisa parar temporariamente |
| **F2** | 🛑 Parar bot | Terminou de pescar |
| **ESC** | 🚨 Emergency stop | Algo deu errado! |
| **F4** | 🎨 Ocultar/Mostrar UI | Gameplay sem interferência |
| **F6** | 🍖 Alimentar | Personagem com fome |
| **F5** | 🧹 Limpar inventário | Inventário cheio |
| **Page Down** | 🔧 Manutenção varas | Varas quebradas/sem isca |
| **TAB** | 🔄 Trocar vara | Mudar vara manualmente |

---

## 📋 Checklist Pré-Uso

### Antes de Iniciar
- [ ] Jogo aberto
- [ ] Personagem em posição de pesca
- [ ] Vara equipada
- [ ] Iscas disponíveis (carne de urso/lobo/crocodilo)
- [ ] Comida no baú (filé frito)
- [ ] Resolução 1920x1080 (ou ajustada no config)
- [ ] Baú acessível (lado configurado corretamente)

### Verificações de Segurança
- [ ] Templates na pasta `templates/`
- [ ] Arquivo `catch.png` existe (CRÍTICO)
- [ ] Config.json criado (auto-criado na primeira execução)
- [ ] Sem outras automações rodando
- [ ] Jogo em foco

---

## 🎯 Primeiro Uso - Passo a Passo Detalhado

### 1. Abrir Bot
```bash
cd fishing_bot_v4
python main.py
```

**Aguarde ver:**
```
═══════════════════════════════════════════════════════════
🎣 Ultimate Fishing Bot v4.0 - Inicializando...
═══════════════════════════════════════════════════════════

🔐 Inicializando sistema de licenças...
✅ Sistema licenciado com sucesso!

🌍 Configurando idioma...
✅ Sistema i18n carregado

⚙️ Inicializando configurações...
✅ ConfigManager v4.0 carregado

🎨 Inicializando interface...
✅ Interface criada!

🚀 Iniciando Ultimate Fishing Bot v4.0...
═══════════════════════════════════════════════════════════
✅ Bot inicializado e licenciado com sucesso!
🎮 Use a interface gráfica para controlar o bot
🌍 Seletor de idioma disponível no canto inferior direito
═══════════════════════════════════════════════════════════

⌨️ HOTKEYS DISPONÍVEIS
═══════════════════════════════════════════════════════════
  F9              - Iniciar bot
  F1              - Pausar/Despausar bot
  F2              - Parar bot
  ESC             - Parada de emergência
  F4              - Alternar visibilidade da UI
  F6              - Alimentação manual
  F5              - Limpeza manual do inventário
  F8              - Executar macro
  F11             - Testar macro de baú
  PAGE DOWN       - Manutenção de varas
  TAB             - Troca manual de vara
═══════════════════════════════════════════════════════════
```

### 2. Configurar (Se Primeira Vez)

**Aba 3 - Alimentação:**
- Quantidade de comidas: `2`
- Modo de trigger: `Por quantidade de peixes`
- Trigger: `3 peixes`

**Aba 4 - Auto-Clean:**
- Intervalo de limpeza: `1 peixe`
- Lado do baú: `direito`

**Aba 6 - Baú:**
- Lado do baú: `direito`
- Distância: `300`
- Offset vertical: `200`

### 3. Posicionar no Jogo
1. Abrir jogo
2. Ir para local de pesca
3. Equipar vara
4. Ficar parado em frente ao local de pesca
5. **NÃO** clicar em nada no jogo ainda

### 4. Iniciar Bot
1. Pressionar **F9**
2. Bot captura posição inicial automaticamente
3. Bot começa a pescar!

**Console mostrará:**
```
🚀 [F9] Iniciando bot...
🔍 Validando dependências...
✅ Dependências validadas com sucesso
📍 Posição inicial capturada: (960, 540)

🔄 Iniciando loop principal de pesca...

🎣 Iniciando ciclo de pesca...
🎣 FASE 1: Iniciando pesca (botão direito 1.6s)...
⚡ FASE 2: Fase rápida (7.5s de cliques)...
🐢 FASE 3: Fase lenta (A/D + cliques até timeout)...

🐟 Peixe detectado! Confiança: 0.850
✅ Peixe #1 capturado! Sistemas notificados.
```

### 5. Observar Funcionamento
**O bot automaticamente:**
- 🎣 Pesca continuamente
- 🍖 Alimenta a cada 3 peixes (configurável)
- 🧹 Limpa inventário a cada 1 peixe (configurável)
- 🔄 Troca varas quando necessário
- 📊 Atualiza estatísticas na UI

### 6. Pausar/Parar
- **F1** - Pausar temporariamente
- **F2** - Parar completamente
- **ESC** - Parada de emergência

---

## ⚠️ Troubleshooting Rápido

### Bot Não Inicia
**Sintoma:** Pressionar F9 não faz nada
**Solução:**
1. Verificar console para erros
2. Verificar se templates existem
3. Verificar se `catch.png` está na pasta `templates/`
4. Tentar reiniciar bot

### Bot Não Detecta Peixes
**Sintoma:** Pesca mas não detecta capturas
**Solução:**
1. Abrir Aba 2 - Templates
2. Reduzir confiança de `catch` para `0.7`
3. Salvar e testar novamente
4. Se ainda falhar, verificar se `catch.png` é correto

### Baú Não Abre
**Sintoma:** F6 ou F5 não abre baú
**Solução:**
1. Verificar Aba 6 - Baú
2. Ajustar `Lado do baú` (esquerdo/direito)
3. Ajustar `Distância` (testar 200, 300, 400)
4. Pressionar F11 para testar macro do baú

### Vara Não Troca
**Sintoma:** TAB não troca vara
**Solução:**
1. Verificar se varas estão no inventário
2. Abrir inventário manualmente (TAB) e verificar
3. Verificar se templates de vara existem:
   - `VARANOBAUCI.png`
   - `enbausi.png`
   - `varaquebrada.png`

### Hotkeys Não Funcionam
**Sintoma:** Nenhum hotkey responde
**Solução:**
1. Verificar se `keyboard` library está instalada:
   ```bash
   pip install keyboard
   ```
2. Reiniciar bot
3. Verificar console para erros de hotkey
4. Se Windows, executar como administrador

---

## 📊 O Que Esperar

### Primeiro Peixe (2-3 minutos)
- Bot inicia pesca
- Cliques rápidos por 7.5s
- Movimentos A/D até captura
- "🐟 Peixe #1 capturado!"

### Após 3 Peixes (~6-9 minutos)
- Alimentação automática executa
- Baú abre
- Comida é consumida
- Baú fecha
- Pesca continua

### Após Cada Peixe
- Inventário limpa automaticamente
- Peixes transferidos para baú
- Iscas permanecem no inventário

### Troca de Vara (Variável)
- Quando vara sem usos ou quebrada
- Inventário abre
- Vara nova selecionada
- Inventário fecha
- Pesca continua

---

## 💡 Dicas Pro

### Performance
- Fechar programas desnecessários
- CPU: ~5-15% esperado
- RAM: ~200MB esperado
- Se lag, aumentar timeouts

### Configuração Otimizada
```json
{
  "template_confidence": {
    "catch": 0.75,     // Reduzir se não detecta
    "VARANOBAUCI": 0.8,
    "enbausi": 0.7
  },
  "feeding_system": {
    "trigger_catches": 3,  // Alimentar a cada 3 peixes
    "feeds_per_session": 2 // Comer 2 vezes
  },
  "cleaning": {
    "auto_clean_interval": 1 // Limpar após cada peixe
  }
}
```

### Atalhos Úteis
- **F4** - Ocultar UI durante gameplay
- **F6** - Alimentar quando necessário
- **F5** - Limpar inventário cheio
- **ESC** - Parar tudo imediatamente

---

## 🎓 Fluxo de Trabalho Recomendado

### Sessão de Pesca Típica
```
1. Abrir jogo
2. Ir para local de pesca
3. Abrir bot (python main.py)
4. Configurar se primeira vez
5. Posicionar personagem
6. F9 - Iniciar
7. F4 - Ocultar UI (opcional)
8. Deixar rodar
9. F4 - Mostrar UI (ver stats)
10. F2 - Parar quando terminar
```

### Monitoramento
- Verificar console para erros
- Ver estatísticas na UI
- Observar logs em `data/logs/`
- Ajustar configs conforme necessário

---

## ✅ Checklist de Sucesso

### Bot Está Funcionando Se:
- [x] F9 inicia pesca
- [x] Detecta peixes capturados
- [x] Alimenta automaticamente
- [x] Limpa inventário
- [x] Troca varas quando necessário
- [x] Estatísticas atualizam
- [x] Logs mostram progresso
- [x] Nenhum erro no console

### Se Algum Item Acima Falhar:
1. Verificar seção de Troubleshooting
2. Consultar `TESTING_CHECKLIST.md`
3. Verificar logs em `data/logs/`
4. Ajustar configurações
5. Testar novamente

---

## 📚 Documentação Adicional

### Arquivos Úteis
- `IMPLEMENTATION_STATUS.md` - Status detalhado
- `TESTING_CHECKLIST.md` - Checklist de testes
- `WHATS_NEW.md` - Novidades da versão
- `README.md` - Documentação completa
- `CLAUDE.md` - Instruções para desenvolvimento

### Suporte
- **Issues:** https://github.com/seu-repo/issues
- **Logs:** `fishing_bot_v4/data/logs/`
- **Config:** `fishing_bot_v4/data/config.json`

---

## 🎉 Pronto para Pescar!

Você agora tem tudo que precisa para usar o Ultimate Fishing Bot v4.0!

**Lembre-se:**
- ⌨️ **F9** para iniciar
- 🎨 **F4** para ocultar UI
- 🛑 **F2** para parar
- 🚨 **ESC** para emergência

**Boa pesca! 🎣**

---

**Última atualização:** 2025-09-29
**Versão:** 4.0