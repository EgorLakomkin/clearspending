#!-*-coding:utf-8-*-
__author__ = 'UM'
import pickle
import json
import os
import requests
import lxml.html
from selenium import webdriver
import time




current_dir = "F:\\tenders\\"

cache_file = os.path.join( current_dir, 'cache.dat' )
if os.path.exists( cache_file ):
    cache = pickle.load( open( cache_file, 'rb' ) )
else:
    cache = { }

def get_driver_by_notification(download_dir, regnum):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)

    dir_dl = os.path.abspath( os.path.join( download_dir, regnum) )
    print "DL dir", dir_dl
    if not os.path.exists(dir_dl):
        os.makedirs( dir_dl )

    fp.set_preference("browser.download.dir", dir_dl )

    fp.set_preference("browser.download.downloadDir", dir_dl)
    fp.set_preference("browser.download.defaultFolder", dir_dl)
    fp.set_preference("browser.helperApps.alwaysAsk.force",False)


    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-msdos-program,"
                                                                " application/x-unknown-application-octet-stream, "
                                                                "application/vnd.ms-powerpoint, application/excel,"
                                                                " application/vnd.ms-publisher, "
                                                                "application/x-unknown-message-rfc822,"
                                                                " application/vnd.ms-excel, application/msword,"
                                                                " application/x-mspublisher, application/x-tar,"
                                                                " application/zip, application/x-gzip,"
                                                                "application/x-stuffit,application/vnd.ms-works, "
                                                                "application/powerpoint, application/rtf,"
                                                                " application/postscript, application/x-gtar, "
                                                                "video/quicktime, video/x-msvideo, video/mpeg,"
                                                                " audio/x-wav, audio/x-midi, audio/x-aiff,"
                                                                "application/msword,application/doc, appl/text, application/vnd.msword, application/vnd.ms-word,"
                                                                "application/winword, application/word, application/x-msw6, application/x-msword,application/download");

    new_driver = webdriver.Firefox(firefox_profile=fp)
    return new_driver, dir_dl

def get_order_documents_url(order_id):
    return "http://zakupki.gov.ru/pgz/public/action/orders/info/order_document_list_info/show?notificationId=" + order_id

def get_order_documents_url_by_contract_id(contract_id):
    return "http://zakupki.gov.ru/pgz/public/action/contracts/info/document_list_info/show?contractInfoId={0}&source=epz".format( contract_id )

def get_documents_by_notification(content):
    lxml_doc = lxml.html.fromstring(content)

    onclicks = lxml_doc.xpath("//a/@onclick")
    doc_ids = []
    try:
        for onclick in onclicks:
            if 'downloadDocument' in onclick:
                start_idx = onclick.find('downloadDocument(')
                end_idx = onclick.find(');', start_idx)

                id = onclick[ start_idx + len( 'downloadDocument(' ) : end_idx ]
                doc_ids.append( id )
    except:
        pass
    return doc_ids

def get_documents_ids_by_contract(content):
    lxml_doc = lxml.html.fromstring(content)

    onclicks = lxml_doc.xpath("//a/@onclick")
    doc_ids = []
    try:
        for onclick in onclicks:
            if 'downloadContractDocument' in onclick:
                start_idx = onclick.find('downloadContractDocument(')
                end_idx = onclick.find(');', start_idx)

                id = onclick[ start_idx + len( 'downloadContractDocument(' ) : end_idx ]
                doc_ids.append( id )
    except:
        pass
    return doc_ids

def get_document_url_by_id(doc_id):
    return "http://zakupki.gov.ru/pgz/documentdownload?documentId=" + doc_id

def get_document_by_contract_id(doc_id):
    return "http://zakupki.gov.ru/pgz/documentdownload?documentId={0}&docType=contract_document".format( doc_id )


def get_content(url):
    driver.get(url)
    return driver.page_source

def get_notification_printform_url(notification_id):
    return "http://zakupki.gov.ru/pgz/printForm?type=NOTIFICATION&id=" + str(notification_id)

def get_contract_info_by_contract_id(contract_id):
    return "http://zakupki.gov.ru/pgz/public/action/contracts/info/common_info/show?contractInfoId={0}&source=epz".format( contract_id )


def get_notification_xml_info(notification_id):
    notif_url = get_notification_printform_url( notification_id )
    driver.get( notif_url )
    lxml_dom = lxml.html.fromstring(driver.page_source)
    pass

def dl_document_by_contract_id(contract_id,new_driver):
    url = get_document_by_contract_id( contract_id )
    print "DL by contract", url
    new_driver.get(url)

def dl_document_by_notification_id(notification_id,new_driver):
    url = get_document_url_by_id( notification_id )
    print "DL by notification", url
    new_driver.get(url)

def process_order_info(reg_num, notification_id, target_dir):

    cache_key = 'reg_num_{0}_n_{1}'.format( reg_num, notification_id )

    if cache_key in cache:
        print 'Already in cache'
        return

    order_docs_url = get_order_documents_url(notification_id)
    doc_content = get_content( order_docs_url )
    ids = get_documents_by_notification(doc_content)

    new_driver, directory = get_driver_by_notification( target_dir, reg_num )

    for id in ids:
        print "Process notification id",  id
        writtern_file = dl_document_by_notification_id( id , new_driver )


    waiting_max = 20*60
    current_waited = 0
    while True:
        os.chdir(directory)
        files = filter(os.path.isfile, os.listdir(os.getcwd()))
        files = [os.path.join(os.getcwd(), f) for f in files]


        wait = False
        for file in files:
            if '.part' in file:
                wait = True
        if wait:
            time.sleep( 10 )
            current_waited+= 10
        else:
            break
        if current_waited > waiting_max:
            break
    cache[cache_key] = True
    pickle.dump(cache, open(cache_file, 'wb') )
    new_driver.close()


