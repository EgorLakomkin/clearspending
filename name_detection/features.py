#!-*-coding:utf-8-*-
__author__ = 'egor'
import re
import codecs, os


current_dir = os.path.dirname(os.path.realpath(__file__))


car_brands = set([line.strip().lower() for line in codecs.open( os.path.join(current_dir,'./../car_brands.txt'), 'r', 'utf-8').readlines() if len(line.strip()) > 0])



def extract_suffix(token, size = 2):
    return token[ -size : ]

def extract_prefix(token, size = 2):
    return token[ : size]

def get_type(token):
    T = (
        'AllUpper', 'AllDigit', 'AllSymbol',
        'AllUpperDigit', 'AllUpperSymbol', 'AllDigitSymbol',
        'AllUpperDigitSymbol',
        'InitUpper',
        'AllLetter',
        'AllAlnum'
        )
    R = set(T)

    for i in range(len(token)):
        c = token[i]
        if c.isupper():
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllDigitSymbol')
        elif c.isdigit() or c in (',', '.'):
            R.discard('AllUpper')
            R.discard('AllSymbol')
            R.discard('AllUpperSymbol')
            R.discard('AllLetter')
        elif c.islower():
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllUpperDigit')
            R.discard('AllUpperSymbol')
            R.discard('AllDigitSymbol')
            R.discard('AllUpperDigitSymbol')
        else:
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllUpperDigit')
            R.discard('AllLetter')
            R.discard('AllAlnum')

        if i == 0 and not c.isupper():
            R.discard('InitUpper')

    for tag in T:
        if tag in R:
            yield tag

def morphology_features(sequence, i):


    current_token = sequence[i]
    current_token = current_token.lower()

    suffix_2 = extract_suffix(current_token, size = 2)
    suffix_3 = extract_suffix(current_token, size = 3)
    suffix_4 = extract_suffix(current_token, size = 4)

    prefix_2 = extract_prefix(current_token, size = 2)
    prefix_3 = extract_prefix(current_token, size = 3)
    prefix_4 = extract_prefix(current_token, size = 4)

    yield "morph_suffix_2" + "=" + suffix_2
    yield "morph_suffix_3" + "=" + suffix_3
    yield "morph_suffix_4" + "=" + suffix_4

    for j in range(-5,5):
        if j != 0 and i + j >=0 and i + j < len(sequence):
            for size in [2,3,4]:
                window_token = sequence[i + j].lower()
                prefix_window_j = extract_prefix( window_token  , size = size)
                suffix_window_j =  extract_suffix( window_token  , size = size)
                yield "morph_prefix_window_" + str(j) + "_size" + str(size)+ "=" + prefix_window_j
                yield "morph_suffix_window_" + str(j) + "_size" + str(size)+ "=" + suffix_window_j

    yield "morph_prefix_2" + "=" + prefix_2
    yield "morph_prefix_3" + "=" + prefix_3
    yield "morph_prefix_4" + "=" + prefix_4

    rus_match = re.match(u"[а-яА-Яёё]+", current_token)
    if rus_match is not None:
        yield 'AllRussian'

    eng_match = re.match(u"[a-zA-Z]+", current_token)

    if current_token in car_brands:
        yield 'CarBrand'

    if len(current_token) <= 3:
        yield 'ShortToken'

    if len( current_token ) >=3 and len( current_token ) <=10:
        yield 'NormalToken'

    if len(current_token) > 10:
        yield 'LongToken'

    if current_token in ['.', ',']:
        yield 'PunktToken'

    if eng_match is not None:
        yield 'AllEnglish'

    for type in get_type( sequence[i] ):
        yield type


def filter_candidates(car):
    if len(car.split()) < 2:
        return False
    first_token = car.split()[0].lower()
    print u"Filtering",  first_token
    if first_token in car_brands:
        print "Found brand"
        return True
    return False


def baseline_features(sequence, i):

    if i == 0:
        yield'__BOS__'
    elif i == len(sequence) - 1:
        yield '__EOS__'

    yield "word=" + sequence[i - 1].lower()

    if i > 0:
        yield "word-1=" + sequence[i - 1].lower()

    if i + 1 < len(sequence):
        yield "word+1=" + sequence[i + 1].lower()