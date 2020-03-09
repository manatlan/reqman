@ECHO OFF
cd %~dp0
c:\Python37\Scripts\pyinstaller.exe --noupx --onefile --exclude-module tkinter --icon="reqman.ico" ..\reqman.py 
for /f %%i in ('c:\Python37\python.exe -c "import re,os; print(re.findall('Version +(.+)',os.popen('dist\\reqman.exe').read())[0].strip())"') do set VER=%%i

echo --------------------------------------
echo Build version %VER%
echo --------------------------------------
verpatch.exe dist\reqman.exe %VER% /high /va /pv %VER% /s description "Commandline tool to test a http service with yaml's scenarios (more info : https://github.com/manatlan/reqman)" /s product "ReqMan" /s copyright "GPLv2, 2018" /s company "manatlan"
copy dist\reqman.exe d:\reqman2.exe
pause
