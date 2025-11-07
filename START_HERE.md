# 🚀 Guia Rápido - Inicialização do Sistema

## ⚡ Início Rápido

### Modo Multi-Usuário (Servidor + Cliente)

**Windows:**
```bash
# Terminal 1: Iniciar servidor
start_server.bat

# Terminal 2: Iniciar cliente
python main.py
```

**Linux/Docker:**
```bash
# Terminal 1: Iniciar servidor
chmod +x start_server.sh
./start_server.sh

# Terminal 2: Iniciar cliente
python3 main.py
```

### Modo Standalone (Apenas Cliente - Offline)

```bash
# Cliente funciona 100% sem servidor
python main.py
```

---

## 🔧 Requisitos

### Python
```bash
# Instalar dependências
pip install -r requirements.txt
```

### Verificar Instalação
```bash
# Testar integração
python test_server_integration.py
```

---

## 🌐 Configuração do Servidor

### Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na pasta raiz com:

```env
# Porta do servidor (padrão: 8122)
PORT=8122

# Host (padrão: 0.0.0.0 para aceitar todas conexões)
HOST=0.0.0.0

# URL do Keymaster (validação de licenças)
KEYMASTER_URL=https://private-keygen.pbzgje.easypanel.host
PROJECT_ID=67a4a76a-d71b-4d07-9ba8-f7e794ce0578

# Banco de dados (padrão: data/fishing.db)
DATABASE_PATH=data/fishing.db

# Logs
LOG_LEVEL=INFO
```

---

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'action_sequences'"

**Solução:** Use os scripts de inicialização fornecidos (`start_server.bat` ou `start_server.sh`) que garantem o diretório correto.

Se ainda assim der erro:
```bash
cd server
python server.py
```

### Erro: "Port already in use"

**Solução:** Porta 8122 já está ocupada. Altere no `.env`:
```env
PORT=8123
```

### Cliente não conecta ao servidor

**Verifique:**
1. Servidor está rodando? Veja logs no terminal
2. Porta correta no cliente? Verifique `config.json`
3. Firewall bloqueando? Libere porta 8122

---

## 📊 Verificar Status

### Servidor
```bash
# Ver logs do servidor
tail -f server/logs/server.log
```

### Cliente
```bash
# Ver logs do cliente
tail -f data/logs/fishing_bot_*.log
```

### Health Check
```bash
# Testar servidor está respondendo
curl http://localhost:8122/health
```

---

## 📚 Documentação Completa

- **[ARCHITECTURE_MULTI_USER.md](ARCHITECTURE_MULTI_USER.md)** - Arquitetura detalhada
- **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Resumo da implementação
- **[README.md](README.md)** - Documentação geral do projeto
- **[QUICK_START.md](QUICK_START.md)** - Guia de 5 minutos

---

## 🎯 Fluxo de Uso

1. **Iniciar servidor** (ou pular para modo offline)
2. **Iniciar cliente** com `python main.py`
3. **Pressionar F9** para começar a pescar
4. **Observar logs** para ver operações automáticas

---

## ✅ Testes

Execute antes de usar em produção:
```bash
# Testar integração completa
python test_server_integration.py

# Resultado esperado: 6/6 testes passam
```

---

**Status:** ✅ Sistema pronto para uso
**Versão:** v5.0 (Multi-User Architecture)
**Última Atualização:** 2025-10-29
