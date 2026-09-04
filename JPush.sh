#!/bin/bash
echo "=== ATUALIZANDO EUFit ==="

# Garantir que arquivos de scan serão ignorados
echo "api_keys_scan_*.txt" >> .gitignore
git add .gitignore

# Adicionar tudo
git add .

# Remover arquivos de scan do stage (por segurança)
git reset HEAD api_keys_scan_*.txt 2>/dev/null || true

# Commit e push
git commit -m "refactor: limpeza e atualização do projeto EUFit"
git push origin main

echo "=== CONCLUÍDO! ==="
