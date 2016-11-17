# This was made for a general purpose linux ami

# touch ~/.bash_profile
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
# source ~/.bash_profile

# homebrew and anaconda
if [[ "$OSTYPE" == linux-gnu ]]; then
    sudo apt-get update
    sudo apt-get install python3

    sudo apt-get install python3-pip

    # Base libraries
    sudo pip3 install --upgrade pip
    sudo pip3 install --upgrade wheel
    sudo pip3 install --upgrade ipython
    sudo pip3 install jupyter
    sudo pip3 install numpy
    sudo pip3 install pandas
    sudo pip3 install scipy
    sudo pip3 install matplotlib
    sudo pip3 install --upgrade sklearn

    # Web scraping
    sudo pip3 install bs4
    sudo pip3 install requests
    sudo pip3 install urllib
    sudo pip3 install selenium
    sudo pip3 install pdfminer3k
    sudo pip3 install internetarchive
    sudo pip3 install us
    sudo pip3 install langdetect
    sudo pip3 install geopy

    # NLP
    sudo pip3 install pyenchant
    sudo pip3 install autocorrect
    sudo pip3 install patterns
    sudo pip3 install -U gensim
    sudo pip3 install pyLDAvis
    sudo pip3 install -U spacy
    sudo python3 -m spacy.en.download all

    # sudo pip3 install nltk
    # sudo python3 -m nltk.downloader all

    # Web app
    sudo apt-get install -y nodejs
    sudo apt install nodejs-legacy
    sudo apt install npm
    npm init
    sudo npm install ogr2ogr
    sudo npm install topojson

    sudo pip3 install flask
    sudo pip3 install sqlalchemy
    sudo pip3 install flask-sqlalchemy

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
    brew install node
    brew install npm
    npm init
    npm install ogr2ogr
    npm install topojson

    pip3 install flask
    pip3 install sqlalchemy
    pip3 install flask-sqlalchemy
fi
