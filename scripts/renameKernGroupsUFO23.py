"""This script can rename kern groups from MetricsMachine style to UFO 3 style
and back.
"""

from vanilla import *
from vanilla.dialogs import message
from renameGroups import renameGroups, getFontLabel


UFO2_LEFT_PREFIX = "@MMK_L_"
UFO2_RIGHT_PREFIX = "@MMK_R_"
UFO3_LEFT_PREFIX = "public.kern1."
UFO3_RIGHT_PREFIX = "public.kern2."


class RenameKernGroupsUFO23:

    def __init__(self):
        self.w = Window((500, 160), "Rename Kern Groups UFO 2 vs 3", autosaveName="RenameKernGroupsUFO23Window")
        options = [
            "Rename @MMK_ to public.kern* (UFO 2 to UFO 3)",
            "Rename public.kern* to @MMK_ (UFO 3 to UFO 2)",
        ]
        self.w.ufo23RadioGroup = RadioGroup((20, 20, -20, 40), options)
        self.w.ufo23RadioGroup.set(0)
        self.w.allFontsCheckbox = CheckBox((20, 80, -20, 20), "Do all open fonts")
        self.w.doRenameGroups = Button((20, 120, 120, 20), "Rename Groups", callback=self.doRenameCallback)
        self.w.setDefaultButton(self.w.doRenameGroups)
        self.w.open()

    def doRenameCallback(self, sender):
        if self.w.allFontsCheckbox.get():
            fonts = AllFonts()
        else:
            f = CurrentFont()
            if f is not None:
                fonts = [f]
            else:
                fonts = []
        if not fonts:
            message("There are no open fonts.",
            parentWindow=self.w)
            return

        direction = self.w.ufo23RadioGroup.get()
        if direction == 0:
            patterns = [(UFO2_LEFT_PREFIX, UFO3_LEFT_PREFIX), (UFO2_RIGHT_PREFIX, UFO3_RIGHT_PREFIX)]
        else:
            patterns = [(UFO3_LEFT_PREFIX, UFO2_LEFT_PREFIX), (UFO3_RIGHT_PREFIX, UFO2_RIGHT_PREFIX)]

        report = []
        totalCount = 0
        for f in fonts:
            table = []
            for groupName in f.groups.keys():
                for original, new in patterns:
                    if groupName.startswith(original):
                        newGroupName = new + groupName[len(original):]
                        table.append((groupName, newGroupName))
            renameCount = renameGroups(f, table)
            totalCount += renameCount
            report.append("%s: %s" % (getFontLabel(f), renameCount))
        report = "\n".join(report)
        message("%s %s renamed" % (totalCount, ["group was", "groups were"][totalCount!=1]),
                report, parentWindow=self.w)


if __name__ == "__main__":
    RenameKernGroupsUFO23()
