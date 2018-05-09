letters = ['O', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Æ', '&']
template = '''II({letter})II){letter}(II[{letter}]II
II]{letter}[II{{{letter}}}II}}{letter}{{II
II/parenleft.case {letter}/parenright.case II/parenright.case {letter}/parenleft.case II/bracketleft.case {letter}/bracketright.case II
II/bracketright.case {letter}/bracketleft.case II/braceleft.case {letter}/braceright.case II/braceright.case {letter}/braceleft.case II
II\\{letter}//II//{letter}\\II
II‹{letter}›II›{letter}‹II-{letter}-II
II/guilsinglleft.case {letter}/guilsinglright.case II/guilsinglright.case {letter}/guilsinglleft.case II/hyphen.case {letter}/hyphen.case II
II“{letter}”II"{letter}"II
II.{letter}.II:{letter}:II·{letter}·II
II•{letter}•II*{letter}*II°{letter}°II'''

for eachLetter in letters:
    print(template.format(letter=eachLetter))