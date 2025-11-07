# 📸 Sobre Prints e Screenshots no Projeto

## Por Que Prints NÃO São Limpos Automaticamente?

Prints/screenshots **não são parte do código**, são arquivos temporários criados manualmente durante desenvolvimento e debugging.

### Onde Prints Costumam Aparecer

```
❌ PRINTS DESNECESSÁRIOS (deletar):
├── fishing_bot_v4/*.png         ← Prints de testes/debug
├── data/*.png                   ← Screenshots salvos em runtime
├── *.png (raiz)                 ← Prints salvos acidentalmente
└── core/ui/utils/*.png          ← Prints esquecidos

✅ TEMPLATES NECESSÁRIOS (preservar):
└── templates/*.png              ← NUNCA deletar!
```

---

## Por Que Não Limpam Sozinhos?

1. **Não são parte do .gitignore padrão** - Geralmente são poucos arquivos
2. **Podem ser intencionais** - Docs, exemplos, etc.
3. **Não afetam compilação** - PyInstaller ignora imagens fora de `datas=[]`

---

## Como Limpar Manualmente

### Opção 1: Script Automático (Recomendado)
```bash
LIMPAR_PRINTS.bat
```

O script:
1. Busca prints em todas as pastas
2. Lista o que encontrou
3. Pede confirmação
4. Deleta tudo EXCETO `templates/`

### Opção 2: Manual
```bash
# Deletar prints da pasta fishing_bot_v4
del /Q fishing_bot_v4\*.png
del /Q fishing_bot_v4\*.jpg

# Deletar prints da raiz
del /Q *.png
del /Q *.jpg

# Verificar data\
del /Q data\*.png
```

---

## Adicionar ao .gitignore

Para evitar commits acidentais de prints, adicione ao `.gitignore`:

```gitignore
# Screenshots e prints temporários
*.png
*.jpg
*.jpeg
*.bmp

# Exceto templates (necessários)
!templates/*.png
!templates/**/*.png
```

---

## Quando Prints São Úteis

### ✅ Casos Legítimos:
- Documentação de bugs
- Exemplos para README
- Testes de detecção de templates

### ❌ Prints Desnecessários:
- Screenshots esquecidos em `fishing_bot_v4/`
- Testes antigos em `data/`
- Capturas acidentais na raiz

---

## Manutenção Regular

Execute antes de commits importantes:

```bash
# 1. Limpar prints
LIMPAR_PRINTS.bat

# 2. Limpar cache Python
del /S /Q __pycache__
del /S /Q *.pyc

# 3. Limpar builds antigas
rmdir /S /Q build dist

# 4. Commit limpo
git add .
git status
```

---

## Estrutura Ideal (Sem Prints)

```
v5/
├── core/              ← Sem imagens
├── ui/                ← Sem imagens
├── utils/             ← Sem imagens
├── data/              ← Sem imagens
├── fishing_bot_v4/    ← Sem imagens (vazio ou deletar pasta)
└── templates/         ← APENAS AQUI tem imagens!
    ├── catch.png
    ├── VARANOBAUCI.png
    └── ... (40+ templates)
```

---

## FAQ

**Q: Por que `fishing_bot_v4/` tem prints?**
A: Provavelmente testes antigos da v4. Se a pasta está vazia/antiga, pode deletar inteira.

**Q: Posso deletar TUDO exceto templates/?**
A: Sim! Use `LIMPAR_PRINTS.bat` com segurança.

**Q: E se eu deletar templates/ acidentalmente?**
A: O bot não funcionará! Templates são NECESSÁRIOS para detecção.

**Q: Como prevenir prints no futuro?**
A: Adicione ao `.gitignore` e use `LIMPAR_PRINTS.bat` antes de commits.
