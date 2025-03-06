tell application "Safari" to activate
tell application "System Events"
    tell process "Safari"
        tell menu bar 1
            tell menu bar item "Develop"
                tell menu 1
                    set v to (value of attribute "AXMenuItemMarkChar" of menu item "Allow Remote Automation") as string
                    if (v = "missing value") then
                        click menu item "Allow Remote Automation"
                    end if
                end tell
            end tell
        end tell
    end tell
end tell
quit application "Safari"
