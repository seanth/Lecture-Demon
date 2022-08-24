#!/bin/sh

# Homebrew Script for OSX
# To execute: save and `chmod +x ./brew-install-script.sh` then `./brew-install-script.sh`

echo "Installing brew..."
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


# Dev Tools
echo "Installing requirements..."
brew install ffmpeg
brew install rubberband


#this has minor changes to allow csv to be output
#download edited gentle zip to lecture-daemon_data folder
curl -o lecture-daemon_data/master.zip -L https://github.com/seanth/gentle/archive/master.zip
#unzip
unzip lecture-daemon_data/master.zip -d lecture-daemon_data/
#remove the existing kaldi folder
rm -r lecture-daemon_data/gentle-master/ext/kaldi
#download kaldi zip to lecture-daemon_data folder
curl -o lecture-daemon_data/gentle-master/ext/kaldi-master.zip -L https://github.com/kaldi-asr/kaldi/archive/7ffc9ddeb3c8436e16aece88364462c89672a183.zip
#unzip
unzip lecture-daemon_data/gentle-master/ext/kaldi-master.zip -d lecture-daemon_data/gentle-master/ext
#rename the existing folder
mv lecture-daemon_data/gentle-master/ext/kaldi-*/ lecture-daemon_data/gentle-master/ext/kaldi/
#change directories and run the shell script to install kaldi
cd lecture-daemon_data/gentle-master/ext
./install_kaldi.sh
#change directories and run the shell script to install kaldi
cd lecture-daemon_data/gentle-master
./install.sh

echo "Done!"