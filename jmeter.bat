@ECHO OFF
ECHO.
winpty docker run --rm -it -v %CD%://jmeter -w //jmeter justb4/jmeter %*