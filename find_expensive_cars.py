#!-*-coding:utf-8-*-
from name_detection.features import filter_candidates
from utils import get_files, google_images_by_kw
import codecs
import json
import re
__author__ = 'egor'
import os
import pickle
from name_detection.classification import train_model, predict_cars

notification_dir = './data/notifications/'

available_notifications_for_regnums = [os.path.join(notification_dir,o) for o in os.listdir(notification_dir) if os.path.isdir(os.path.join(notification_dir,o))]
available_notifications_for_regnums = set([ regnum.split('/')[-1] for regnum in  available_notifications_for_regnums])

car_model = train_model()

def get_documents_by_regnum(reg_num):
    notif_dir = os.path.join( notification_dir, reg_num )
    for file in get_files( notif_dir , '*tika.txt'):
        yield file

contracts = pickle.load( open('filtered_contracts','rb') )

target_json_file = open('cars.json', 'w')



def find_cars_by_document( document_file ):
    content = open( document_file ).read().decode('cp1251')

    lines = content.split('\n')

    found_cars = []
    for line in lines:
        line = line.strip()
        line = re.sub('\s+', ' ', line)
        if len(line) > 0:
            cars = predict_cars( car_model, line )

            if len(cars) > 0:
                found_cars.extend( cars )
    return found_cars

def process_cars_by_documents( reg_num ):
    documents_by_regnum = get_documents_by_regnum(reg_num)
    found_cars = []
    for document_file in documents_by_regnum:
        file_cars = find_cars_by_document( document_file )
        if len(file_cars) > 0:
            found_cars.extend( file_cars )
    found_cars = filter(filter_candidates,found_cars)
    return len(found_cars) > 0, found_cars


data = []

for contract in contracts:
    reg_num = str(contract['regNum'].strip())

    products_names = [ prod['name'] for prod in contract['products']['product']    ]

    for product_name in products_names:
        cars = filter(filter_candidates,predict_cars( car_model, product_name ))
        if len(cars) == 0:
            print "Not found car by product", product_name
            if reg_num in available_notifications_for_regnums:

                found_car, found_cars = process_cars_by_documents(reg_num)

                if not found_car:
                    print "Car not found for regnum {0}".format( reg_num )
                else:
                    print "Documentation cars", found_cars[0]
                    contract_id = contract['notif_id']

                    contract_url = "http://clearspending.ru/contract/{0}/".format( reg_num )

                    car_name = found_cars[0]
                    car_picture_lst = list( google_images_by_kw( car_name ) )
                    if len(car_picture_lst) > 0:
                        car_picture = car_picture_lst[0]
                    else:
                        car_picture = "http://www.acsu.buffalo.edu/~rslaine/imageNotFound.jpg"
                    entry = { 'contract_url' : contract_url, 'car_name' : car_name, 'car_picture' : car_picture,
                              'contract_price' : unicode(int(contract['price'])) + u' р.', 'contract_customer' : contract['customer']['fullName']}
                    data.append( entry )

                    print u"Added car", car_name
        else:
            print "Found cars product ", u' '.join(cars)

target_json_file.write( "var jsonObject = " + json.dumps( data ) )
target_json_file.flush()
target_json_file.close()