set file_name=python-3.8.10-embed-win32.zip
set embed_python_url=https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-win32.zip
set get_pip_url=https://bootstrap.pypa.io/pip/3.8/get-pip.py

set file_pth=python38._pth
set out_7z_name=python-3.8.10-embed-win32_PyQt5.7z


rem download
curl -L -O %embed_python_url%
curl -L -O %get_pip_url%

rem extract
7z x %file_name% -opython_embed

rem  *._pth
rem import site
echo import site>>python_embed\%file_pth%


rem get-pip
python_embed\python.exe get-pip.py

rem install packages
python_embed\python.exe -m pip install --upgrade pip setuptools wheel
python_embed\python.exe -m pip install "qtpy==2.4.3"
python_embed\python.exe -m pip install PyQt5

rem run_Jkui.bat
echo @echo off>run_Jkui.bat
echo CD /D ^"^%^~dp0^">>run_Jkui.bat
echo start python_embed\pythonw.exe Jkui>>run_Jkui.bat

7z a -t7z -mx=9 "%out_7z_name%" python_embed  qss  JKui  run_Jkui.bat   LICENSE   folders   .JKui

