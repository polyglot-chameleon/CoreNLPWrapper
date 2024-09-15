#!/usr/bin/env python3

import subprocess
import os
import xml.etree.ElementTree as ET
import re
import logging
from CoreNLPWrapper.corenlp_downloader import download

try:
    from langdetect import detect
except ImportError:
    ask = input('Python package <langdetect> currently not installed. Download? [Y/n] ')

    if ask == 'Y':
        cp = subprocess.run('pip3 install --user langdetect'.split(), stdout=subprocess.PIPE)
        print(cp.stdout.decode())
    else:
        quit()


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - \033[92m%(message)s\033[0m',
    datefmt='%H:%M:%S'
)


def cmd(command_as_str):
    for command in command_as_str.strip().splitlines():
        cp = subprocess.run(command.strip().split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cp.stdout:
            print(cp.stdout.decode())
        if cp.stderr:
            print(cp.stderr.decode())


def purge(pattern, some_dir='./'):
    for f in os.listdir(some_dir):
        if re.search(pattern, f):
            os.remove(os.path.join(some_dir, f))


def align_columns(*columns):
    pattern = ''
    for arg in columns:
        if arg:
            pattern += str(arg) + '\t'

    return pattern.strip() + '\n'


class CoreNLPWrapper:
    def __init__(self, registry, corpus, **kwargs):
        self.registry = registry
        self.corpus = corpus
        self.directory = os.path.abspath(os.path.join(registry, os.pardir))
        self.core_directory = kwargs['core_directory']

        self.vrt_file = corpus + '.vrt'
        self.export_corpus()

        self.detect_language()
        self.annotators = kwargs['annotators']

        if self.language == 'en':
            self.truecase = kwargs['truecase']
            self.americanize = kwargs['americanize']
        else:
            self.truecase = False
            self.americanize = False
        self.memory = kwargs['memory']

        self.run_corenlp()
        self.extract_annotations()
        self.make_corpus()
        self.regedit_lang()

        purge(self.vrt_file + '.*')


    def export_corpus(self):
        # export word forms and sentence boundaries
        with open(self.vrt_file, "w") as f:
            cp = subprocess.run(["cwb-decode", "-r", self.registry, "-C", self.corpus, "-P", "word", "-S", "s"], stdout=f, stderr=subprocess.PIPE)
            if cp.stderr:
                print(cp.stderr.decode())
                if "setup_corpus: can't locate " in cp.stderr.decode() or 'not found in registry' in cp.stderr.decode():
                    with open('CoreNLPWrapper/.default_registry.txt', 'w') as f:
                        f.write('')
                    quit()

        iFile = open(self.vrt_file, "r").read()
        oFile = open(self.vrt_file, "w")
        oFile.write(re.sub('<s( id="\d+")?( sentimentvalue="\d+" sentiment="\w+")?( parse=".+")?>', '<s>', iFile))


    def read_coreferences(self, corenlp_xml_object):
        coref_matrix = []
        count = 1

        for cor in corenlp_xml_object.findall('./document/coreference/coreference'):
            name = 'coref' + str(count)

            for mention in cor.findall('mention'):
                coref_anot = '%s(sent-%s, %s-%s)' % (name, mention.findtext('sentence'), mention.findtext('text'), mention.findtext('head'))                
                val = [re.findall('\d+', coref_anot)[1]]
                val.append((mention.findtext('start'), mention.findtext('end')))
                val.append('%s(gov:%s)' % (name,cor.findtext('./mention/text')))
                coref_matrix.append(val)

            count += 1

        return coref_matrix


    def get_coreference(self, coreferences, sentence, token):
        coref = 'O'
        for val in coreferences:
            if val[0] == sentence.get('id'):
                if int(token.get('id')) >= int(val[1][0]):
                    if int(token.get('id')) < int(val[1][1]):
                        coref = val[-1]
        return coref



    def read_dependencies(self, sentence):
        deps = sentence.find(
            './dependencies[@type="enhanced-plus-plus-dependencies"]'
        )

        return deps


    def get_dependence(self, dependencies, token):
        if not dependencies:
            return

        for dep in dependencies.iter('dep'):
            if dep.find('dependent').get('idx') == token.get('id'):
                depparse = '%s(%s-%s, %s-%s)' % (dep.get('type'),
                                                 dep.findtext('governor'),
                                                 dep.find('governor').get('idx'),
                                                 token.findtext('word'),
                                                 token.get('id'))

        return depparse


    def make_entities(self, sentence, token, out):
        if 'ner' not in self.annotators:
            return

        norm = token.findtext('NormalizedNER')
        prev_norm = sentence.findtext('.//token[@id="%s"]/NormalizedNER'
                                      % str(int(token.get('id'))-1))
        if norm:
            if prev_norm:
                if norm != prev_norm:
                    out.write('</entity>\n')
                    out.write('<entity mention="%s">\n' % norm)
            else:
                out.write('<entity mention="%s">\n' % norm)
        else:
            if prev_norm:
                out.write('</entity>\n')

    def manage_annotations(self):
        german = ''

        if self.language == 'en':
            if not self.annotators:
                self.annotators = 'pos,parse,lemma,ner,sentiment,coref'
            elif self.annotators == 'sentiment':
                self.annotators = 'parse,' + self.annotators
            elif self.annotators == 'coref':
                self.annotators = 'parse,lemma,ner,' + self.annotators
            if self.annotators == 'lemma':
                self.annotators = 'pos,' + self.annotators
            if self.annotators == 'ner':
                self.annotators = 'pos,lemma,' + self.annotators

        elif self.language == 'de':
            german = '-props StanfordCoreNLP-german.properties'
            if self.annotators == 'pos':
                pass
            elif self.annotators == 'lemma':
                logging.warn('No lemma annotator for german!')
                self.annotators = ''
            elif self.annotators == 'ner':
                pass
            elif self.annotators == 'parse':
                self.annotators += ',depparse'
            else:
                self.annotators = 'pos,parse,depparse,ner'

        return german


    def run_corenlp(self):
        german = self.manage_annotations()

        truecase = ''
        americanize = ''
        if self.truecase:
            truecase = '-truecase.overwriteText'
            self.annotators = 'truecase,' + self.annotators
        if self.americanize:
            americanize = '-tokenize.options americanize=true'

        command = 'java -mx%sg edu.stanford.nlp.pipeline.StanfordCoreNLP %s -annotators tokenize,cleanxml,ssplit,%s -file %s -tokenize.class PTBTokenizer -coref.algorithm neural -clean.singlesentencetags s -tokenize.whitespace %s %s' % (self.memory, german, self.annotators, self.vrt_file, americanize, truecase)

        cp = subprocess.run(command.strip().split(), stdout=subprocess.PIPE)
        print(cp.stdout.decode())

    def extract_annotations(self):
        annotated = ET.parse(self.vrt_file + '.xml')
        coref_matrix = self.read_coreferences(annotated)

        out_file = self.vrt_file + '.out'
        with open(out_file, 'w') as f:
            for sentence in annotated.iter('sentence'):
                if not sentence.find('tokens'):
                    break

                attribs = ''
                if sentence.get('sentimentValue'):
                    attribs += 'sentimentvalue="%s" sentiment="%s" ' % (sentence.get('sentimentValue'), sentence.get('sentiment'))
                if sentence.findtext('parse'):
                    attribs += 'parse="%s"' % re.sub('(\'\'|``) \"', '&apos;&apos; &quot;', sentence.findtext('parse'))
                f.write(
                    '<s id="%s" %s>\n'
                    % (sentence.get('id'), attribs)
                )

                deps = self.read_dependencies(sentence)

                for token in sentence.iter('token'):
                    self.make_entities(sentence, token, f)

                    self.pattern = align_columns(token.findtext('word'),
                                                 token.get('id'),
                                                 token.findtext('POS'),
                                                 token.findtext('lemma'),
                                                 token.findtext('NER'),
                                                 token.findtext('sentiment'),
                                                 self.get_dependence(deps, token),
                                                 self.get_coreference(coref_matrix, sentence, token),
                                                 token.findtext('Speaker')
                    )


                    f.write(self.pattern)
                f.write('</s>\n\n')


    def make_corpus(self):
        columns = 'id pos'
        if self.language == 'en':
            if self.annotators.split(',')[-1] == 'parse':
                pass
            if self.annotators.split(',')[-1] == 'ner':
                columns += ' lemma ner'
            elif self.annotators.split(',')[-1] == 'sentiment':
                columns += ' sentiment dep'
            elif self.annotators.split(',')[-1] == 'coref':
                if 'sentiment' in self.annotators:
                    columns += ' lemma ner sentiment dep coref speaker'
                else:
                    columns += ' lemma ner dep coref speaker'
        elif self.language == 'de':
            if self.annotators.split(',')[-1] == 'depparse':
                columns += ' dep'
            elif not self.annotators:
                columns = 'id'
            elif self.annotators == 'ner':
                columns = 'id ner'
            elif self.annotators.split(',')[-1] == 'ner':
                columns += ' ner dep'

        entity_mention = ''
        newword = ''
        sentiment = ''
        parse = ''

        if 'ner' in self.annotators:
            entity_mention = '-V entity:0+mention'
        if self.truecase or self.americanize:
            newword = '-p -'
            columns = 'coreword ' + columns
        if 'parse' in self.annotators:
            parse = '+parse'
            if 'sentiment' in self.annotators:
                sentiment = '+sentimentvalue+sentiment'
        columns = columns.split()

        cmd(
            """
            cwb-encode -d {0} -f {1}.out -c utf8 -U O -xsB {8} -P {4} -V s:0+id{10}{11} {6}
            cwb-regedit -r {2} {3} :add :p {5} :s s {7}
            cwb-regedit -r {2} {3} :prop language {9}
            cwb-make -r {2} -M 500 -V {3}
            cp {1}.xml ../output
            """.format(
                (os.path.abspath(self.directory + '/data/' + self.corpus)),
                self.vrt_file,
                self.registry,
                self.corpus,
                ' -P '.join(columns).strip(),
                ' '.join(columns),
                entity_mention,
                ''.join(re.findall('entity', entity_mention)),
                newword,
                self.language,
                sentiment,
                parse,
                self.core_directory)
        )

        


    def detect_language(self):
        acc = ''

        for line in open(self.vrt_file, 'r').readlines():
            if '<' not in line:
                acc += ' ' + line

        self.language = detect(acc.strip())
        logging.info('Detected Language: %s' % self.language)

        if self.language == 'de':
            if not os.path.exists(os.path.join(self.core_directory, 'stanford-german-corenlp-2018-02-27-models.jar')):
                download('stanford-german-corenlp-2018-02-27-models.jar', directory='../CoreNLP/stanford-corenlp-full-2018-02-27/')

    def regedit_lang(self):
        with open(os.path.join(self.registry, self.corpus), 'rt') as fin:
            with open(os.path.join(self.registry, self.corpus)+'copy', 'wt') as fout:
                for line in fin:
                    fout.write(line.replace('??', self.language))

        cmd('mv {0}copy {0}'.format(os.path.join(self.registry, self.corpus)))
