"""This script will copy all groups from the current font to all other
open fonts. It deletes existing groups data in the other fonts.
"""

import os
from vanilla.dialogs import message, askYesNo


fonts = AllFonts()

if len(fonts) < 2:
    message("There must be at least two open fonts.")
else:
    current = fonts[0]
    if current.path:
        fontIdentifier = os.path.basename(current.path)
    elif current.info.fullName:
        fontIdentifier = current.info.fullName
    else:
        fontIdentifier = (current.info.familyName + " " + current.info.styleName)
    yes = askYesNo("Copy all groups from ‘%s’ to all other open fonts?" % fontIdentifier,
            "This will delete all existing groups.")
    if yes:
        for dest in fonts[1:]:
            dest.groups.clear()
            for groupName in current.groups.keys():
                dest.groups[groupName] = current.groups[groupName]
