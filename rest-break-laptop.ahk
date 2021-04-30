; Run once and if the user is active (and no fullscreen application is present) put up need rest screen
; Use the windows scheduler to run this as often as you want.
; Note that it will check if the user was active the last minute to run a rest break

; Name of games to disable this script for (RegEx mode)
APPS_WITHOUT_BREAK := ["Slack \\| Slack call", "(Meeting) \\| Microsoft Teams"]
GAMES_WITH_DELAYED_BREAK := ["Minecraft ahk_class GLFW30"]
OWNCLOUD_DIR := "C:\Users\matmag\ownCloud\"
PERSONAL_DATA_FILE := OWNCLOUD_DIR . "configs\personal-data.csv"
ICON_FOLDER := OWNCLOUD_DIR . "configs\.commands\assets\icons\"
NOTIFICATION_SOUND := OWNCLOUD_DIR . "Dev\Notification\dong.wav"

BREAK_TIME := 3.5 * 60 * 1000
; BREAK_TIME := 10 * 1000
BREAK_GAME_DELAY_TIME := 10 * 1000
breakProgress := 0
timeLeftLabel := 1
energyLevel := False
extraCategory := False
extraAction := False
startTime := A_TickCount
running := False

SetTimer, main, 1000

main() {
	global startTime
	global endTime
	global BREAK_TIME
	global currentDate
	global running
	global energyLevel
	global extraCategory
	global extraAction

	if (shouldActivate()) {
		startTime := A_TickCount
		endTime := startTime + BREAK_TIME

		createAndShowOverlay()
		updateProgressBar()

		sleepTime := -BREAK_TIME
		running := True
		energyLevel := False
		extraCategory := False
		extraAction := False
		SetTimer, breakDone, -%BREAK_TIME%
		SetTimer, updateProgressBar, 500
		FormatTime, currentDate,, yyyy-MM-dd HH:mm
	}
}

shouldActivate() {
	return isPauseEnabled() 
		and isPauseTime() 
		and not isAnyAppWithoutBreakRunning()
		and not isActiveWindowFullscreen()
}

isPauseEnabled() {
	RegRead, turnedOn, HKCU\Software\RestBreak, TurnedOn
	return turnedOn = 1
}

