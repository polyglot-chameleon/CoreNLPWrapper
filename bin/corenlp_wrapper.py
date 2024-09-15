#!/usr/bin/env python3

# import subprocess
import os
import logging
from CoreNLPWrapper.corenlp import CoreNLPWrapper
# corenlp import CoreNLPWrapper
import argparse
import webbrowser
from CoreNLPWrapper.corenlp_downloader import check_corenlp


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - \033[92m%(message)s\033[0m',
    datefmt='%H:%M:%S'
)

parser = argparse.ArgumentParser(description='CoreNLPWrapper for IMS Corpus Workbench')

default_registry = None
req = True

env = ''
try:
    env = os.environ['CORPUS_REGISTRY']
except KeyError:
    pass

if os.path.isfile('CoreNLPWrapper/.default_registry.txt') and open('CoreNLPWrapper/.default_registry.txt', 'r').read():
    req = False
    default_registry = open('CoreNLPWrapper/.default_registry.txt', 'r').read()
elif env:
    oFile = open('CoreNLPWrapper/.default_registry.txt', 'w')
    oFile.write(os.environ['CORPUS_REGISTRY'])
    oFile.close()
    default_registry = os.environ['CORPUS_REGISTRY']

parser.add_argument('-r', '--registry', help='Path to registry directory; Default: %s' % default_registry, default=default_registry, required=req)
parser.add_argument('corpus', help='Corpus name')
parser.add_argument('-a', '--annotators', help='Annotators to be loaded. If not specified, full pipeline is performed which takes at least 3G RAM', default='', choices=['pos','lemma','parse','ner','sentiment','coref'])
parser.add_argument('-M', help='Forced RAM usage assignment', default='3', choices=['1','2','3','4','5'])
parser.add_argument('--truecase', help='Guesses the true case of input tokens and gathers them in a new word column', action='store_true')
parser.add_argument('--americanize', help='Returns the AE spelling of tokens in a new word column', action='store_true')
parser.add_argument('--visualize', help='Shows CoreNLP Annotation Results via webbrowser', action='store_true')
args = parser.parse_args()

if args.registry:
    registry = os.path.abspath(args.registry)

if os.path.isdir(registry) and os.path.isfile(os.path.join(registry, args.corpus)):
    core = check_corenlp()

    path = '../CoreNLP/%s/' % core
    os.environ['CLASSPATH'] = path + '*'

    with open('CoreNLPWrapper/.default_registry.txt', 'w') as f:
        f.write(registry)
    CoreNLPWrapper(registry, args.corpus, annotators=args.annotators, truecase=args.truecase, americanize=args.americanize, core_directory=path, memory=args.M)
    if args.visualize:
        # if os.path.isfile('CoreNLP/stanford-corenlp-full-2018-01-31/outverne.vrt.xml'):
        webbrowser.open_new_tab('../output/%s.vrt.xml' % args.corpus)
else:
    logging.warn('%s not in %s!' % (args.corpus, registry))
