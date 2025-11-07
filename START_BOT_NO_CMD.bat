@echo off
REM Ultimate Fishing Bot v5.0 - Start Without Console Window
REM Este arquivo inicia o bot sem mostrar a janela CMD

REM Usar pythonw.exe (Python sem janela de console)
start "" pythonw "%~dp0main.py"

REM Alternativa: Usar o arquivo .pyw
REM start "" "%~dp0start_bot.pyw"

exit
