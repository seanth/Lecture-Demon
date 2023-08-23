import os, sys, csv, glob, argparse

import pandas as pd #pip install pandas
import nltk #pip install nltk

pathToUtils = "lecture-daemon_data"
###append the path to basic data files
sys.path.append(pathToUtils)
import fileUtils

#pathToWhisperTranscribe = 'lecture-daemon_data/whisper-timestamped-master/whisper_timestamped/'
pathToWhisperTranscribe = 'lecture-daemon_data/whisperX-min/whisperx/'

def str2bool(string):
    #MIT License, Copyright (c) 2022 OpenAI
    str2val = {"True": True, "False": False}
    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(f"Expected one of {set(str2val.keys())}, got {string}")

def makeWhisperTranscription(audioFilePath, outputTranscriptDir, boolcsv, booljson, boolsrt, booltxt, boolvtt, theProcessedAudioDir):
        theAudioFileName = os.path.basename(audioFilePath)
        if os.path.exists(audioFilePath):
            print("         '%s' found" % theAudioFileName)
            transcribeScript = os.path.join(pathToWhisperTranscribe, "transcribe.py")
            #python transcribe.py <path to audio file> --model small.ed --language en --csv True --json False --srt False --txt False --vtt False
            #python transcribe.py <path to audio file> --model small.en --language en --csv True --json False --srt False --txt False --vtt False --align_model WAV2VEC2_ASR_LARGE_LV60K_960H
            theModel = "base.en"
            theLanguage = "en"
            verbose = False
            #theCommand = "python '%s' '%s' --model %s --language %s --csv %s --json %s --srt %s --txt %s --vtt %s --punctuations False -o %s" % (transcribeScript, 
            #    audioFilePath, theModel, theLanguage, boolcsv, booljson, boolsrt, booltxt, boolvtt, outputTranscriptDir)
            theCommand = "python '%s' '%s' --model %s --language %s --csv %s --json %s --srt %s --txt %s --vtt %s --align_model WAV2VEC2_ASR_LARGE_LV60K_960H -o %s" % (transcribeScript, 
               audioFilePath, 
               theModel, 
               theLanguage, 
               boolcsv, booljson, boolsrt, booltxt, boolvtt,
               outputTranscriptDir)
            print(theCommand)
            #os.exit()
            os.system(theCommand)
            print("         Storing transcribed file...")
            theCommand = "mv '%s' '%s'" % (audioFilePath, theProcessedAudioDir)
            os.system(theCommand)
        else:
            print("         '%s' missing. SKIPPING" % theAudioName)

def alignTokens(transcriptFilePath,alignmentDir,theProcessedTranscriptDir):
        theFileName = os.path.basename(transcriptFilePath)
        if os.path.exists(transcriptFilePath):
            print("     Opening transcript file %s" % theFileName)
            alignmentRead = pd.read_csv(transcriptFilePath, header=None, names=['word','start','stop','token','slide', 'meta'])
            theWordList = list(alignmentRead['word'])
            tokenList=[]
            for i in theWordList:
                tagged = nltk.pos_tag([i], tagset='universal')
                tokenList.append(tagged[0][1])

            alignmentRead['token']=tokenList

            print("          Saving word tokens...")
            theNewName = theFileName.split(".mp3.word.csv")[0]
            theAlignedFilePath = os.path.join(alignmentDir,theNewName+".csv")

            alignmentRead.to_csv(theAlignedFilePath,header=False)
            print("          Storing tokenized file...")
            theCommand = "mv '%s' '%s'" % (transcriptFilePath, theProcessedTranscriptDir)
            os.system(theCommand)
        else:
            print("         '%s' missing. SKIPPING" % theFileName)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    # parser.add_argument('--transcript', metavar='', dest='downloadTranscript', default=True, required=False, help='download the transcript from youtube?' )
    parser.add_argument('--transcript', metavar='', dest='makeTranscription', default=True, required=False, help='use gentle to make an alignment csv? Default True' )
    parser.add_argument('--tokens', metavar='', dest='makeTokens', default=True, required=False, help='assign word tokens to words in alignment csv? Default True' )

    parser.add_argument('--audioDir', metavar='', dest='theAudioDir', default='intermediate/processed_audio', required=False, help='path to folder containing processed mp3s' )
    parser.add_argument('--transcriptDir', metavar='', dest='theTranscriptDir', default='intermediate/lecture_transcripts', required=False, help='path to place transcripts')
    parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='intermediate/lecture_alignments', required=False, help='path to place alignments')
    parser.add_argument("--csv", default=True, help="output word-by-word transcript times as csv. Default True", type=str2bool)
    parser.add_argument("--json", default=False, help="output transcript as json. Default False", type=str2bool)
    parser.add_argument("--srt", default=False, help="output transcript as srt. Default False", type=str2bool)
    parser.add_argument("--txt", default=False, help="output transcript as txt. Default False", type=str2bool)
    parser.add_argument("--vtt", default=False, help="output transcript as vtt. Default False", type=str2bool)

    args = parser.parse_args()

    
    outputAlignmentDir = 'intermediate/lecture_alignments'
    #transcriptDir = 'output/lecture_transcripts'
    #inputAudioDir = 'output/processed_audio'

    #check and see whether destination folder for transcripts exists
    transcriptDir = fileUtils.pathExistsMake(args.theTranscriptDir, True)
    theProcessedTranscriptDir = os.path.join(transcriptDir,"aligned")
    theProcessedTranscriptDir = fileUtils.pathExistsMake(theProcessedTranscriptDir, True)

    theAudioDirIn = fileUtils.pathExistsMake(args.theAudioDir, True)
    theProcessedAudioDir = os.path.join(theAudioDirIn,"transcribed")
    theProcessedAudioDir = fileUtils.pathExistsMake(theProcessedAudioDir, True)

    theAlignmentDir = fileUtils.pathExistsMake(args.theAlignmentDir, True)

    if args.makeTranscription == True:
        print("     Attempting to make transcription...") 
        tempVar = os.path.join(theAudioDirIn, "*.mp3")
        for theFilePath in glob.glob(tempVar):
            makeWhisperTranscription(theFilePath, transcriptDir, args.csv, args.json, args.srt, args.txt, args.vtt, theProcessedAudioDir)

    if args.makeTokens == True:
        nltk.download('averaged_perceptron_tagger')
        nltk.download('universal_tagset')
        print("     Attempting to asign tokens...") 
        tempVar = os.path.join(transcriptDir, "*mp3.word.csv")
        for theFilePath in glob.glob(tempVar):
            alignTokens(theFilePath,theAlignmentDir,theProcessedTranscriptDir)
    
    print("     *****Done*****")

