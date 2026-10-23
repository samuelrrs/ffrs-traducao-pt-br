@echo off
chcp 65001 >nul
setlocal EnableExtensions
title Aplicar traducao FFRS
echo.
echo === Traducao FFRS ===
echo.

set "ALVO=%~1"
if not defined ALVO (
  echo Arraste a pasta PPSA31544-app0 em cima deste BAT.
  echo Ou cole o caminho dela abaixo.
  set /p "ALVO=Pasta app0: "
)

if not defined ALVO (
  echo Nenhuma pasta informada.
  goto fim
)

echo Alvo: %ALVO%
echo.

where python >nul 2>&1
if %errorlevel%==0 (
  python "%~dp0aplicar_traducao.py" "%ALVO%"
) else (
  where py >nul 2>&1
  if %errorlevel%==0 (
    py -3 "%~dp0aplicar_traducao.py" "%ALVO%"
  ) else (
    echo Python 3 nao encontrado.
    echo Instale o Python no PC (python.org) e marque "Add python.exe to PATH".
    goto fim
  )
)

if errorlevel 1 (
  echo.
  echo Falhou. Instale o Python no PC e use a pasta PPSA31544-app0.
) else (
  echo.
  echo Pronto.
)

:fim
echo.
pause
endlocal
