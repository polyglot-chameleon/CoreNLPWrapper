#!/usr/bin/env python3

import os
import urllib.request
import urllib.parse
import logging
import sys
import zipfile
import re


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - \033[92m%(message)s\033[0m',
    datefmt='%H:%M:%S'
)


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize:
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


def download(name, directory='../CoreNLP'):
    logging.info('Downloading CoreNLP')
    url = 'http://nlp.stanford.edu/software/%s' % name
    file_name = os.path.join(directory, name)
    urllib.request.urlretrieve(url, file_name, reporthook)

    return file_name


def extract_zip(zipf):
    logging.info('Extracting .jar-files')
    zip_ref = zipfile.ZipFile(zipf, 'r')
    zip_ref.extractall('../CoreNLP/')
    zip_ref.close()

    if os.path.exists(zipf[:-4]):
        logging.info('Successfully installed!')


def check_corenlp():
    name = 'stanford-corenlp-full-2018-02-27.zip'
    logging.info('Looking for existing .jar-files')
    if not os.path.exists('../CoreNLP/%s' % name[:-4]):
        logging.info('Nothing found!')
        try:
            os.mkdir('../CoreNLP')
        except FileExistsError:
            pass

        extract_zip(download(name))

    else:
        logging.info('Found %s ' % name[:-4])
        url = 'https://stanfordnlp.github.io/CoreNLP/'
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        latest = re.findall('stanford-corenlp-full-\d{4}-\d{2}-\d{2}.zip', str(response.read()))[0]

        file_name = os.path.join('../CoreNLP', latest)
        if not os.path.exists(file_name):
            ask = input('CoreNLP Update[%s] available! Download? [Y/n] ' % latest)

            if ask == 'Y':
                extract_zip(download(latest))
                name = latest

    return name[:-4]
