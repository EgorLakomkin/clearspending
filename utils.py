#!-*-coding:utf-8-*-

import simplejson
import urllib2
import requests
import re
def get_files(path, pattern="*.*"):
    import os
    from glob import glob

    files = []
    start_dir = path

    for dir,_,_ in os.walk(start_dir):
        files.extend(glob(os.path.join(dir,pattern)))
    return files

def preprocessor_text(text):
    text = re.sub(u'[«»\'\"]',u'', text)
    return text

def google_images_by_kw(searchTerm):
    searchTerm = searchTerm.encode('utf8')
    searchTerm += " 2013 wikimedia"
    searchTerm = re.sub(u'[^a-zA-Z%0-9а-яА-ЯёЁ\. ]', u'', searchTerm)
    searchTerm = searchTerm.replace(' ','%20')



    start = 1
    url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+searchTerm+'&start='+str(start)+'&userip=MyIP')
    request = urllib2.Request(url, None, {'Referer': 'testing'})
    response = urllib2.urlopen(request)

    # Get results using JSON
    try:
        results = simplejson.load(response)
        data = results['responseData']
        if 'results' in data:
            dataInfo = data['results']

            # Iterate for each result and get unescaped url
            for myUrl in dataInfo:
                url = myUrl['unescapedUrl']

                req = requests.get(url)
                headers = req.headers['content-type']
                if req.status_code == 200 and 'jpeg' in headers:
                    yield url
    except:
        pass

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

if __name__ == "__main__":

    preprocessor_text(u"«CAMRY»")
    for url in google_images_by_kw(u'Toyota Highlander'):
        print url