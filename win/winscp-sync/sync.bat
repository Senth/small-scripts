@echo off
set WINSCP_NAME=WinSCP.exe
set WINSCP_COM="C:\Program Files\WinSCP\WinSCP.com"

:: Only run the synchronization file, if it's not running already
tasklist /FI "IMAGENAME eq %WINSCP_NAME%" 2>NUL | find /I /N "%WINSCP_NAME%">NUL
if not "%ERRORLEVEL%"=="0" (
	%WINSCP_COM% /script=winscpsync.txt
)
