#this has minor changes to allow csv to be output
# curl -o lecture-daemon_data/master.zip -L https://github.com/seanth/gentle/archive/master.zip

# unzip lecture-daemon_data/master.zip -d lecture-daemon_data/

# rm -r lecture-daemon_data/gentle-master/ext/kaldi
# curl -o lecture-daemon_data/gentle-master/ext/kaldi-master.zip -L https://github.com/kaldi-asr/kaldi/archive/7ffc9ddeb3c8436e16aece88364462c89672a183.zip
# unzip lecture-daemon_data/gentle-master/ext/kaldi-master.zip -d lecture-daemon_data/gentle-master/ext
# mv lecture-daemon_data/gentle-master/ext/kaldi-*/ lecture-daemon_data/gentle-master/ext/kaldi/
# touch lecture-daemon_data/gentle-master/ext/kaldi/tools/extras/python/.use_default_python
##############
# lecture-daemon_data/gentle-master/ext/kaldi/tools/extras/check_dependencies.sh
#####will probably need automake and autoconf
# brew install automake
# brew install autoconf ##note that autoconf is a dependency for automake, so should get both with the above
##############
# cd lecture-daemon_data/gentle-master/ext/kaldi/tools && make && cd -
# cd lecture-daemon_data/gentle-master/ext/kaldi/src && ./configure && make && cd -
##############
# cd lecture-daemon_data/gentle-master && ./install.sh && cd -

#./install.sh


import os, sys, csv, glob, argparse

import pandas as pd #pip install pandas
import nltk #pip install nltk
from youtube_transcript_api import YouTubeTranscriptApi #pip install youtube-transcript-api

pathToUtils = "lecture-daemon_data"
###append the path to basic data files
sys.path.append(pathToUtils)
import fileUtils

nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')


pathToGentle = 'lecture-daemon_data/gentle-master'
broadcastIDFileName = 'lecture-daemon_data/broadcast_id_archive.csv'

#########################################################################################
# def pathExists(thePath, makeBool):
#     theFeedback="     Path '%s' found:    %s"
#     if os.path.exists(thePath)==False:
#         print(theFeedback % (thePath, "FALSE"))
#         sys.exit()
#     else:
#         print(theFeedback % (thePath, "TRUE"))
#         return os.path.abspath(thePath)

# def pathExistsMake(thePath, makeBool=False):
#   ###does the folder containing audio files exist?
#     theFeedback="     Path '%s' found:    %s"
#     if os.path.exists(thePath)==False:
#         print(theFeedback % (thePath, "FALSE"))
#         if makeBool==False:
#             print("        Exiting.")
#             sys.exit()
#         else:
#             #Make the dir if it doesn't exist
#             print("     Creating dir '%s'" % (thePath))
#             os.mkdir(thePath)
#             return os.path.abspath(thePath)
#     else:
#         print(theFeedback % (thePath, "TRUE"))
#         return os.path.abspath(thePath)

def getTranscript(broadcastIDFileName, transcriptDir):
    #read in the saved video id,lecture name data
    with open(broadcastIDFileName) as csvfile:
        theReader = csv.reader(csvfile)
        for row in theReader:
            theVideoID = row[0]
            theLectureName = row[1]
            theTranscriptFile = os.path.join(transcriptDir, theLectureName+".txt")
            print("     Attempting to download transcript for '%s'" % theLectureName) 
            theRawTranscript = YouTubeTranscriptApi.get_transcript(theVideoID)
            transcriptFile = open(theTranscriptFile,"w")
            for aDict in theRawTranscript:
                transcriptFile.write(aDict['text']+"\n")
            transcriptFile.close()
            print("          Done")
    #consider a cli arg that would allow for clearing the info from the broadcast_id_archive.csv after transcript download        

def makeAlignments(transcriptDir, outputAlignmentDir, inputAudioDir):
    #the txt files in inputTranscriptDir should have same name matches in inputAudioDir
    tempVar = os.path.join(transcriptDir, "*.txt")
    for theFileName in glob.glob(tempVar):
        theTranscriptName = os.path.basename(theFileName)
        print("         '%s' found" % theTranscriptName)
        theTranscriptName = os.path.splitext(theTranscriptName)[0]
        audioFilePath = os.path.join(inputAudioDir, theTranscriptName+".mp3")
        theAudioName = os.path.basename(audioFilePath)
        if os.path.exists(audioFilePath):
            print("         '%s' found" % theAudioName)
            #python3 align.py -o <output file> -c <audioFile> <textFile>
            theAlignmentName = theTranscriptName+".csv"
            alignmentFile = os.path.join(outputAlignmentDir, theAlignmentName)
            alignScript = os.path.join(pathToGentle, "align.py")
            #print(tempVar)

            theCommand = "python3 '%s' -c -o '%s' '%s' '%s'" % (alignScript, alignmentFile, audioFilePath, theFileName)
            os.system(theCommand)
        else:
            print("         '%s' missing. SKIPPING" % theAudioName)

def alignTokens(alignmentDir):
    tempVar = os.path.join(alignmentDir, "*.csv")
    for theFileName in glob.glob(tempVar):
        print("     Opening alignment file %s" % theFileName)
        alignmentRead = pd.read_csv(theFileName, header=None, names=['word','match','start','stop','token','slide', 'meta'])
        theWordList = list(alignmentRead['word'])
        tokenList=[]
        for i in theWordList:
            #print(i)
            tagged = nltk.pos_tag([i], tagset='universal')
            tokenList.append(tagged[0][1])

        alignmentRead['token']=tokenList

        print("          Saving word tokens")
        alignmentRead.to_csv(theFileName,header=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--transcript', metavar='', dest='downloadTranscript', default=True, required=False, help='download the transcript from youtube?' )
    parser.add_argument('--alignment', metavar='', dest='makeAlignment', default=True, required=False, help='use gentle to make an alignment csv?' )
    parser.add_argument('--tokens', metavar='', dest='makeTokens', default=True, required=False, help='assign word tokens to words in alignment csv?' )

    parser.add_argument('--audioDir', metavar='', dest='theAudioDir', default='intermediate/processed_audio', required=False, help='path to folder containing processed mp3s' )
    parser.add_argument('--transcriptDir', metavar='', dest='theTranscriptDir', default='intermediate/lecture_transcripts', required=False, help='path to place transcripts')
    parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='intermediate/lecture_alignments', required=False, help='path to place alignments')
    args = parser.parse_args()

    
    outputAlignmentDir = 'intermediate/lecture_alignments'
    #transcriptDir = 'output/lecture_transcripts'
    #inputAudioDir = 'output/processed_audio'

    #check and see whether file with video id's exists
    broadcastIDFileName = fileUtils.pathExists(broadcastIDFileName)

    #check and see whether destination folder for transcripts exists
    transcriptDir = fileUtils.pathExistsMake(args.theTranscriptDir, True)
    theAudioDirIn = fileUtils.pathExistsMake(args.theAudioDir, True)
    theAlignmentDir = fileUtils.pathExistsMake(args.theAlignmentDir, True)

    if args.downloadTranscript == True:
        print("     Attempting to download transcripts...") 
        getTranscript(broadcastIDFileName, transcriptDir)

    if args.makeAlignment == True:
        print("     Attempting to make alignments...") 
        makeAlignments(transcriptDir, theAlignmentDir, theAudioDirIn)

    if args.makeTokens == True:
        print("     Attempting to asign tokens...") 
        alignTokens(theAlignmentDir)
    
    print("     *****Done*****")

