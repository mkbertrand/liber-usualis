# Why is this module called chomp? Idk, it's just a random word that's vaguely related to processing things (in the case of chomp, it's food but that's beside the point)

import re

def chomp(gabc: str, tags) -> str:

    gabc = gabc.replace(r'<v>\greheightstar</v>','*')
    mode: str | None = None
    if 'mode:' in gabc:
        mode = gabc[gabc.index('mode:') + 5:gabc.index('\n', gabc.index('mode:'))].strip()
        if mode.endswith(';'):
            mode = mode[:-1]

    # Remove all commented text before the beginning of the content
    gabc = '%%\n' + gabc[re.search(r'\([cf]\d\)', gabc).span()[0]:]

    # Replace gregobase's preferred versicle and response with libu-friendly versions
    gabc = gabc.replace('<sp>V/</sp>.', '<v>\\Vbar</v>').replace('<sp>R/</sp>.', '<v>\\Rbar</v>')

    gabc = re.sub('<.?sc>', '', gabc)
    # Remove in-text comments
    gabc = re.sub(r'\[.*?\]', '', gabc)

    if mode:
        gabc = f'mode:{mode};\n{gabc}'
    if 'deus-in-adjutorium' in tags:
        return gabc[0:re.search(r'\(Z\-?\)', gabc).start()]

    elif 'antiphona' in tags:
        euouae = ''
        if '<eu>' in gabc:
            # Notes which define the termination
            euouae = re.sub('<.?eu>', '', re.search(r' <eu>.+', gabc).group()).strip()
            # Gabc without the euouae
            gabc = gabc[:gabc.index('<eu>')]

        if not 'paschalis' in tags and ' <i>T. P.</i>' in gabc:
            gabc = gabc[:gabc.index(' <i>T. P.</i>')]

        if not 'septuagesima' in tags and '<i>Post Septuag.</i>' in gabc:
            gabc = gabc[:gabc.index('<i>Post Septuag.</i>')]

        if 'intonata' in tags:
            return gabc[:gabc.index('*')] + '(::)' + euouae
        elif {'commemoratio', 'repetita', 'suffragium'}.isdisjoint(tags):
            gabc = gabc + euouae
        else:
            gabc = gabc.replace('*','')[gabc.index('\n') + 1:]
            firstsyllable = re.search(r'\w+\(', gabc).group()
            gabc = 'initial-style:0;\n' + gabc[:gabc.index('(')].capitalize() + gabc[gabc.index('('):].replace(firstsyllable, firstsyllable.capitalize())
        return gabc

    elif 'responsorium-breve' in tags:
        clef = gabc[:gabc.index(')') + 1]
        incipit = re.search(r'\(..\)\s(.+?)\s\(\W\)\s\*', gabc).group(1)
        response = re.search(r'\s\(\W\)\s\*\s(.+?)\s\(::\)', gabc).group(1)
        verses = re.findall(r'<v>\\Vbar</v>\s(.+?)?\s\(::\)', gabc)
        verse = verses[0]
        gloria = verses[1]

        return f'{clef} {incipit} *(;) {response} (::) <v>\\Rbar</v> {incipit} (;) {response} (::) <v>\\Vbar</v> {verse} *(;) {response} (::) <v>\\Vbar</v> {gloria} (::) <v>\\Rbar</v> {incipit} (;) {response} (::)'
    else:
        return gabc

