# Why is this module called chomp? Idk, it's just a random word that's vaguely related to processing things (in the case of chomp, it's food but that's beside the point)

import re

def chomp(gabc: str, tags) -> str:
    mode: str | None = None
    if 'mode:' in gabc:
        mode = gabc[gabc.index('mode:') + 5:gabc.index('\n', gabc.index('mode:'))].strip()
        if mode.endswith(';'):
            mode = mode[:-1]
    gabc = '%%\n' + gabc[re.search(r'\([cf]\d\)', gabc).span()[0]:]
    gabc = gabc.replace('<sp>V/</sp>.', '<v>\\Vbar</v>').replace('<sp>R/</sp>.', '<v>\\Rbar</v>')
    gabc = re.sub('<.?sc>', '', gabc)
    if mode:
        gabc = f'mode:{mode};\n{gabc}'
    if 'antiphona' in tags:
        if '<eu>' in gabc:
            # Notes which define the termination
            euouae = re.sub('<.?eu>', '', re.search(' <eu>.+$', gabc).group())
            # Gabc without the euouae
            gabc = gabc[:gabc.index('<eu>')]

        if 'intonata' in tags:
            return gabc[:gabc.index('*')] + '(::)' + euouae
        elif 'repetita' in tags:
            gabc = gabc.replace('*','')[gabc.index('\n') + 1:]
            firstsyllable = re.search('\\w+\\(', gabc).group()
            gabc = 'initial-style:0;\n' + gabc[:gabc.index('(')].capitalize() + gabc[gabc.index('('):].replace(firstsyllable, firstsyllable.capitalize())
        if not 'paschalis' in tags and ' <i>T. P.</i>' in gabc:
            return gabc[:gabc.index(' <i>T. P.</i>')]
        return gabc

    elif 'responsorium-breve' in tags:
        clef = gabc[:gabc.index(')') + 1]
        incipit = re.search(r'\(..\)\s(.+?)\s\(\W\)\s\*', gabc).group(1)
        response = re.search(r'\s\(\W\)\s\*\s(.+?)\s\(::\)', gabc).group(1)
        verses = re.findall(r'<v>\\Vbar</v>\s(.+?)?=\s\(::\)', gabc)
        verse = verses[0]
        gloria = verses[1]

        return f'{clef} {incipit} *(;) {response} (::) <v>\\Rbar</v> {incipit} (;) {response} (::) <v>\\Vbar</v> {verse} *(;) {response} (::) <v>\\Vbar</v> {gloria} (::) <v>\\Rbar</v> {incipit} (;) {response} (::)'
    else:
        return gabc