def process_contract_info(reg_num, contract_id, target_dir):

    cache_key = 'reg_num_{0}_c_{1}'.format( reg_num, contract_id )

    if cache_key in cache:
        print 'Already contract in cache'
        return

    order_docs_url = get_order_documents_url_by_contract_id(contract_id)
    doc_content = get_content( order_docs_url )
    ids = get_documents_ids_by_contract(doc_content)

    new_driver, directory = get_driver_by_notification( target_dir, reg_num)

    for id in ids:
        print "Process contract id",  id
        writtern_file = dl_document_by_contract_id( id , new_driver )

    current_waited = 0
    waiting_max = 5*60
    while True:
        os.chdir(directory)
        files = filter(os.path.isfile, os.listdir(os.getcwd()))
        files = [os.path.join(os.getcwd(), f) for f in files]
        wait = False
        for file in files:
            if '.part' in file:
                wait = True
        if wait:
            time.sleep( 10 )
            current_waited+= 10
        else:
            break
        if current_waited > waiting_max:
            break
    cache[cache_key] = True
    pickle.dump(cache, open(cache_file, 'wb') )
    new_driver.close()

def dump_all_contracts(mashape_api):
    import requests
    import json
    import pickle

    url = "https://clearspending.p.mashape.com/v1/contracts/select/"

    payload = {'daterange': '01.01.2013-31.12.2013', 'okdp' : '3410010'}
    headers = {"X-Mashape-Authorization": mashape_api}

    received_objects = []
    current_page = 1
    while True:
        try:
            payload['page'] = str(current_page)
            req = requests.get( url, params = payload, headers=headers )
            objects = req.text
            objects = json.loads( objects )
            received_objects.extend( objects['contracts']['data'] )
            current_page +=1
            print "Current_page", current_page
            if len(received_objects) >= objects['contracts']['total']:
                break
        except Exception as e:
            print e
            time.sleep(2)
            print "Waiting..."
            continue

    pickle.dump( received_objects, open('car_contracts','wb') )


black_list = [u'ГАЗ', u'ВАЗ', u'УАЗ', u'МАЗ']

def filter_contracts(contract):
    if contract['price\r'] < 1500000:
        return False

    products = contract['products\r']['product\r']
    if not isinstance(products, list):
        products = [ products ]

    contract['products\r']['product\r'] = products


    found_expensive = False
    for product in products:
        name =  product['name\r'].strip()
        for black in black_list:
            if name.lower().find(black.lower()) != -1:
                return False

        price = product['price\r']
        if price > 800000:
            found_expensive = True


    if not found_expensive:
        return False
    return True


def get_contract_id_by_reg_num(reg_num, mashape_api):
    print "Check", reg_num
    url = "https://clearspending.p.mashape.com/v1/contracts/get/"

    payload = {'regnum': reg_num}
    headers = {"X-Mashape-Authorization": mashape_api}

    req = requests.get( url, params = payload, headers = headers )

    text = req.text
    obj = json.loads( text )

    data = obj['contracts']['data']
    try:
        for item in data:
            if item['_newestVersion'] == True:
                printFormUrl = item['printFormURL']
                notification_id = printFormUrl[ printFormUrl.find('&id=') + len('&id='): ]
                return notification_id
    except:
        print "Error"

def get_order_notification_id_by_contract_id(contract_id):
    contract_info_url = get_contract_info_by_contract_id( contract_id )

    driver.get( contract_info_url )
    content = driver.page_source
    lxml_doc = lxml.html.fromstring(content)

    onclicks = lxml_doc.xpath("//a/@onclick")
    for onclick in onclicks:
        if onclick.find("notificationId=") != -1:
            start_idx  = onclick.find("notificationId=") + len("notificationId=")
            end_x = onclick.find( "&source=", start_idx )
            notification_id = onclick[ start_idx : end_x ]
            return notification_id

def filter_contracts():


    contracts = pickle.load( open('car_contracts','rb') )
    filtered_contracts = filter( filter_contracts, contracts )

    print len(filtered_contracts)
    found_notif = 0
    for contract in filtered_contracts:
        products = contract['products\r']['product\r']
        if not isinstance(products, list):
            products = [ products ]

        regNum = contract['regNum\r'].strip()

        contract_id = get_contract_id_by_reg_num( regNum )
        if contract_id is not None:
            found_notif +=1
            contract['contract_id'] = contract_id
            print "Found contract id", contract_id
        else:
            print "Not found"


    pickle.dump( filtered_contracts, open('filtered_contracts', 'wb') )

    print "Found contract ids percent", float(found_notif) /len(filtered_contracts) * 100

if __name__ == "__main__":

    driver = webdriver.Firefox()
    driver.set_page_load_timeout(300)
    notification_dir = os.path.abspath(os.path.join( current_dir, 'files_n' ))
    contracts_dir = os.path.abspath(os.path.join( current_dir, 'files_c' ))

    contracts = pickle.load( open('filtered_contracts','rb') )
    for contract in contracts:
        reg_num = contract['regNum'].strip()
        print "RegNum", reg_num
        contract_id = contract['notif_id']

        notification_id = get_order_notification_id_by_contract_id( contract_id )
        if notification_id:
            print "Found notification id", notification_id
            process_order_info( reg_num, notification_id,  notification_dir )
            time.sleep(1)

        process_contract_info( reg_num, contract_id,  contracts_dir )
        time.sleep(1)

