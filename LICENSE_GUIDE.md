# 🔐 Guia de Licenciamento - Ultimate Fishing Bot v4.0

## ℹ️ Informações Importantes

O Ultimate Fishing Bot v4.0 usa um sistema de licenciamento baseado em hardware fingerprinting para proteger o software.

### 🆔 Hardware ID

Cada instalação gera um Hardware ID único baseado em:
- Processador
- Memória total
- Nome da máquina
- Arquitetura do sistema

**Importante**: Mudanças significativas no hardware podem invalidar sua licença.

## 📋 Como Obter uma Licença

### 1. Encontrar seu Hardware ID

Ao iniciar o bot pela primeira vez, você verá:
```
🖥️ Hardware ID: 26ac9cc77f1aa50a0f5b0582c7f0f84a
```

Ou execute:
```bash
cd fishing_bot_v4
python -c "from utils.license_manager import LicenseManager; print(LicenseManager().hardware_id)"
```

### 2. Solicitar Licença

Entre em contato com o desenvolvedor fornecendo:
- Seu Hardware ID completo
- Informações de pagamento/plano desejado
- Email para contato

### 3. Receber sua Chave

Você receberá uma chave no formato:
```
PROD-XXXX-YYYY-ZZZZ-AAAA-BBBB
```

ou

```
O9QY229LF042G9KZ
```

## ✅ Como Ativar sua Licença

### Método 1: Interface Gráfica

1. Execute o bot: `python main.py`
2. Se não houver licença, abrirá automaticamente o diálogo
3. Cole sua chave no campo
4. Clique em "🔓 Ativar Licença"

### Método 2: Teste Manual

```bash
cd fishing_bot_v4
python test_new_license.py PROD-XXXX-YYYY-ZZZZ
```

### Método 3: Arquivo Manual

Crie o arquivo `license.key` na pasta `fishing_bot_v4/`:
```bash
echo PROD-XXXX-YYYY-ZZZZ > license.key
```

Depois execute: `python main.py`

## ❌ Problemas Comuns

### Erro: "Chave inválida ou usada em outro dispositivo"

**Causas possíveis:**

1. **Chave digitada incorretamente**
   - Verifique se copiou a chave completa
   - Sem espaços extras no início/fim
   - Maiúsculas e minúsculas devem estar corretas

2. **Chave não existe no sistema**
   - Verifique com o desenvolvedor
   - Confirme que a chave foi gerada para este projeto

3. **Chave já usada em outro dispositivo**
   - Cada chave só pode ser ativada em um Hardware ID
   - Entre em contato para transferir ou solicitar nova chave

4. **Chave expirada**
   - Verifique a data de validade
   - Renove sua licença se necessário

### Erro: "Erro de conexão"

- Verifique sua conexão com a internet
- Servidor pode estar temporariamente indisponível
- Tente novamente em alguns minutos

### Erro: Status Code 400/403

- **400**: Dados de ativação inválidos (chave malformada)
- **403**: Chave inválida, expirada ou já usada

## 🔍 Verificar Licença Atual

```bash
cd fishing_bot_v4
python -c "
from utils.license_manager import LicenseManager
lm = LicenseManager()
if lm.check_license():
    print('✅ Licença válida!')
    info = lm.get_license_info()
    print(f'Expira em: {info.get(\"expires_at\")}')
    print(f'Status: {info.get(\"status\")}')
else:
    print('❌ Sem licença válida')
"
```

## 🔄 Transferir Licença

Se você trocou de computador ou reinstalou o sistema:

1. Entre em contato com o desenvolvedor
2. Informe o Hardware ID antigo e o novo
3. A licença será transferida manualmente

## 📞 Suporte

Para problemas com licenciamento:

- **Email**: [contato do desenvolvedor]
- **Discord**: [servidor do bot]
- **Issues**: https://github.com/[projeto]/issues

## 🔐 Informações Técnicas

- **Servidor**: `https://private-keygen.pbzgje.easypanel.host`
- **Project ID**: `67a4a76a-d71b-4d07-9ba8-f7e794ce0578`
- **Algoritmo**: SHA-256 para Hardware ID
- **Timeout**: 15 segundos para requisições

## ⚠️ Avisos Importantes

1. **Não compartilhe sua chave de licença** - Ela é única e vinculada ao seu hardware
2. **Mantenha sua chave segura** - Salve em um local seguro para reinstalações
3. **Hardware ID muda com upgrades** - Grandes mudanças de hardware podem requerer nova ativação
4. **Licenças têm validade** - Verifique a data de expiração e renove quando necessário

## 📊 Exemplo de Ativação Bem-Sucedida

```
🔐 Ativando chave: O9QY229LF0...
📤 Enviando ativação para: https://private-keygen.pbzgje.easypanel.host/activate
📋 Hardware ID: 26ac9cc77f1aa50a0f5b0582c7f0f84a
📥 Status Code: 200
📄 Response: {"valid":true,"message":"Chave já ativada neste dispositivo",...}
✅ Licença ativada com sucesso!
💾 Licença salva com sucesso!
```

## 🧪 Modo de Desenvolvimento

Para desenvolvedores e testes, o sistema pode criar licenças temporárias:

```python
from utils.license_validator import LicenseValidator
validator = LicenseValidator()
validator.create_development_license()
```

**Nota**: Licenças de desenvolvimento são apenas para testes locais e não funcionam em produção.
