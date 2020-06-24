; Run once and if the user is active (and no fullscreen application is present) put up need rest screen
; Use the windows scheduler to run this as often as you want.
; Note that it will check if the user was active the last minute to run a rest break

; Name of games to disable this script for
GAMES := ["ahk_exe Borderlands2.exe", " - S\d+ . E\d+"]
ENERGY_LEVELS_FILE := "E:\ownCloud\Various\personal-data.csv"

; In milliseconds
IDLE_TIME := 60 * 1000
BREAK_TIME := 3.5 * 60 * 1000
; BREAK_TIME := 5 * 1000
START_TIME := A_TickCount
END_TIME := START_TIME + BREAK_TIME
breakProgress := 0
timeLeftLabel := 1
energyLevel := 0

FormatTime, currentDate,, yyyy-MM-dd HH:mm

; User has been active - activate overlay
if (A_TimeIdlePhysical < IDLE_TIME && not isAnyGameRunning()) {
	createAndShowOverlay()
	updateProgressBar()

	sleepTime := -BREAK_TIME
	SetTimer, breakDone, -%BREAK_TIME%
	SetTimer, updateProgressBar, 500
} else {
	ExitApp
}

isAnyGameRunning() {
	global GAMES
	matched := False
	SetTitleMatchMode, RegEx
	for index, game in GAMES {
		if (WinActive(game)) {
			matched := True
			break
		}
	}
	SetTitleMatchMode, 1
	return matched
}

createAndShowOverlay() {
	; Get screen information
	SysGet, SCREEN_WIDTH, 78 
	SysGet, SCREEN_HEIGHT, 79
	SysGet, SCREEN_X, 76
	SysGet, SCREEN_Y, 77

	; Create GUI
	; Location
	ELEMENT_WIDTH := 500
	ELEMENT_X := SCREEN_WIDTH / 2 - ELEMENT_WIDTH / 2
	PROGRESS_HEIGHT := 50
	PROGRESS_Y := SCREEN_HEIGHT / 2 - PROGRESS_HEIGHT / 2
	ELEMENT_Y_OFFSET := 200

	; Time for a break text box
	y := PROGRESS_Y - ELEMENT_Y_OFFSET
	Gui, Font, s42, Roboto
	Gui, Add, Text, C64b5f6 X%ELEMENT_X% Y%y% W%ELEMENT_WIDTH% Center, Time for a break :D

	; Progress Bar
	Gui, Add, Progress, X%ELEMENT_X% Y%PROGRESS_Y% W%ELEMENT_WIDTH% H%PROGRESS_HEIGHT% C64b5f6 vbreakProgress
	GuiControl,, breakProgress, 100

	; Time left
	y := PROGRESS_Y + ELEMENT_Y_OFFSET
	Gui, Add, Text, C64b5f6 X%ELEMENT_X% Y%y% W%ELEMENT_WIDTH% Center VtimeLeftLabel, X:XX

	createEnergyLevelButtons(PROGRESS_Y - ELEMENT_Y_OFFSET)

	; The window
	Gui, Color, 0,0                           ; Black
	Gui, -Caption +ToolWindow ;+E0x20          ; No title bar, No taskbar button, Transparent for clicks
	Gui, Show, X%SCREEN_X% Y%SCREEN_Y% W%SCREEN_WIDTH% H%SCREEN_HEIGHT% ; Show semi-transparent cover window

	WinGet ID, ID, A                         ; ...with HWND/handle ID
	Winset AlwaysOnTop,ON,ahk_id %ID%        ; Keep it always on the top
	WinSet Transparent,220,ahk_id %ID%       ; Set transparency
}

createEnergyLevelButtons(label_y) {
	; Get screen information
	SysGet, SCREEN_WIDTH, 78 
	SysGet, SCREEN_HEIGHT, 79
	SysGet, SCREEN_X, 76
	SysGet, SCREEN_Y, 77

	; Calculate center of third monitor
	CENTER_Y := SCREEN_HEIGHT / 2
	MONITOR_WIDTH := SCREEN_WIDTH / 3
	CENTER_X := MONITOR_WIDTH * 2 + MONITOR_WIDTH / 2
	LABEL_WIDTH := 1000
	LABEL_X := CENTER_X - LABEL_WIDTH / 2

	; Add label "What's your current energy level?"
	Gui, Add, Text, Center C64b5f6 X%LABEL_X% Y%LABEL_Y% W%LABEL_WIDTH%, What is your current energy level?

	; Energy buttons
	COLORS := [ "b71c1c", "C95024", "DB842C", "EDB733", "FFEB3B", "E4EF30", "C8F325",	"ADF719",	"91FB0E",	"76FF03" ]
	Loop, 10 {
		addButton(A_Index, COLORS, CENTER_X, CENTER_Y)
	}
}

addButton(index, colors, xCenter, yCenter) {
	BUTTON_WIDTH := 65
	BUTTON_HEIGHT := 100
	xStart := xCenter - (BUTTON_WIDTH * 10 + BUTTON_WIDTH / 2 * 9) / 2
	button_x := xStart + (index - 1) * BUTTON_WIDTH * 1.5
	button_y := yCenter - BUTTON_HEIGHT / 2
	color := colors[index]
	Gui, Add, Text, Center C%color% X%button_x% Y%button_y% W%BUTTON_WIDTH% H%BUTTON_HEIGHT% GenergyButton%index%Pressed, %index%
}

updateProgressBar() {
	global END_TIME
	global BREAK_TIME

	timeLeft := (END_TIME - A_TickCount) / 10.0

	; Progress Bar
	percentLeft := timeLeft / (BREAK_TIME / 1000.0)
	GuiControl,, breakProgress, %percentLeft%

	; Time left label
	timeLeftSeconds := timeLeft / 100 + 1
	timeLeftMinutes := Floor(timeLeftSeconds / 60)
	timeLeftSeconds := Floor(timeLeftSeconds - 60 * timeLeftMinutes)
	formattedText := Format("{1:d}:{2:02d}", timeLeftMinutes, timeLeftSeconds)
	GuiControl,, timeLeftLabel, %formattedText%
}

breakDone() {
	saveEnergyLevels()
	Gui Destroy
	ExitApp
}

saveEnergyLevels() {
	global energyLevel
	global ENERGY_LEVELS_FILE
	global currentDate
	if (energyLevel > 0) {
		FileAppend, %currentDate%`,energy`,%energyLevel%`n, %ENERGY_LEVELS_FILE%
	}
}

; Make it impossible to close the window
; F4::F3
; LWin::LAlt
; RWin::LAlt
; LCtrl::LAlt
; RCtrl::LAlt

return


energyButton1Pressed:
	energyLevel := 1
	return

energyButton2Pressed:
	energyLevel := 2
	return

energyButton3Pressed:
	energyLevel := 3
	return

energyButton4Pressed:
	energyLevel := 4
	return

energyButton5Pressed:
	energyLevel := 5
	return

energyButton6Pressed:
	energyLevel := 6
	return

energyButton7Pressed:
	energyLevel := 7
	return

energyButton8Pressed:
	energyLevel := 8
	return

energyButton9Pressed:
	energyLevel := 9
	return

energyButton10Pressed:
	energyLevel := 10
	return