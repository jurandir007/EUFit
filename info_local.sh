#!/bin/bash
# deploy.sh - Script para deploy do EUFit para o GitHub
# Uso: ./deploy.sh

echo "========================================"
echo "   DEPLOY EUFit - GitHub Push"
echo "========================================"
echo "Data: $(date)"
echo "Usuário: $(whoami)"
echo "Hostname: $(hostname)"
echo "========================================"

# Configurações
PROJECT_DIR="/home/jurandir/PycharmProjects/EUFit"
GITKEY_PATH="/home/jurandir/PycharmProjects/EUFit/gitkey"
BRANCH="main"
REMOTE="origin"

# Verificar se está no diretório correto
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ ERRO: Diretório do projeto não encontrado: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo -e "\n📁 Diretório: $(pwd)"

# Verificar chave SSH
echo -e "\n🔐 Verificando chave SSH..."
if [ -f "$GITKEY_PATH" ]; then
    echo "✅ Chave SSH encontrada: $GITKEY_PATH"
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add "$GITKEY_PATH" 2>/dev/null && echo "✅ Chave adicionada ao ssh-agent"
else
    echo "❌ Chave SSH não encontrada em: $GITKEY_PATH"
    exit 1
fi

# Verificar conexão com GitHub
echo -e "\n🌐 Verificando conexão com GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ Conexão SSH com GitHub OK!"
else
    echo "❌ Falha na conexão SSH com GitHub"
    exit 1
fi

# Mostrar status atual
echo -e "\n📊 Status do Git:"
git status --short

# Verificar se há arquivos para adicionar
echo -e "\n📦 Preparando arquivos para commit..."

# Adicionar apenas arquivos que EXISTEM E FORAM MODIFICADOS
git add deploy.sh 2>/dev/null && echo "✅ deploy.sh adicionado"

# Adicionar .gitignore se foi modificado
git add .gitignore 2>/dev/null && echo "✅ .gitignore adicionado"

# Verificar se routes.py foi modificado
if git status --porcelain | grep -q "routes.py"; then
    git add app/modules/dashboard/routes.py 2>/dev/null && echo "✅ routes.py adicionado"
fi

# Verificar se vape_dashboard.html foi modificado
if git status --porcelain | grep -q "vape_dashboard.html"; then
    git add app/docs/vape_dashboard.html 2>/dev/null && echo "✅ vape_dashboard.html adicionado"
fi

# Verificar se requirements.txt foi modificado
if git status --porcelain | grep -q "requirements.txt"; then
    git add requirements.txt 2>/dev/null && echo "✅ requirements.txt adicionado"
fi

# Verificar arquivos de script
if [ -f "info_local.sh" ] && git status --porcelain | grep -q "info_local.sh"; then
    git add info_local.sh 2>/dev/null && echo "✅ info_local.sh adicionado"
fi

echo -e "\n⚠️  Lembrete: NÃO versionar arquivos .env ou neon.env"
if [ -f ".env" ]; then
    echo "  - .env existe (NÃO versionado)"
fi
if [ -f "neon.env" ]; then
    echo "  - neon.env existe (NÃO versionado)"
fi

# Mostrar o que será commitado
echo -e "\n📋 Arquivos preparados para commit:"
git status --short

# Verificar se há algo para commitar
if git status --porcelain | grep -q "^[AM]"; then
    echo -e "\n❓ Deseja continuar com o commit? (s/N)"
    read -r resposta
    if [[ ! "$resposta" =~ ^[Ss]$ ]]; then
        echo "❌ Deploy cancelado pelo usuário."
        exit 0
    fi

    # Fazer commit
    echo -e "\n📝 Fazendo commit..."
    commit_msg="Deploy: $(date '+%Y-%m-%d %H:%M')"
    echo "Mensagem do commit: $commit_msg"
    git commit -m "$commit_msg"

    if [ $? -ne 0 ]; then
        echo "❌ Falha no commit. Verifique as mensagens acima."
        exit 1
    fi

    echo -e "\n✅ Commit realizado com sucesso!"
    git log -1 --oneline

    # Fazer push
    echo -e "\n🚀 Enviando para GitHub..."
    git push "$REMOTE" "$BRANCH"

    if [ $? -eq 0 ]; then
        echo -e "\n✅ Deploy concluído com sucesso!"
        echo "📌 Último commit: $(git log -1 --oneline)"
    else
        echo -e "\n❌ Falha no push."
        exit 1
    fi
else
    echo -e "\n⚠️  Nenhum arquivo modificado para commitar."
    echo "Se quiser forçar o push, use: git push --force"
fi

echo -e "\n========================================"
echo "  DEPLOY FINALIZADO!"
echo "========================================"
echo "Próximos passos na VM (GCE):"
echo "  1. cd ~/EUFit"
echo "  2. git pull origin main"
echo "  3. .EUFit/bin/uv pip install -r requirements.txt"
echo "  4. sudo systemctl restart eufit.service"
echo "========================================"
