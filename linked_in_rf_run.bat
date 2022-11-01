CALL %~dp0venv\Scripts\activate.bat
cd %~dp0
python -m robot -d %~dp0linked_in_rf\ %~dp0linked_in_rf/scrape.robot
pause