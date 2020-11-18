; Run once and if the user is active (and no fullscreen application is present) put up need rest screen
; Use the windows scheduler to run this as often as you want.
; Note that it will check if the user was active the last minute to run a rest break

; Name of games to disable this script for
GAMES := []
GAMES_WITH_DELAYED_BREAK := ["Minecraft ahk_class GLFW30"]
ENERGY_LEVELS_FILE := "O:\ownCloud\Archived\personal-data.csv"
ICON_FOLDER := "E:\ownCloud\configs\.commands\assets\icons\"
NOTIFICATION_SOUND := "E:\ownCloud\Archived\Sounds\Notification\dong.wav"

; In milliseconds
IDLE_TIME := 60 * 1000
BREAK_TIME := 3.5 * 60 * 1000
; BREAK_TIME := 5 * 1000
BREAK_GAME_DELAY_TIME := 10 * 1000
breakProgress := 0
timeLeftLabel := 1
energyLevel := False
extraCategory := False
extraAction := False

FormatTime, currentDate,, yyyy-MM-dd HH:mm

; Skip if scroll lock is turned on
if (GetKeyState("ScrollLock","T") == 1) {
	ExitApp
}


; User has been active - activate overlay
if (A_TimeIdlePhysical < IDLE_TIME && not isAnyGameWithoutBreakRunning() && not isActiveWindowFullscreen()) {
	; Is a game with break being played, delay break with around 30 seconds
	if (isAnyGameWithBreakRunning()) {
		SoundPlay, %NOTIFICATION_SOUND%, 1
		Sleep, BREAK_GAME_DELAY_TIME
	}
	START_TIME := A_TickCount
	END_TIME := START_TIME + BREAK_TIME

	createAndShowOverlay()
	updateProgressBar()

	sleepTime := -BREAK_TIME
	SetTimer, breakDone, -%BREAK_TIME%
	SetTimer, updateProgressBar, 500
} else {
	ExitApp
}

isAnyGameWithBreakRunning() {
	global GAMES_WITH_DELAYED_BREAK

	matched := False
	SetTitleMatchMode, RegEx
	for index, game in GAMES_WITH_DELAYED_BREAK {
		if (WinActive(game)) {
			matched := True
			break
		}
	}
	SetTitleMatchMode, 1

	return matched
}

isAnyGameWithoutBreakRunning() {
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

isActiveWindowFullscreen() {
	winId := WinExist("A")

	if (!winId)
		return False

	WinGet style, Style, ahk_id %winId%
	WinGetPos ,,, width, height, A

	; 0x800000 is WS_BORDER.
	; 0x20000000 is WS_MINIMIZE.
	; no border and not minimized
	Return ((style & 0x20800000) or height < A_ScreenHeight or width < A_ScreenWidth) ? false : true
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
	Gui, Add, Text, Center C64b5f6 X%LABEL_X% Y%label_y% W%LABEL_WIDTH%, What is your current energy level?

	; Energy buttons
	COLORS := [ "b71c1c", "C95024", "DB842C", "EDB733", "FFEB3B", "E4EF30", "C8F325",	"ADF719",	"91FB0E",	"76FF03" ]
	Loop, 10 {
		addButton(A_Index, COLORS, CENTER_X, CENTER_Y)
	}

	; Extra activity icons
	addIcon(1, "shortWorkout", "fitness_white.png", CENTER_X, CENTER_Y)
	addIcon(2, "foodBreakfast", "beverage_white.png", CENTER_X, CENTER_Y)
	addIcon(3, "foodLunch", "bento_white.png", CENTER_X, CENTER_Y)
	addIcon(4, "foodDinner", "dinner_white.png", CENTER_X, CENTER_Y)
	addIcon(5, "foodHealthySnack", "eco_white.png", CENTER_X, CENTER_Y)
	addIcon(6, "foodSnack", "fastfood_white.png", CENTER_X, CENTER_Y)
	addIcon(7, "foodEveningSnack", "bedtime_white.png", CENTER_X, CENTER_Y)
}

addButton(index, colors, xCenter, yCenter) {
	BUTTON_WIDTH := 65
	BUTTON_HEIGHT := 100
	xStart := xCenter - (BUTTON_WIDTH * 10 + BUTTON_WIDTH / 2 * 9) / 2
	buttonX := xStart + (index - 1) * BUTTON_WIDTH * 1.5
	buttonY := yCenter - BUTTON_HEIGHT / 2
	color := colors[index]
	Gui, Add, Text, Center C%color% X%buttonX% Y%buttonY% W%BUTTON_WIDTH% H%BUTTON_HEIGHT% GenergyButton%index%Pressed, %index%
}

addIcon(index, labelName, fileName, xCenter, yCenter) {
	global ICON_FOLDER
	filePath := ICON_FOLDER . fileName

	ICON_WIDTH := 200
	ICONS := 7
	iconY := yCenter + 200
	xStart := xCenter - (ICON_WIDTH * (ICONS - 0.5)) / 2
	iconX := xStart + (index - 1) * ICON_WIDTH
	; Gui, Add, Text, CWhite X%iconX% Y%iconY%, %labelName%
	; MsgBox, , Location, %filePath%, 4
	Gui, Add, Picture, X%iconX% Y%iconY% G%labelName%, %filePath%
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
	saveEnergyAndExtraAction()
	Gui Destroy
	ExitApp
}

saveEnergyAndExtraAction() {
	global energyLevel
	global extraAction
	global extraCategory
	saveToFile("energy", energyLevel)
	saveToFile(extraCategory, extraAction)
}

saveToFile(category, value) {
	global currentDate
	global ENERGY_LEVELS_FILE

	if (category and value) {
		FileAppend, %currentDate%`,%category%`,%value%`n, %ENERGY_LEVELS_FILE%
	}
}

; Make it impossible to close the window
LWin::Escape
RWin::Escape
LCtrl::Escape
RCtrl::Escape
LAlt::Escape
RAlt::Escape

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

shortWorkout:
	extraCategory := "activity"
	extraAction := "short workout"
	return

foodBreakfast:
	extraCategory := "food"
	extraAction := "breakfast"
	return

foodLunch:
	extraCategory := "food"
	extraAction := "lunch"
	return

foodSnack:
	extraCategory := "food"
	extraAction := "snack"
	return

foodHealthySnack:
	extraCategory := "food"
	extraAction := "healthy snack"
	return

foodDinner:
	extraCategory := "food"
	extraAction := "dinner"
	return

foodEveningSnack:
	extraCategory := "food"
	extraAction := "evening snack"
	return

