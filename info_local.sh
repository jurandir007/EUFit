#!/bin/bash
# info_deploy_complete.sh

echo "========================================"
echo "   COLETANDO INFORMAÇÕES PARA DEPLOY"
echo "========================================"
echo "Data: $(date)"
echo "Usuário: $(whoami)"
echo "Hostname: $(hostname)"
echo "Diretório: $(pwd)"
echo "========================================"

cd ~/PycharmProjects/EUFit

echo -e "\n========================================"
echo "  1. INFORMAÇÕES DO GIT"
echo "========================================"

echo "1.1 Repositório remoto:"
git remote -v

echo -e "\n1.2 Branch atual:"
git branch --show-current

echo -e "\n1.3 Status do repositório:"
git status --short

echo -e "\n1.4 Último commit:"
git log -1 --oneline

echo -e "\n1.5 Commits não enviados (local -> remote):"
git log origin/main..HEAD --oneline 2>/dev/null || echo "Nenhum commit local não enviado"

echo -e "\n1.6 Commits novos no remote (remote -> local):"
git fetch origin 2>/dev/null
git log HEAD..origin/main --oneline 2>/dev/null || echo "Nenhum commit novo no remote"

echo -e "\n1.7 Verificando chave SSH:"
if [ -f ~/.ssh/id_rsa ]; then
    echo "✅ Chave SSH encontrada: ~/.ssh/id_rsa"
    ssh -T git@github.com 2>&1 | head -1
else
    echo "❌ Chave SSH não encontrada"
fi

echo -e "\n========================================"
echo "  2. AMBIENTE VIRTUAL"
echo "========================================"

echo "2.1 Ambiente virtual ativo:"
echo "VIRTUAL_ENV: $VIRTUAL_ENV"

echo -e "\n2.2 Versão do Python:"
python3 --version

echo -e "\n2.3 Pip:"
pip --version 2>/dev/null || echo "pip não disponível"

echo -e "\n2.4 uv:"
uv --version 2>/dev/null || echo "❌ uv não instalado"

echo -e "\n2.5 uv no .EUFit:"
if [ -d ".EUFit" ]; then
    .EUFit/bin/uv --version 2>/dev/null && echo "✅ uv está no .EUFit" || echo "❌ uv não está no .EUFit"
fi

echo -e "\n2.6 Dependências principais instaladas:"
pip list 2>/dev/null | grep -E "Flask|SQLAlchemy|scikit|gunicorn|psycopg2|Authlib|bcrypt" || echo "Nenhuma dependência principal encontrada"

echo -e "\n========================================"
echo "  3. ARQUIVOS DO PROJETO"
echo "========================================"

echo "3.1 requirements.txt:"
if [ -f "requirements.txt" ]; then
    echo "✅ Sim"
    echo "Total de linhas: $(wc -l < requirements.txt)"
    echo -e "\nPrimeiras 10 dependências:"
    head -10 requirements.txt
    echo -e "\nÚltimas 5 dependências:"
    tail -5 requirements.txt
else
    echo "❌ Não encontrado"
fi

echo -e "\n3.2 .env:"
if [ -f ".env" ]; then
    echo "✅ Sim"
    echo -e "\nVariáveis configuradas (sem valores):"
    grep -E "^[A-Z_]+=" .env | cut -d= -f1
    echo -e "\nTotal de variáveis: $(grep -E "^[A-Z_]+=" .env | wc -l)"
else
    echo "❌ Não encontrado"
fi

echo -e "\n3.3 neon.env:"
if [ -f "neon.env" ]; then
    echo "✅ Sim"
    echo "Variáveis:"
    grep -E "^[A-Z_]+=" neon.env | cut -d= -f1
else
    echo "❌ Não encontrado"
fi

echo -e "\n3.4 app.py ou run.py:"
if [ -f "app.py" ]; then
    echo "✅ app.py encontrado"
elif [ -f "run.py" ]; then
    echo "✅ run.py encontrado"
elif [ -f "main.py" ]; then
    echo "✅ main.py encontrado"
else
    echo "❌ Nenhum arquivo principal encontrado (app.py, run.py, main.py)"
fi

echo -e "\n========================================"
echo "  4. ESTRUTURA DO PROJETO"
echo "========================================"