isPauseTime() {
	global running

	if (not running) {
		FormatTime, minutes,, mm
		if (minutes == "00" || minutes == "30") {
			return True
		}
	}
	return False
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

isAnyAppWithoutBreakRunning() {
	global APPS_WITHOUT_BREAK

	matched := False
	SetTitleMatchMode, RegEx
	for index, app in APPS_WITHOUT_BREAK {
		if (WinExist(app)) {
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

	xCenter := SCREEN_WIDTH / 2
	yCenter := SCREEN_HEIGHT / 2
	progressWidth := 500
	progressHeight := 50

	; Location of elements depending on screen size
	; (Only laptop)
	if (SCREEN_WIDTH == 1920) {
		elementOffsetY := 150
		progressY := yCenter - progressHeight - SCREEN_HEIGHT / 6
		energyY := progressY + elementOffsetY * 2
		energyX := xCenter
	} else if (SCREEN_WIDTH == 7680) {
		elementOffsetY := 200
		monitorWidth := SCREEN_WIDTH / 3
		progressY := yCenter - progressHeight
		energyY := progressY - elementOffsetY
		energyX := xCenter + monitorWidth
	}

	progressX := xCenter - progressWidth / 2
	progressHeaderY := progressY - elementOffsetY
	progressTimeLeftY := progressY + elementOffsetY

	; Create GUI
	; Time for a break text box
	Gui, Font, s42, Roboto
	Gui, Add, Text, C64b5f6 X%progressX% Y%progressHeaderY% W%progressWidth% Center, Time for a break :D

	; Progress Bar
	Gui, Add, Progress, X%progressX% Y%progressY% W%progressWidth% H%progressHeight% C64b5f6 vbreakProgress
	GuiControl,, breakProgress, 100

	; Time left
	Gui, Add, Text, C64b5f6 X%progressX% Y%progressTimeLeftY% W%progressWidth% Center VtimeLeftLabel, X:XX

	createEnergyLevelButtons(energyX, energyY, elementOffsetY)

	; Transparent window overlay
	Gui, Color, 0,0                           ; Black
	Gui, -Caption +ToolWindow ;+E0x20          ; No title bar, No taskbar button, Transparent for clicks
	Gui, Show, X%SCREEN_X% Y%SCREEN_Y% W%SCREEN_WIDTH% H%SCREEN_HEIGHT% ; Show semi-transparent cover window

	WinGet ID, ID, A                         ; ...with HWND/handle ID
	Winset AlwaysOnTop,ON,ahk_id %ID%        ; Keep it always on the top
	WinSet Transparent,220,ahk_id %ID%       ; Set transparency
}

createEnergyLevelButtons(xCenter, energyY, elementOffsetY) {
	labelWidth := 1000
	energyX := xCenter - labelWidth / 2

	; Add label "What's your current energy level?"
	Gui, Add, Text, Center C64b5f6 X%energyX% Y%energyY% W%labelWidth%, What is your current energy level?

	; Energy buttons
	COLORS := [ "b71c1c", "C95024", "DB842C", "EDB733", "FFEB3B", "E4EF30", "C8F325",	"ADF719",	"91FB0E",	"76FF03" ]
	Loop, 10 {
		addButton(A_Index, COLORS, xCenter, energyY + elementOffsetY)
	}

	iconY := energyY + elementOffsetY * 1.5

	; Extra activity icons
	addIcon(1, "shortWorkout", "fitness_white.png", xCenter, iconY, elementOffsetY)
	addIcon(2, "foodBreakfast", "beverage_white.png", xCenter, iconY, elementOffsetY)
	addIcon(3, "foodLunch", "bento_white.png", xCenter, iconY, elementOffsetY)
	addIcon(4, "foodDinner", "dinner_white.png", xCenter, iconY, elementOffsetY)
	addIcon(5, "foodHealthySnack", "eco_white.png", xCenter, iconY, elementOffsetY)
	addIcon(6, "foodSnack", "fastfood_white.png", xCenter, iconY, elementOffsetY)
	addIcon(7, "foodEveningSnack", "bedtime_white.png", xCenter, iconY, elementOffsetY)
}

addButton(index, colors, xCenter, yCenter) {
	buttonWidth := 65
	buttonHeight := 100
	xStart := xCenter - (buttonWidth * 10 + buttonWidth / 2 * 9) / 2
	buttonX := xStart + (index - 1) * buttonWidth * 1.5
	buttonY := yCenter - buttonHeight / 2
	color := colors[index]
	Gui, Add, Text, Center C%color% X%buttonX% Y%buttonY% W%buttonWidth% H%buttonHeight% GenergyButton%index%Pressed, %index%
}

addIcon(index, labelName, fileName, xCenter, iconY, elementOffsetY) {
	global ICON_FOLDER
	filePath := ICON_FOLDER . fileName

	iconWidth := elementOffsetY
	iconCount := 7
	xStart := xCenter - (iconWidth * (iconCount - 0.5)) / 2
	iconX := xStart + (index - 1) * iconWidth
	; Gui, Add, Text, CWhite X%iconX% Y%iconY%, %labelName%
	; MsgBox, , Location, %filePath%, 4
	Gui, Add, Picture, X%iconX% Y%iconY% G%labelName%, %filePath%
}

updateProgressBar() {
	global endTime
	global BREAK_TIME

	timeLeft := (endTime - A_TickCount) / 10.0

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
	global running
	running := False
	Gui Destroy
	saveEnergyAndExtraAction()
}

saveEnergyAndExtraAction() {
	global energyLevel
	global extraAction
	global extraCategory

	; We want to pause and save a bit later as the server updates and syncs files every XX:03
	Sleep, 5 * 60 * 1000

	saveToFile("energy", energyLevel)
	saveToFile(extraCategory, extraAction)
}

saveToFile(category, value) {
	global currentDate
	global PERSONAL_DATA_FILE

	if (category and value) {
		FileAppend, %currentDate%`,%category%`,%value%`n, %PERSONAL_DATA_FILE%
	}
}

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

; Make it impossible to close the window
#If running
	LWin::Escape
	RWin::Escape
	LCtrl::Escape
	RCtrl::Escape
	LAlt::Escape
	RAlt::Escape
return
