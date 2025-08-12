# Script para configurar novo repositório no GitHub
# Execute este script APÓS criar o repositório no GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$RepositoryName
)

Write-Host "🚀 Configurando novo repositório no GitHub..." -ForegroundColor Green
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "multichat_system")) {
    Write-Host "❌ Erro: Execute este script no diretório raiz do projeto multiChat" -ForegroundColor Red
    exit 1
}

# Verificar se o Git está inicializado
if (-not (Test-Path ".git")) {
    Write-Host "❌ Erro: Repositório Git não encontrado. Execute 'git init' primeiro." -ForegroundColor Red
    exit 1
}

# Remover remote antigo se existir
Write-Host "🔧 Removendo remote antigo..." -ForegroundColor Yellow
git remote remove origin 2>$null

# Adicionar novo remote
$remoteUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
Write-Host "🔗 Adicionando novo remote: $remoteUrl" -ForegroundColor Yellow
git remote add origin $remoteUrl

# Renomear branch para main
Write-Host "🌿 Renomeando branch para main..." -ForegroundColor Yellow
git branch -M main

# Fazer push
Write-Host "📤 Enviando código para o GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Sucesso! Repositório configurado com sucesso!" -ForegroundColor Green
    Write-Host "🌐 Acesse: https://github.com/$GitHubUsername/$RepositoryName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Para futuras atualizações, use:" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor White
    Write-Host "   git commit -m 'Sua mensagem'" -ForegroundColor White
    Write-Host "   git push" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push. Verifique:" -ForegroundColor Red
    Write-Host "   - Se o repositório foi criado no GitHub" -ForegroundColor Red
    Write-Host "   - Se o nome do usuário e repositório estão corretos" -ForegroundColor Red
    Write-Host "   - Se você tem permissão para fazer push" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Processo concluído!" -ForegroundColor Green 