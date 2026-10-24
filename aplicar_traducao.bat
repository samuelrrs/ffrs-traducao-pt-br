@echo off
chcp 65001 >nul
setlocal DisableDelayedExpansion
title Aplicar traducao FFRS
echo.
echo === Traducao FFRS ===
echo.

set "ALVO=%~1"
if defined ALVO goto temalvo

echo Arraste a pasta PPSA31544-app0 em cima deste arquivo.
echo Ou cole o caminho dela abaixo.
set /p "ALVO=Pasta app0: "
if defined ALVO goto temalvo

echo Nenhuma pasta informada.
goto fim

:temalvo
echo Alvo: "%ALVO%"
echo.
set "FFRS_FROM_BAT=1"

where python >nul 2>&1
if errorlevel 1 goto trypy
python "%~dp0aplicar_traducao.py" "%ALVO%"
goto depois

:trypy
where py >nul 2>&1
if errorlevel 1 goto nopy
py -3 "%~dp0aplicar_traducao.py" "%ALVO%"
goto depois

:nopy
echo Python 3 nao encontrado.
echo Instale o Python no PC (python.org) e marque "Add python.exe to PATH".
goto fim

:depois
if errorlevel 1 goto falhou
echo.
echo Pronto.
goto fim

:falhou
echo.
echo Falhou. Confira o Python e a pasta PPSA31544-app0.

:fim
echo.
pause
endlocal
