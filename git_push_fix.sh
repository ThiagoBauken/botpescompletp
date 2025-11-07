#!/bin/bash
echo "=========================================="
echo "  Git Push - Fix Docker Import"
echo "=========================================="
echo ""

echo "Adicionando arquivos corrigidos..."
git add server/Dockerfile
git add server/server.py
git add server/.dockerignore
git add server/action_sequences.py
git add FIX_DOCKER_IMPORT.md
git add EASYPANEL_UPDATE.md
git add ARCHITECTURE_MULTI_USER.md
git add MIGRATION_COMPLETE.md

echo ""
echo "Fazendo commit..."
git commit -m "fix: Add action_sequences.py to Docker build

- Corrige ModuleNotFoundError no container
- Dockerfile copia todos os .py files
- Import robusto com fallbacks
"

echo ""
echo "Fazendo push..."
git push

echo ""
echo "=========================================="
echo "✅ Push completo!"
echo "=========================================="
echo ""
echo "EasyPanel vai detectar e rebuildar automaticamente."
echo "Aguarde 2-5 minutos e verifique os logs no painel."
echo ""
