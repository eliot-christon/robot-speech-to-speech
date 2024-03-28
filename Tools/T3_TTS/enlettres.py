import math
import re

# Variables globales
NEL_SEPTANTE = 0x0001
NEL_HUITANTE = 0x0002
NEL_OCTANTE = 0x0004
NEL_NONANTE = 0x0008
NEL_BELGIQUE = NEL_SEPTANTE | NEL_NONANTE
NEL_VVF = NEL_SEPTANTE | NEL_HUITANTE | NEL_NONANTE
NEL_ARCHAIQUE = NEL_SEPTANTE | NEL_OCTANTE | NEL_NONANTE
NEL_SANS_MILLIARD = 0x0010
NEL_AVEC_ZILLIARD = 0x0020
NEL_TOUS_ZILLIONS = 0x0040
NEL_RECTIF_1990 = 0x0100
NEL_ORDINAL = 0x0200
NEL_NIEME = 0x0400

# Le dictionnaire associatif NEL contient toutes les variables utilisées
NEL = {
    '1-99': [
        '', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept',
        'huit', 'neuf', 'dix', 'onze', 'douze', 'treize', 'quatorze',
        'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf',
        'vingt', 'vingt-et-un', 'vingt-deux', 'vingt-trois',
        'vingt-quatre', 'vingt-cinq', 'vingt-six',
        'vingt-sept', 'vingt-huit', 'vingt-neuf',
        'trente', 'trente-et-un', 'trente-deux', 'trente-trois',
        'trente-quatre', 'trente-cinq', 'trente-six',
        'trente-sept', 'trente-huit', 'trente-neuf',
        'quarante', 'quarante-et-un', 'quarante-deux', 'quarante-trois',
        'quarante-quatre', 'quarante-cinq', 'quarante-six',
        'quarante-sept', 'quarante-huit', 'quarante-neuf',
        'cinquante', 'cinquante-et-un', 'cinquante-deux', 'cinquante-trois',
        'cinquante-quatre', 'cinquante-cinq', 'cinquante-six',
        'cinquante-sept', 'cinquante-huit', 'cinquante-neuf',
        'soixante', 'soixante-et-un', 'soixante-deux', 'soixante-trois',
        'soixante-quatre', 'soixante-cinq', 'soixante-six',
        'soixante-sept', 'soixante-huit', 'soixante-neuf',
        'soixante-dix', 'soixante-et-onze', 'soixante-douze', 'soixante-treize',
        'soixante-quatorze', 'soixante-quinze', 'soixante-seize',
        'soixante-dix-sept', 'soixante-dix-huit', 'soixante-dix-neuf',
        'quatre-vingt', 'quatre-vingt-un', 'quatre-vingt-deux', 'quatre-vingt-trois',
        'quatre-vingt-quatre', 'quatre-vingt-cinq', 'quatre-vingt-six',
        'quatre-vingt-sept', 'quatre-vingt-huit', 'quatre-vingt-neuf',
        'quatre-vingt-dix', 'quatre-vingt-onze', 'quatre-vingt-douze', 'quatre-vingt-treize',
        'quatre-vingt-quatorze', 'quatre-vingt-quinze', 'quatre-vingt-seize',
        'quatre-vingt-dix-sept', 'quatre-vingt-dix-huit', 'quatre-vingt-dix-neuf'
    ],

    'illi': ['', 'm', 'b', 'tr', 'quatr', 'quint', 'sext'],
    'maxilli': 0,
    'de_maxillions': '',

    'soixante-dix': False,
    'quatre-vingt': False,
    'quatre-vingt-dix': False,
    'zillions': False,
    'zilliard': 1,
    'rectif': False,
    'ordinal': False,

    'separateur': '-'
}

# Calcul du maxilli et de de_maxillions
NEL['maxilli'] = len(NEL['illi']) - 1
NEL['de_maxillions'] = " de {}illions".format(NEL['illi'][NEL['maxilli']])


