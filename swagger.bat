@ECHO OFF
ECHO.
winpty docker run --rm -it --env GOPATH=/go -v %CD%://go/src -w //go/src quay.io/goswagger/swagger:v0.25.0 %*