mkdir wiki;cd wiki
wget https://dumps.wikimedia.org/cswiki/latest/cswiki-latest-pages-articles.xml.bz2
bunzip2 cswiki-latest-pages-articles.xml.bz2
git clone https://github.com/attardi/wikiextractor.git
cd wikiextractor
python WikiExtractor.py --filter_disambig_pages -b 100G  -it abbr,b,big -de gallery,timeline,noinclude,nowiki,poem,ref,mapref,a --min_text_length 1000 ../cswiki-latest-pages-articles.xml

