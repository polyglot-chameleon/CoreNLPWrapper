
### CoreNLP-Wrapper for IMS-CorpusWorkbench ###

Requirements:
   This package makes use of a pre-existing package installable from PyPI, namely: langdetect 

1) Installation:
   - Simply run the corenlp_wrapper.py script in the bin folder. All necessary dependencies will be installed automatically.
     However, the latter process might take some time depending on your network speed.

2) Usage:
   - If you have some CWB_Indexed corpora installed simply pass the corresponding registry file path
     with the option -r/--registry when running corenlp_wrapper.py.

     Example:
                ./corenlp_wrapper <corpus_name> -r /path/to/registry <options>

		
   - Otherwise, there are some demo corpora included in this package which can be installed via the install_corpora.sh script.

   - There's a bunch of additional options which can be passed along the script execution command:

   
                   -a {pos,lemma,parse,ner,sentiment,coref}, --annotators {pos,lemma,parse,ner,sentiment,coref}
					 Annotators to be loaded. If not specified, full pipeline is performed which takes at least 3G RAM

		   -M {1,2,3,4,5}        Forced RAM usage assignment

		   --truecase            Guesses the true case of input tokens and gathers them
					 in a new word column

		   --americanize         Returns the AE spelling of tokens in a new word column

		   --visualize           Shows CoreNLP Annotation Results via webbrowser
		   

3) Output
   - To view the annotation results in the newly annotated CWB-corpora you can run the following command:

                 cwb-decode -r /path/to/registry -C <corpusname> -ALL
