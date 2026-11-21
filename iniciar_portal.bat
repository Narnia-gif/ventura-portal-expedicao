@echo off
REM Ventura Biomedica - Portal Comercial e Expedicao
REM Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis
REM Clique duas vezes para abrir a tela em http://localhost:8000
cd /d "%~dp0"
call :preparar
if errorlevel 1 goto :fim
echo.
echo Abrindo o navegador em http://localhost:8000 ...
echo Para desligar o portal, feche esta janela ou aperte Ctrl+C.
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000"
".venv\Scripts\python.exe" -m portal.servidor
:fim
pause
exit /b

:preparar
if exist ".venv\Scripts\python.exe" goto :temvenv
set "PY="
for /d %%D in ("%APPDATA%\uv\python\cpython-*") do if exist "%%D\python.exe" set "PY=%%D\python.exe"
if not defined PY py -c "import sys" >nul 2>nul && set "PY=py"
if not defined PY python -c "import sys" >nul 2>nul && set "PY=python"
if not defined PY (
  echo [ERRO] Python nao encontrado. Instale em python.org marcando "Add python.exe to PATH".
  exit /b 1
)
echo Criando o ambiente .venv - so na primeira vez...
"%PY%" -m venv .venv
if errorlevel 1 exit /b 1
:temvenv
".venv\Scripts\python.exe" -c "import pytest" >nul 2>nul
if errorlevel 1 (
  echo Instalando o pytest - so na primeira vez, precisa de internet...
  ".venv\Scripts\python.exe" -m pip install pytest
)
exit /b 0
