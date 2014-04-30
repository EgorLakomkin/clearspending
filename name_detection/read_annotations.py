#!-*-coding:utf-8-*-
__author__ = 'egor'
import os, codecs
import collections
import re
Annotations = collections.namedtuple('Annotation', ['id', 'type', 'start', 'end', 'name', 'text'])

def filter_annotation_by_grant(annotation):
    return filter_annotation_by_type(annotation, 'Car')


def filter_annotation_by_type(annotation, type ):
    annotation_type = annotation.type
    if annotation_type == type:
        return True
    return False

from itertools import groupby
def splitWithIndices(s, c='\n'):
    p = 0
    for k, g in groupby(s, lambda x:x==c):
        q = p + sum(1 for i in g)
        if not k:
            yield p, q, s[p:q]
        p = q


def get_annotations(data_dir = './../annotation/'):

    txt_files = [os.path.join(data_dir, str(idx)+'.txt') for idx in range(1,3)]
    ann_files = [os.path.join(data_dir, str(idx)+'.ann') for idx in range(1,3)]

    car_brands = codecs.open( './../car_names.txt', 'r', 'utf-8' ).read().split('\n')
    for car_brand in car_brands:
        yield  Annotations(id = 'no' , type='Car',start=0, end=len(car_brand) -1 , name = car_brand, text = car_brand)

    for txt_file, ann_file in zip( txt_files, ann_files ):
        ann_content = codecs.open( ann_file, 'r', 'utf-8' ).read().strip()
        txt_content =  codecs.open( txt_file, 'r', 'utf-8' ).read()

        #txt_content = re.sub('\n+', '\n', txt_content).strip()

        sentence_split = list(splitWithIndices( txt_content ))
        annotated_senteces = {}
        for (sent_start, sent_end, sent) in sentence_split:
            annotated_senteces[ sent_start ] = False

        if len(ann_content) > 0:
            raw_annotations = [ann.split('\t') for ann in  ann_content.split('\n') if len(ann) > 0]
            for annotation in raw_annotations:
                type, start, end = annotation[1].split(' ')
                id = annotation[0]
                if id[0] != 'R':
                    start = int(start)
                    end = int(end)
                    name = txt_content[start:end]

                    for (sent_start, sent_end, sent) in sentence_split:
                        if sent_start <= start <= sent_end:
                            new_ann = Annotations(id =id , type=type,start=int(start), end=int(end), name = name, text = sent)
                            annotated_senteces[ sent_start ] = True
                            yield new_ann
                            break

        for (sent_start, sent_end, sent) in sentence_split:
            if not annotated_senteces[ sent_start ]:
                new_ann = Annotations(id = 'no' , type='Car',start=0, end=0, name = '', text = sent)
                yield new_ann





if __name__ == "__main__":
    annotations = list(  get_annotations() )
    print annotations