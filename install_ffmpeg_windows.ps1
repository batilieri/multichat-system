# Script para instalar FFmpeg no Windows
# Execute como administrador

Write-Host "🎵 Instalando FFmpeg no Windows..." -ForegroundColor Green

# Verificar se o Chocolatey está instalado
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando Chocolatey..." -ForegroundColor Yellow
    
    # Instalar Chocolatey
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    Write-Host "✅ Chocolatey instalado!" -ForegroundColor Green
} else {
    Write-Host "✅ Chocolatey já está instalado" -ForegroundColor Green
}

# Instalar FFmpeg
Write-Host "🎵 Instalando FFmpeg..." -ForegroundColor Yellow
choco install ffmpeg -y

# Verificar se a instalação foi bem-sucedida
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "✅ FFmpeg instalado com sucesso!" -ForegroundColor Green
    
    # Mostrar versão
    $version = ffmpeg -version 2>&1 | Select-String "ffmpeg version" | ForEach-Object { $_.ToString().Split(' ')[2] }
    Write-Host "📋 Versão: $version" -ForegroundColor Cyan
    
    # Testar conversão
    Write-Host "🧪 Testando conversão..." -ForegroundColor Yellow
    
    # Criar arquivo de teste
    $testFile = "test_audio.wav"
    $testContent = [System.Text.Encoding]::ASCII.GetBytes("RIFF    WAVEfmt ")
    [System.IO.File]::WriteAllBytes($testFile, $testContent)
    
    # Tentar conversão
    try {
        ffmpeg -i $testFile -f mp3 -y test_output.mp3 2>$null
        if (Test-Path "test_output.mp3") {
            Write-Host "✅ Conversão de teste bem-sucedida!" -ForegroundColor Green
            Remove-Item "test_output.mp3" -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Host "⚠️ Conversão de teste falhou, mas FFmpeg está instalado" -ForegroundColor Yellow
    }
    
    # Limpar arquivo de teste
    Remove-Item $testFile -ErrorAction SilentlyContinue
    
} else {
    Write-Host "❌ Falha na instalação do FFmpeg" -ForegroundColor Red
    Write-Host "💡 Tente instalar manualmente:" -ForegroundColor Yellow
    Write-Host "   1. Baixe de: https://ffmpeg.org/download.html" -ForegroundColor Cyan
    Write-Host "   2. Extraia para C:\ffmpeg" -ForegroundColor Cyan
    Write-Host "   3. Adicione C:\ffmpeg\bin ao PATH" -ForegroundColor Cyan
}

Write-Host "🎵 Instalação concluída!" -ForegroundColor Green 