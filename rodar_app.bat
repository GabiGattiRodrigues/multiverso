@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Instalando dependencias...
python -m pip install -r requirements.txt
echo Abrindo o Multiverso no navegador...
python -m streamlit run app.py
pause
