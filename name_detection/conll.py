#!-*-coding:utf-8-*-
__author__ = 'egor'
from name_detection.read_annotations import get_annotations
from nltk.tokenize import word_tokenize
import codecs
from utils import preprocessor_text



def write_anotations_to_file(lst_annotation, file_name):

    with codecs.open(file_name, 'w', 'utf-8') as f:
        for annotation in lst_annotation:
            annotation_full_text = annotation.text

            car_name = preprocessor_text(annotation.name)

            annotation_start = annotation_full_text.find(car_name)
            annotation_end = annotation.start + len(car_name)

            full_text_before_annotation = preprocessor_text(annotation_full_text[:annotation_start].strip())

            before_tokens = word_tokenize(full_text_before_annotation)

            for token in before_tokens:
                f.write( token + u' ' + u'O' + u'\n' )

            annotation_tokens = word_tokenize(car_name)
            for idx, token in enumerate(annotation_tokens):
                if idx == 0:
                    label = u'B'
                else:
                    label = u'I'
                f.write( token + u' ' + label + u'\n' )

            full_text_after_annotation =  preprocessor_text(annotation_full_text[annotation_end:]).strip()

            after_tokens = word_tokenize(full_text_after_annotation)

            for token in after_tokens:
                f.write( token + u' ' + u'O' + '\n' )
            f.write( u'\n' )


if __name__ == "__main__":
    import random




    annotations =  list(get_annotations())




    random.shuffle( annotations )


    pos = int(0.8* len(annotations))
    train_annotations = annotations[:pos]
    test_annotations = annotations[pos:]

    write_anotations_to_file( train_annotations, './../data/train.conll' )
    write_anotations_to_file( test_annotations, './../data/test.conll' )

    write_anotations_to_file( annotations, './../data/all.conll' )