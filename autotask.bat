@ECHO OFF 
:: This batch file details Windows 10, hardware, and networking configuration.
TITLE My System Info
ECHO Please wait... Checking system information.
:: Section 1: Windows 10 information
ECHO ========================================================================================================
ECHO WINDOWS INFO
ECHO ========================================================================================================
systeminfo | findstr /c:"OS Name"
systeminfo | findstr /c:"OS Version"
systeminfo | findstr /c:"System Type"
:: Section 2: Hardware information.
ECHO ========================================================================================================
ECHO HARDWARE INFO
ECHO ========================================================================================================
systeminfo | findstr /c:"Total Physical Memory"
wmic cpu get name
wmic diskdrive get name,model,size
wmic path win32_videocontroller get name
wmic path win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
:: Section 3: Networking information.
ECHO ========================================================================================================
ECHO NETWORK INFO
ECHO ========================================================================================================
ipconfig | findstr IPv4
ipconfig | findstr IPv6
ECHO ========================================================================================================
:: Section 4: Checking WAMP connection.
ECHO Checking connetion to WAMP server.
SET error=%ERRORLEVEL%
IF %error%=="0" (
 TASKLIST /FI "IMAGENAME eq wampmanager.exe"
 CD /wamp64
 START wampmanager.exe
 GOTO StartWamp
 ) ELSE (
 ECHO ========================================================================================================
 ECHO 				WAMP-MANAGER IS ALREADY RUNNING.
 ECHO				-- Initiating Python app. --
 ECHO ========================================================================================================
 TIMEOUT /T 5
 GOTO StartApp
)
:: Section 5: Connecting to WAMPmanager
: StartWamp
SET error=%ERRORLEVEL%
 CD /wamp64
 START wampmanager.exe
IF %error%=="0" (
 ECHO ======================================================================================================== 
 ECHO 				Initiating WAMPmanager.
 ECHO 				-- Connection established. --
 ECHO ========================================================================================================
 ECHO Loading WAMP MANAGER...
 TIMEOUT /T 10
 GOTO StartApp
) ELSE ( ECHO ...
 ECHO ========================================================================================================
 ECHO 				UNABLED TO START WAMP-MANAGER!!
 ECHO 				-- Termininating auto run. --
 ECHO ========================================================================================================
 TIMEOUT /T 3
 EXIT
)
:: Section 6: Connecting to WAMPmanager
: StartApp
WHERE python
CD /Users/Administrator/Documents/Projects/www/HutHunter/Controller
python explorer.py 


SET error=%ERRORLEVEL%
IF %error%=="0" (
    EXIT ) ELSE (
    ECHO %error%
    TIMEOUT /T 3
    EXIT
    )