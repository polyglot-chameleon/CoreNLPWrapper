#!/usr/bin/env python3

import glob
import os
from setuptools import setup

current_wd = os.getcwd()
mydir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(mydir, "CoreNLPWrapper"))
corenlp_files = glob.glob("*", recursive=True)
print(corenlp_files)
os.chdir(current_wd)

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as fh:
    long_description = fh.read()

setup(
    name='CoreNLPWrapper',
    version="0.1.0",
    author='Oleg Harlamov',
    author_email='oleg.harlamov@fau.de',
    packages=[
        'CoreNLPWrapper'
    ],
    scripts=[
        'bin/corenlp_wrapper.py',
    ],
    package_data={
        'CoreNLPWrapper': corenlp_files,
    },

    data_files=[('demo_corpora', ['demo_corpora/install_corpora.sh', 'demo_corpora/verne_journey_into_the_interior_of_the_earth.txt', 'demo_corpora/verne_reise_nach_dem_mittelpunkt_der_erde.txt', 'demo_corpora/verne_interior_short.txt', 'demo_corpora/verne_mittelpunkt_short.txt']),
                ('output', ['output/CoreNLP-to-HTML.xsl', 'output/verne_interior_full.vrt.xml', 'output/verne_interior_short.vrt.xml', 'output/verne_mittelpunkt_short.vrt.xml']),
    ],

    license='GNU General Public License v3 or later (GPLv3+)',
    description='A Python wrapper to run StanfordCoreNLP pipeline on CWB-indexed corpora.',
    long_description=long_description,
    install_requires=[
         "langdetect",
     ],
     python_requires='>=3.4',
)
