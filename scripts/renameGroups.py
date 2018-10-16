"""This script offers a UI to rename groups in a font, using a rename table
that is read from a text file. The text file should contain lines that
contain the original group name and the new group name on a single line,
separated by whitespace (spaces or tabs). Group names cannot contain
whitespace.
"""

import os
from vanilla import *
from vanilla.dialogs import message, getFile


def getFontLabel(font):
    if font.path:
        fontLabel = os.path.basename(font.path)
    elif font.info.fullName:
        fontLabel = font.info.fullName
    else:
        fontLabel = (font.info.familyName + " " + font.info.styleName)
    return fontLabel

def renameGroups(font, table):
    table = dict(table)
    groups = {}
    renameCount = 0
    for groupName in font.groups.keys():
        newGroupName = table.get(groupName, groupName)
        if newGroupName != groupName:
            renameCount += 1
        groups[newGroupName] = font.groups[groupName]
    font.groups.clear()
    for groupName in groups.keys():
        font.groups[groupName] = groups[groupName]
    return renameCount


class RenameGroupsWindow:

    def __init__(self):
        self.replacementTable = None

        self.w = Window((500, 300), "Rename Groups", minSize=(400, 300), autosaveName="RenameGroupsWindow")
        self.w.loadFileButton = Button((20, 20, 120, 20), "Load file...", callback=self.loadFileCallback)
        columnDescriptions = [
            dict(title="original group name", key="original"),
            dict(title="new group name", key="new"),
        ]
        self.w.tableList = List((20, 60, -20, -90), [], columnDescriptions=columnDescriptions,
                allowsSorting=False)
        self.w.allFontsCheckbox = CheckBox((20, -70, -20, 20), "Do all open fonts")
        self.w.doRenameGroups = Button((20, -40, 120, 20), "Rename Groups", callback=self.doRenameCallback)
        self.w.doRenameGroups.enable(False)
        self.w.setDefaultButton(self.w.loadFileButton)
        self.w.open()

    def loadFileCallback(self, sender):
        result = getFile("Hey", parentWindow=self.w, resultCallback=self.getFileResultCallback)

    def getFileResultCallback(self, result):
        if not result:
            return
        with open(result[0], encoding="utf-8") as f:
            lines = f.read().splitlines()
        table = []
        for lineNo, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) != 2:
                    message("Can't extract rename table from file",
                            "Line %s does not have two fields." % lineNo,
                            parentWindow=self.w)
                    return
                originalGroupName, newGroupName = parts
                table.append((originalGroupName, newGroupName))
        msg = self.validateTable(table)
        if msg:
            message("The table is not valid", msg, parentWindow=self.w)
            return
        self.replacementTable = table
        self.w.tableList.set([dict(original=originalGroupName, new=newGroupName) for originalGroupName, newGroupName in table])
        if table:
            self.w.setDefaultButton(self.w.doRenameGroups)
            self.w.doRenameGroups.enable(True)

    @staticmethod
    def validateTable(table):
        original = [o for o, n in table]
        new = [n for o, n in table]
        if len(original) != len(set(original)):
            return "The table contains duplicate original group names."
        if len(new) != len(set(new)):
            return "The table contains duplicate new group names."
        return None

    def doRenameCallback(self, sender):
        table = self.replacementTable
        if not table:
            message("There is no replacement table or replacement table is empty.",
                    parentWindow=self.w)
            return
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
        report = []
        totalCount = 0
        for f in fonts:
            renameCount = renameGroups(f, table)
            totalCount += renameCount
            report.append("%s: %s" % (getFontLabel(f), renameCount))
        report = "\n".join(report)
        message("%s %s renamed" % (totalCount, ["group was", "groups were"][totalCount!=1]),
                report, parentWindow=self.w)


if __name__ == "__main__":
    RenameGroupsWindow()