echo "4.1 Arquivos por tipo:"
echo "Python: $(find . -name "*.py" -not -path "./.EUFit/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./build/*" 2>/dev/null | wc -l)"
echo "HTML: $(find . -name "*.html" -not -path "./.EUFit/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./build/*" 2>/dev/null | wc -l)"
echo "CSS: $(find . -name "*.css" -not -path "./.EUFit/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./build/*" 2>/dev/null | wc -l)"
echo "JS: $(find . -name "*.js" -not -path "./.EUFit/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./build/*" 2>/dev/null | wc -l)"

echo -e "\n4.2 Principais diretórios:"
ls -la | grep "^d" | grep -v "\.$" | grep -v "\.\."

echo -e "\n4.3 Tamanho do projeto:"
du -sh . 2>/dev/null || echo "Não foi possível calcular"

echo -e "\n========================================"
echo "  5. ARQUIVOS MODIFICADOS (últimos 30 dias)"
echo "========================================"
echo "Últimos 10 arquivos modificados:"
find . -type f -not -path "./.EUFit/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./.git/*" -not -path "./build/*" -mtime -30 -printf "%T@ %p\n" 2>/dev/null | sort -rn | head -10 | cut -d' ' -f2-

echo -e "\n========================================"
echo "  6. CONFIGURAÇÕES DO BANCO"
echo "========================================"

if [ -f "neon.env" ]; then
    source neon.env 2>/dev/null
    if [ ! -z "$SQLALCHEMY_DATABASE_URI" ]; then
        echo "SQLALCHEMY_DATABASE_URI configurada (parcial):"
        echo "$SQLALCHEMY_DATABASE_URI" | sed 's/:\/\/[^@]*@/:\/\/***@/'
    fi
fi

if [ -f ".env" ]; then
    source .env 2>/dev/null
    if [ ! -z "$DATABASE_URL" ]; then
        echo "DATABASE_URL configurada (parcial):"
        echo "$DATABASE_URL" | sed 's/:\/\/[^@]*@/:\/\/***@/'
    fi
fi

echo -e "\n========================================"
echo "  7. MIGRAÇÕES"
echo "========================================"

if [ -d "migrations" ]; then
    echo "✅ Diretório migrations existe"
    echo "Arquivos de migração: $(find migrations -name "*.py" 2>/dev/null | wc -l)"
    echo -e "\nÚltimas migrações:"
    ls -la migrations/versions/ 2>/dev/null | tail -5
else
    echo "❌ Diretório migrations não encontrado"
fi

echo -e "\n========================================"
echo "  8. VERIFICAÇÃO PARA DEPLOY"
echo "========================================"

echo "8.1 Arquivos que serão enviados:"
git ls-files | head -10
echo "... (total: $(git ls-files | wc -l) arquivos)"

echo -e "\n8.2 Arquivos ignorados (.gitignore):"
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore encontrado"
    echo "Total de regras: $(grep -v "^#" .gitignore | grep -v "^$" | wc -l)"
else
    echo "❌ .gitignore não encontrado"
fi

echo -e "\n8.3 Branch para deploy:"
echo "Branch atual: $(git branch --show-current)"
echo "Origin: $(git remote get-url origin 2>/dev/null || echo 'não configurado')"

echo -e "\n8.4 Status do serviço (se rodando localmente):"
if pgrep -f "flask" > /dev/null 2>&1; then
    echo "✅ Flask está rodando localmente"
else
    echo "❌ Flask não está rodando localmente"
fi

echo -e "\n========================================"
echo "  9. COMPARAÇÃO COM VM (produção)"
echo "========================================"

echo "9.1 Último commit na VM (precisa ser verificado na VM):"
echo "Execute na VM: cd ~/apps/EUFit && git log -1 --oneline"

echo -e "\n9.2 Variáveis .env vs neon.env:"
if [ -f ".env" ] && [ -f "neon.env" ]; then
    echo "Comparando variáveis:"
    echo ".env: $(grep -E "^[A-Z_]+=" .env | cut -d= -f1 | wc -l) variáveis"
    echo "neon.env: $(grep -E "^[A-Z_]+=" neon.env | cut -d= -f1 | wc -l) variáveis"
    echo -e "\nVariáveis que existem em ambos:"
    comm -12 <(grep -E "^[A-Z_]+=" .env | cut -d= -f1 | sort) <(grep -E "^[A-Z_]+=" neon.env | cut -d= -f1 | sort)
fi

echo -e "\n========================================"
echo "  10. CHECKLIST FINAL PARA DEPLOY"
echo "========================================"

echo "Antes de fazer o deploy, verifique:"
echo ""
echo "[ ] 1. Todas as alterações estão commitadas e pushadas"
echo "[ ] 2. O requirements.txt está atualizado no GitHub"
echo "[ ] 3. As novas variáveis de ambiente estão no .env da VM"
echo "[ ] 4. A VM tem acesso SSH ao GitHub"
echo "[ ] 5. O uv está instalado no .EUFit da VM"
echo "[ ] 6. Backup do banco foi feito"
echo "[ ] 7. Testes estão passando localmente"

echo -e "\n========================================"
echo "✅ Coleta concluída!"
echo "========================================"