def enlettres_options(options, separateur=None):
    global NEL

    if options is not None:
        NEL['soixante-dix'] = bool(options & NEL_SEPTANTE)
        NEL['quatre-vingt-dix'] = bool(options & NEL_NONANTE)
        NEL['zillions'] = bool(options & NEL_TOUS_ZILLIONS)
        NEL['zilliard'] = 2 if options & NEL_AVEC_ZILLIARD else 0 if options & NEL_SANS_MILLIARD else 1
        NEL['rectif'] = bool(options & NEL_RECTIF_1990)
        NEL['ordinal'] = 'nieme' if options & NEL_NIEME else bool(options & NEL_ORDINAL)

    if separateur is not None:
        NEL['separateur'] = separateur


def enlettres_par3(par3):
    global NEL

    if par3 == 0:
        return ''

    centaine = math.floor(par3 / 100)
    par2 = par3 % 100
    dizaine = math.floor(par2 / 10)

    # On traite à part les particularités du français de référence
    # 'soixante-dix', 'quatre-vingts' et 'quatre-vingt-dix'.
    nom_par2 = None
    if dizaine == 7 and not NEL['soixante-dix']:
        if par2 == 71:
            nom_par2 = 'soixante-et-onze'
        else:
            nom_par2 = 'soixante-' + NEL['1-99'][par2 - 60]
    elif dizaine == 8 and not NEL['quatre-vingt']:
        if par2 == 80:
            nom_par2 = 'quatre-vingts'
        else:
            nom_par2 = 'quatre-vingt-' + NEL['1-99'][par2 - 80]
    elif dizaine == 9 and not NEL['quatre-vingt-dix']:
        nom_par2 = 'quatre-vingt-' + NEL['1-99'][par2 - 80]
    
    if nom_par2 is None:
        nom_par2 = NEL['1-99'][par2]

    # Après les dizaines et les unités, il reste à voir les centaines
    if centaine == 0:
        return nom_par2
    elif centaine == 1:
        return "cent-" + nom_par2

    # Assertion : centaine = 2 .. 9
    nom_centaine = NEL['1-99'][centaine]
    if par2 == 0:
        return nom_centaine + "-cents"
    return nom_centaine + "-cent-" + nom_par2


def enlettres_zilli(idx):
    # Noms des 0ème à 9ème zillions
    petit = ['', 'm', 'b', 'tr', 'quatr', 'quint', 'sext']
    # Composantes des 10ème à 999ème zillions
    unite = ['<', 'un<', 'duo<', 'tre<sé', 'quattuor<', 'quin<', 'se<xsé', 'septe<mné', 'octo<', 'nove<mné']
    dizaine = ['', 'né>déci<', 'ms>viginti<', 'ns>triginta<', 'ns>quadraginta<', 'ns>quinquaginta<', 'n�>sexaginta<', 'n�>septuaginta<', 'mxs>octoginta<', '�>nonaginta<']
    centaine = ['>', 'nxs>cent', 'n�>ducent', 'ns>trécent', 'ns>quadringent', 'ns>quingent', 'n�>sescent', 'n�>septingent', 'mxs>octingent', '�>nongent']

    # Règles d'assimilation aux préfixes latins
    recherche = [
        '/<[a-zé]*?([a-zé])[a-zé]*\\1[a-zé]*>/',  # (1)
        '/<[a-zé]*>/',  # (2)
        '/eé/',  # (3)
        '/[ai]illi/'  # (4)
    ]
    remplace = ['\\1', '', 'é', 'illi']

    nom = ''
    while idx > 0:
        p = idx % 1000
        idx = math.floor(idx / 1000)

        if p < 10:
            nom = petit[p] + 'illi' + nom
        else:
            nom = unite[p % 10] + dizaine[math.floor(p / 10) % 10] + centaine[math.floor(p / 100)] + 'illi' + nom

    # Utilisation des expressions régulières pour les règles d'assimilation
    for i in range(len(recherche)):
        nom = re.sub(recherche[i], remplace[i], nom)

    return nom


