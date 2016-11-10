# This was made for a general purpose linux ami

# touch ~/.bash_profile
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
# source ~/.bash_profile

# homebrew and anaconda
if [[ "$OSTYPE" == linux-gnu ]]; then
    sudo yum groupinstall 'Development Tools' && sudo yum install curl git irb python-setuptools ruby
    sudo yum install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel
    source ~/.bash_profile

    # pyenchant
    sudo yum install enchant

elif [[ "$OSTYPE" == darwin* ]]; then
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

    # pyenchant
    brew install enchant

    # chrome driver for selenium
    brew install chromedriver

    # Berkeley-db for gutenberg
    brew install berkeley-db4
    brew info berkeley-db4
    echo -n 'What is the filepath of the berkeley-db package? > '
    read FILEPATH
    echo 'export BERKELEYDB_DIR=$FILEPATH' >> ~/.zshrc
    source ~/.zshrc

    # python 3
    brew install python3
    source ~/.zshrc

    # Base libraries
    pip3 install --upgrade pip
    pip3 install --upgrade wheel
    pip3 install --upgrade ipython
    pip3 install jupyter
    pip3 install numpy
    pip3 install pandas
    pip3 install scipy
    pip3 install matplotlib
    pip3 install --upgrade sklearn

    # Web scraping
    pip3 install bs4
    pip3 install requests
    pip3 install urllib
    pip3 install selenium
    pip3 install pdfminer3k
    pip3 install bsddb3
    pip3 install gutenberg
    pip3 install internetarchive
    pip3 install us
    pip3 install langdetect
    pip3 install geopy

    # NLP
    pip3 install pyenchant
    pip3 install autocorrect
    pip3 install patterns
    pip3 install -U gensim
    pip3 install pyLDAvis
    pip3 install -U spacy
    python3 -m spacy.en.download all

    pip3 install nltk
    python3 -m nltk.downloader all

    # Web app
    pip3 install flask
    pip3 install sqlalchemy
    pip3 install flask-sqlalchemy
    pip3 install folium
fi
