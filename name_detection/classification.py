#!-*-coding:utf-8-*-
from utils import preprocessor_text

__author__ = 'egor'


from seqlearn.datasets import load_conll
from seqlearn.perceptron import StructuredPerceptron
from seqlearn.datasets import load_conll
from seqlearn.evaluation import bio_f_score
from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics import accuracy_score
import codecs
from nltk.tokenize import word_tokenize

from features import baseline_features, morphology_features
import os
default_pipeline = [ baseline_features, morphology_features ]

current_dir = os.path.dirname(os.path.realpath(__file__))


def features(sequence, i, pipe_line = default_pipeline):
   for feature_func in pipe_line:
       for feature in feature_func(sequence, i):
           yield feature


def predict_cars(clf, sentence):
    test_f_name = os.path.join( current_dir, './../data/test_ann' )

    sentence = preprocessor_text( sentence )
    tokens = word_tokenize(sentence)
    with codecs.open(test_f_name, 'w', 'utf-8') as f:

        for t in tokens:
            f.write(t + u' ' + u'O' + u'\n')
        f.flush()

    X, y, lengths= load_conll(test_f_name, features)
    y_pred = clf.predict(X, lengths)

    found_cars = []

    current_car = []
    found_car = False
    for idx, token in enumerate( y_pred ):
        t = str(token)
        if t == 'B':

            current_car.append(tokens[idx])
            found_car = True
        elif t == 'I':
            current_car.append(tokens[idx])
        else:
            if found_car:
                found_car = False
                found_cars.append( u' '.join(current_car) )
                current_car = []
    if len(current_car) > 0:
        found_cars.append( u' '.join(current_car) )
    return found_cars

def describe(X, lengths):
    print("{0} sequences, {1} tokens.".format(len(lengths), X.shape[0]))


def train_model():
    print "Loading training data..."
    X_train, y_train, lengths_train = load_conll(os.path.join( current_dir, "./../data/train.conll"), features)
    clf = StructuredPerceptron(verbose=True,max_iter = 10)
    describe(X_train, lengths_train)

    print "Loading test data..."
    X_test, y_test, lengths_test = load_conll(os.path.join( current_dir, "./../data/test.conll"), features)
    describe(X_test, lengths_test)

    print("Training %s" % clf)
    clf.fit(X_train, y_train, lengths_train)

    y_pred = clf.predict(X_test, lengths_test)

    print("Accuracy: %.3f" % (100 * accuracy_score(y_test, y_pred)))
    print("CoNLL F1: %.3f" % (100 * bio_f_score(y_test, y_pred)))
    return clf

if __name__ == "__main__":
    clf = train_model()
    found_cars = predict_cars(clf, u"Автомобиль марки Я ХЗ ЧТО непонятно Toyota Gustavo GT 100 лошадиных сил")
    print found_cars