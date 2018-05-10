import makeUC2INT_kerningText
from makeUC2INT_kerningText import template

letters = ['/zero.lf ', '/one.lf ', '/two.lf ', '/three.lf ', '/four.lf ', '/five.lf ', '/six.lf ', '/seven.lf ', '/eight.lf ', '/nine.lf ', '/zero.osf ', '/one.osf ', '/two.osf ', '/three.osf ', '/four.osf ', '/five.osf ', '/six.osf ', '/seven.osf ', '/eight.osf ', '/nine.osf ']

if __name__ == '__main__':
    for eachLetter in letters:
        print(template.format(letter=eachLetter))