def enlettres_illions(idx):
    if idx == 0:
        return ''

    global NEL

    if NEL['zillions']:
        return enlettres_zilli(idx) + 'ons'

    suffixe = ''
    while idx > NEL['maxilli']:
        idx -= NEL['maxilli']
        suffixe += NEL['de_maxillions']
    
    return NEL['illi'][idx] + 'illions' + suffixe


def enlettres_avec_illiards(idx):
    global NEL

    if idx == 0:
        return False
    
    if NEL['zilliard'] == 0:
        return False
    elif NEL['zilliard'] == 2:
        return True
    
    return idx == 1


def enlettres(nombre, options=None, separateur=None):
    global NEL

    if options is not None or separateur is not None:
        NELsave = NEL.copy()
        enlettres_options(options, separateur)
        nom = enlettres(nombre)
        NEL = NELsave
        return nom
    
    # compter le nombre de 0 au début du nombre
    nb_zeros = 0
    for chiffre in nombre:
        if chiffre == '0':
            nb_zeros += 1
        else:
            break

    # Ne garder que les chiffres, puis supprimer les 0 du début
    nombre = ''.join(filter(str.isdigit, nombre)).lstrip('0')

    if nombre == '':
        if NEL['ordinal'] == 'nieme':
            return 'zéroième'
        else:
            return 'zéro' if nb_zeros == 0 else 'zéro-' + 'zéro-' * (nb_zeros - 1) + 'ième'

    table_noms = {}
    idx = 0
    while nombre != '':
        par6 = int(nombre[-6:]) if len(nombre) >= 6 else int(nombre)
        nombre = nombre[:-6] if len(nombre) >= 6 else ''

        if par6 == 0:
            continue

        nom_par3_sup = enlettres_par3(par6 // 1000)
        nom_par3_inf = enlettres_par3(par6 % 1000)

        illions = enlettres_illions(idx)

        if enlettres_avec_illiards(idx):
            if nom_par3_inf != '':
                table_noms[illions] = nom_par3_inf
            if nom_par3_sup != '':
                illiards = illions.replace('illion', 'illiard', 1)
                table_noms[illiards] = nom_par3_sup
        else:
            if nom_par3_sup == '':
                nom_par6 = nom_par3_inf
            elif nom_par3_sup == 'un':
                nom_par6 = 'mille-' + nom_par3_inf
            else:
                nom_par3_sup = re.sub(r'(vingt|cent)s', r'\1', nom_par3_sup)
                nom_par6 = nom_par3_sup + '-mille-' + nom_par3_inf
            
            table_noms[illions] = nom_par6
        
        idx += 1

    nom_enlettres = ''
    for nombre, nom in table_noms.items():
        if nom_enlettres == '':
            nom_enlettres = nom
        else:
            nom_enlettres = nom + '-' + nombre + '-' + nom_enlettres
            
    if NEL['ordinal'] is False:
        return nom_enlettres

    nom_enlettres = re.sub(r'(cent|vingt|illion|illiard)s', r'\1', nom_enlettres)

    if NEL['ordinal'] == 'nieme':
        if nom_enlettres == 'un':
            return 'premier'
        elif nom_enlettres[-1] == 'e':
            return nom_enlettres[:-1] + 'ième'
        elif nom_enlettres[-1] == 'f':
            return nom_enlettres[:-1] + 'vième'
        elif nom_enlettres[-1] == 'q':
            return nom_enlettres + 'uième'
        else:
            return nom_enlettres + 'ième'

    return nom_enlettres



if __name__ == "__main__":

    num_to_test = ["5907805", "7", "70", "71", "456789745013654897485614563", "007"]

    for num in num_to_test:
        print("enlettres('{}')".format(num) + " -> " + enlettres(num))