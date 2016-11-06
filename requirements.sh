# This was made for a general purpose linux ami

touch ~/.bash_profile
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile

# homebrew and anaconda
if [[ "$OSTYPE" == linux-gnu ]]; then
	sudo yum groupinstall 'Development Tools' && sudo yum install curl git irb python-setuptools ruby
	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install)"
	# PATH="$HOME/.linuxbrew/bin:$PATH"
	echo 'export PATH="$HOME/.linuxbrew/bin:$PATH"' >> ~/.bash_profile
	echo 'export PATH="/home/ec2-user/.linuxbrew/bin:$PATH"' >>~/.bash_profile
    echo 'export MANPATH="/home/ec2-user/.linuxbrew/share/man:$MANPATH"' >>~/.bash_profile
    echo 'export INFOPATH="/home/ec2-user/.linuxbrew/share/info:$INFOPATH"' >>~/.bash_profile
	source ~/.bash_profile

	# anaconda
	curl -L http://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh > ~/anaconda_script.sh
	bash ~/anaconda_script.sh
	echo 'export PATH="~/anaconda3/bin:$PATH"' >> ~/.bash_profile

    # pyenchant
    sudo yum install enchant

elif [[ "$OSTYPE" == darwin* ]]; then
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	# anaconda
	curl -L http://repo.continuum.io/archive/Anaconda3-4.2.0-MacOSX-x86_64.sh > ~/anaconda_script.sh
	bash ~/anaconda_script.sh
	echo 'export PATH="~/anaconda3/bin:$PATH"' >> ~/.bash_profile
    
    # pyenchant
    brew install enchant
fi

# chrome driver for selenium
brew install chromedriver

# Berkeley-db for gutenberg
brew install berkeley-db4
brew info berkeley-db4
echo -n 'What is the filepath of the berkeley-db package? > '
read FILEPATH
echo 'export BERKELEYDB_DIR=$FILEPATH' >> ~/.bash_profile
source ~/.bash_profile

conda update conda
conda update anaconda

sudo ln -s /usr/local/bin/pip /usr/bin/pip

# Base libraries
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade ipython
pip install numpy
pip install pandas
pip install scipy
pip install --upgrade sklearn

# Web scraping
pip install bs4
pip install requests
pip install urllib
pip install selenium
pip install pdfminer3k
pip install bsddb3
pip install gutenberg
pip install internetarchive
pip install us
pip install langdetect
pip install pymongo

# NLP
pip install pyenchant
pip install autocorrect
pip install patterns
pip install gensim
pip install --upgrade spacy
python -m spacy.en.download all

echo 'import nltk
nltk.download("all")' | python

# Web app
pip install flask
pip install SQLAlchemy
