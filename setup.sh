#!/bin/sh

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.10
#might need to add path to .rc file

# Dev Tools
echo "Installing requirements..."
brew install ffmpeg
brew install rubberband
brew install sox

####################################
curl -o lecture-daemon_data/master.zip -L https://github.com/seanth/whisper/archive/main.zip
unzip lecture-daemon_data/master.zip -d lecture-daemon_data/

cd lecture-daemon_data/whisper-main
python -m pip install -r requirements.txt
sudo python setup.py install --record whisper-files.txt
cd ../../
####################################

####################################
#download whisper with word-by-word
curl -o lecture-daemon_data/master.zip -L https://github.com/seanth/whisperX/archive/refs/heads/min.zip
unzip lecture-daemon_data/master.zip -d lecture-daemon_data/
python -m pip install -r lecture-daemon_data/whisper-timestamped-master/requirements.txt
####################################

rm lecture-daemon_data/master.zip
