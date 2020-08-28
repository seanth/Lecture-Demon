import datetime, os, sys, argparse, glob, re, json, itertools

import pandas as pd                         
import srt 			                        
from moviepy.editor import VideoFileClip    
from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip

from PIL import Image                       
from pydub import AudioSegment              
import audiosegment as audiosegwrap                         
import ffmpeg                               


theLeaderImage = "autodipop_data/leaderImage.png"

videoSuffixList = ['.mp4', '.m4v', '.mov']
audioSuffixList = ['.aiff', '.mp3', '.wav']
imageSuffixList = ['.png','.jpg','.jpeg','.gif']

theSlateDuration = 5
outroDuration = 5

def booleanCheck(theVariable):
    #assume theVariable is a string
    if theVariable.lower()=="true":
        return True
    else:   
        return False

def pathExistsMake(thePath, makeBool=False):
  ###does the folder containing audio files exist?
    theFeedback="     Path '%s' found:    %s"
    if os.path.exists(thePath)==False:
        print(theFeedback % (thePath, "FALSE"))
        if makeBool==False:
            print("        Exiting.")
            sys.exit()
        else:
            #Make the dir if it doesn't exist
            print("     Creating dir '%s'" % (thePath))
            os.mkdir(thePath)
            return os.path.abspath(thePath)
    else:
        print(theFeedback % (thePath, "TRUE"))
        return os.path.abspath(thePath)

def indexListMatchingElement(theList, theElement):
    checkedList = [] 
    i=0
    for anELement in theList:
        if str(anELement) != theElement:
            checkedList.append(i)        
        i=i+1
    return checkedList

def pydub_to_moviepy(theAudio, frameRate):
    if theAudio.channels < 2:
        #needs to be stereo for the conversion to a numpy arry to be OK
        #for then being used by moviepy
        print("          Changing number of audio channels to two(2)...")
        theAudio = audiosegwrap.from_mono_audiosegments(theAudio, theAudio)
    else:
        test = audiosegwrap.empty()
        theAudio = test+theAudio

    print("          Converting audio to numpy array...")
    theAudio = theAudio.to_numpy_array() #pydub convert to a numpy array
    #convert pydup numpy array to what moviepy wants
    #this is dirt and spit
    print("          32bit numpy array...")
    theAudio = theAudio*3.05175781e-05
    theAudio = AudioArrayClip(theAudio, fps=frameRate) #moviepy read in numpy array
    theAudio.end = theAudio.duration
    return theAudio

# def parse_ass_positioning(theText):
#     #look of '{\an#}'' where # is between 1 &9, inclusive
#     #a failure will have a single element in the list (just text)
#     #a success will return [#,string]
#     #where # is the ASS keypad position on screen
#     #in the event no # is found, return a default of 2
#     theMatchedSplit = re.split('{an([1-9])}(.*)', theText)
#     if len(theMatchedSplit) < 2:
#         theMatchedSplit.insert(0,'')
#         theMatchedSplit.insert(1,2)
#     return theMatchedSplit

# def ass_position_to_imageMagick_position(theNumber):
#     #http://docs.aegisub.org/3.2/ASS_Tags/
#     #https://imagemagick.org/script/command-line-options.php
#     #ASS number tags map like keypad #s
#     #the gravity cardinal values in imagemagick seem e-w inverted
#     #why?
#     if theNumber == 1: return "SouthWest"
#     elif theNumber == 2: return "South"
#     elif theNumber == 3: return "SouthEast"
#     elif theNumber == 4: return "West"
#     elif theNumber == 5: return "Center"
#     elif theNumber == 6: return "East"
#     elif theNumber == 7: return "NorthWest"
#     elif theNumber == 8: return "North"
#     elif theNumber == 9: return "NorthEast"
#     else: return "Center"

def resize(t,holdTime,theStartSizeW,theEndSizeW):
     #calculate the size at time t
    holdTime=float(holdTime)
    if t<holdTime:
        size = 1.0
    else:
        size = theEndSizeW
    return size

def move(t,holdTime,startX,endX,startY,endY,theSlateSize,theClipSize):
    holdTime=float(holdTime)
    theClipW = theClipSize[0]
    theClipH = theClipSize[1]
    theFrameWCntr = theSlateSize[0]/2
    theFrameHCntr = theSlateSize[1]/2
    theClpWCntr = theClipSize[0]/2
    theClpHCntr = theClipSize[1]/2

    #parse if text location is used
    if startX == 'left':
        startX = 0
    if startX == 'center':
        startX = theFrameWCntr-theClpWCntr
    if startX == 'right':
        startX = theSlateSize[0]-theClipW

    if startY == 'top':
        startY = 0
    if startY == 'center':
        startY = theFrameHCntr-theClpHCntr
    if startY == 'bottom':
        startY = theSlateSize[1]-theClipH

    if endX == 'left':
        endX = 0
    if endX == 'center':
        endX = theFrameWCntr-theClpWCntr
    if endX == 'right':
        endX = theSlateSize[0]-theClipW

    if endY == 'top':
        endY = 0
    if endY == 'center':
        endY = theFrameHCntr-theClpHCntr
    if endY == 'bottom':
        endY = theSlateSize[1]-theClipH
        #endY = theSlateSize[1]

    #calculate the X at time t
    if t<holdTime:
        x = startX
        y = startY
    else:
        x = endX
        y = endY

    return (x,y)



def calcPos(t,holdTime,startX,endX,startY,endY,theSlateSize,theClipSize):
    holdTime=float(holdTime)
    theClipW = theClipSize[0]
    theClipH = theClipSize[1]
    theFrameWCntr = theSlateSize[0]/2
    theFrameHCntr = theSlateSize[1]/2
    theClpWCntr = theClipSize[0]/2
    theClpHCntr = theClipSize[1]/2

    #parse if text location is used
    if startX == 'left':
        startX = 0
    if startX == 'center':
        startX = theFrameWCntr-theClpWCntr
    if startX == 'right':
        startX = theSlateSize[0]-theClipW

    if startY == 'top':
        startY = 0
    if startY == 'center':
        startY = theFrameHCntr-theClpHCntr
    if startY == 'bottom':
        startY = theSlateSize[1]-theClipH

    if endX == 'left':
        endX = 0
    if endX == 'center':
        endX = theFrameWCntr-theClpWCntr
    if endX == 'right':
        endX = theSlateSize[0]-theClipW

    if endY == 'top':
        endY = 0
    if endY == 'center':
        endY = theFrameHCntr-theClpHCntr
    if endY == 'bottom':
        endY = theSlateSize[1]-theClipH
        #endY = theSlateSize[1]

    #this slop method sucks. STH 2020-0803
    #slope of line to get from start to end
    rise = endY-startY

    run = endX-startX
    slope = rise/run
    b = startY-slope

    #calculate the X at time t
    if endX<startX: 
        theClipW=0-theClipW
    if t<holdTime:
        x = startX
        y = startY
    else:
        if endX<startX:
            x = max(endX,startX+theClipW*(t-holdTime))
        else:
            x = min(endX,startX+theClipW*(t-holdTime))

        #use the calculated x to find y @ time t using slope
        y = (slope*x)+b

    return (x,y)


# def audio_duck(sound, position, duration, gain=-15.0, fade_duration=500):
#     #stackoverflow.com/questions/33880261/bad-quality-after-multiple-fade-effect-with-pydub
#     #retrieved 2020-0608
#     """
#     sound - an AudioSegment object
#     position - how many milliseconds into the sound the duck should 
#         begin (this is where overlaid audio could begin, the fade down
#         will happen before this point)
#     duration - how long should the sound stay quiet (milliseconds)
#     gain - how much quieter should the sound get (in dB)
#     fade_duration - how long sound the fades last (in milliseconds)
#     """

#     # this part is from the beginning until the end of the ducked section
#     print("duck duck goose")
#     print(position)
#     print(duration)
#     print(gain)
#     print(fade_duration)
#     the_prefix = sound[0:position]
#     the_ducked = sound[position:position+duration]
#     the_suffix = sound[position+duration:]
#     print(len(the_prefix))
#     print(len(the_ducked))
#     print(len(the_suffix))
#     sys.exit()
#     # first_part = sound[:position+duration]
#     # first_part = first_part.fade(to_gain=gain, end=position, duration=fade_duration)

#     # # this part begins where the fade_up happens (will just fade in)
#     # second_part = sound[position+duration:]
#     # second_part = second_part.fade(from_gain=gain, start=0, duration=fade_duration)

#     # return first_part + second_part


def readStartStopTimes(theAlignmentFile, metaDataList):
    #this will fail if the last entry has to "end" data
    #might need to look at the mp3 and get the time length
    theLastTimePoint = theAlignmentFile['stop'].iat[-1] #this should be the last recorded time in the alignment file
    metaDataList = list(theAlignmentFile['meta'])

    ##########################################################################################
    #look at the alignment file and see if the meta data defines the start and stop points
    if 'start' in metaDataList:
        startDataList = list(theAlignmentFile['start'])
        i = metaDataList.index('start')
        lectureStartTime=startDataList[i]
        print("         Lecture start meta data found: %s" % lectureStartTime)
    else:
        lectureStartTime = 0.0 #seconds
        print("         No explicit start. Start set to: %s" % lectureStartTime)
    if 'stop' in metaDataList:
        stopDataList = list(theAlignmentFile['stop'])
        i = metaDataList.index('stop')
        lectureStopTime=stopDataList[i]
        print("         Lecture stop meta data found: %s" % lectureStopTime)
    else:
        lectureStopTime=theLastTimePoint
        print("         No explicit stop. Stop set to: %s" % lectureStopTime)
    ##########################################################################################
    return [lectureStartTime, lectureStopTime]


def makeSRTVFile(theLectureName, theSRTVIndexList, theSlideList, theSlideDir, metaDataList, startDataList, stopDataList, lectureStartTime, lectureStopTime, theSRTVDir, theSRTDir):
    theSlideDir = os.path.join(theSlideDir,theLectureName)
    theSRTVList = []
    theSRTList = []
    #I should have made things a form of json form the start
    # :( STH 2020-0805
    ###some things will just be in the meta column and not have a corresponding
    ###item in the slide column
    jsonifier = '{%s}'
    for i in range(len(metaDataList)):
        theStr = metaDataList[i]
        jsonText = '{%s}' % theStr
        try:
            jsonDict = json.loads(jsonText)
            if 'cut' in jsonDict.keys():
                if 'duration' in jsonDict['cut'].keys():
                    theDuration = float(jsonDict['cut']['duration'])
                    theStart = float(startDataList[i])
                    theStop = theStart+theDuration
                    theIndex = len(theSRTVList)+1
                    print("                %s --> %s" %(datetime.timedelta(seconds=theStart+float(lectureStartTime)), datetime.timedelta(seconds=theStop+float(lectureStartTime))))
                    theStart = datetime.timedelta(seconds=theStart) #convert to datetime
                    theStop = datetime.timedelta(seconds=theStop) #convert to datetime

                    theSRTVList.append(srt.Subtitle(theIndex,theStart,theStop,"na",str(jsonDict)))
        except:
            continue

    allMediaSuffixList = imageSuffixList + videoSuffixList + audioSuffixList
    for i in range(len(theSRTVIndexList)):
        theSlide = theSlideList[theSRTVIndexList[i]]
        print("             %s" % (theSlide))
        theFileSuffix = os.path.splitext(theSlide)[1]
        if (theFileSuffix in allMediaSuffixList):
            theSlide = os.path.join(theSlideDir,theSlide)

        theMeta = str(metaDataList[theSRTVIndexList[i]])
        theStart = float(startDataList[theSRTVIndexList[i]])
        theStop = ""
        theMetaList= [x.strip() for x in theMeta.split(';')]
        if i == len(theSRTVIndexList)-1:
            #this just pads the ends so last slide stays up to the end
            theStop = float(lectureStopTime+outroDuration)
        elif theFileSuffix in videoSuffixList:
            #read in the video clip
            theVideoClip = VideoFileClip(theSlide)
            #start parsing the meta data
            for aMetaArg in theMetaList:
                ###########################
                #split the arg and values
                theMetaArgList = [x.strip() for x in aMetaArg.split(':')]
                theArg = theMetaArgList[0]
                if len(theMetaArgList)>1: theValue = theMetaArgList[1]
                ###########################
                if theArg == "loop":
                    #default the looping to stop when the next slide starts
                    theStop = float(startDataList[theSRTVIndexList[i+1]])
                if theArg == "duration":
                    #if an explicit duration is provided, use that
                    theStop = float(theStart+float(theValue))
                elif theStop == "":
                    #if no duration is provided, and if it's not looped, the duration should be the video length
                    theDuration = theVideoClip.duration #in seconds
                    theStop = float(theStart+theDuration)
                #startDataList[theSRTVIndexList[i+1]]=theStop
        elif theFileSuffix in audioSuffixList:
            #this section is for audio replace
            theStop = float(stopDataList[theSRTVIndexList[i]])
        elif theFileSuffix == "" or (os.path.exists(os.path.join(theSlideDir,theSlideList[theSRTVIndexList[i]])) == False):
            #this section is for text overlays
            #need to have it written to a unique srt file
            #lectureStartTime = datetime.timedelta(seconds=lectureStartTime) #convert to datetime
            theStart = float(startDataList[theSRTVIndexList[i]])-float(lectureStartTime)
            theStop = float(stopDataList[theSRTVIndexList[i]])-float(lectureStartTime)
            #convert theMeta to a list
            #theMetaList =theMeta.split(';')
            for aMetaArg in theMetaList:
                ###########################
                #split the arg and values
                theMetaArgList = [x.strip() for x in aMetaArg.split(':')]
                theArg = theMetaArgList[0]
                if len(theMetaArgList)>1: theValue = theMetaArgList[1]
                ###########################
                # for j in theMetaList:
                #     theSublist = j.split(":")
                #if there is a defined duration, use that as theStop
                if theArg == "duration":
                    theTextDuration = float(theValue)
                    theStop = (float(startDataList[theSRTVIndexList[i]])+theTextDuration)-float(lectureStartTime)
            print("                %s --> %s" %(datetime.timedelta(seconds=theStart+float(lectureStartTime)), datetime.timedelta(seconds=theStop+float(lectureStartTime))))
            if theMeta == "nan": theMeta = ""
            theStart = datetime.timedelta(seconds=theStart+theSlateDuration) #convert to datetime
            theStop = datetime.timedelta(seconds=theStop+theSlateDuration) #convert to datetime
            theSRTList.append(srt.Subtitle(i,theStart,theStop,theSlide,theMeta))
            continue #move to the next item in theSRTVIndexList
        else:
            #this is sort of complicated
            #a slide image should end when the next slide OR video starts
            #it should not end when an audio clip begins
            #it should not end when a text overlay beings
            #so if the following entries are an audio clip OR a text overlay, ignore it
            ####NEW
            #start parsing the meta data
            for aMetaArg in theMetaList:
                ###########################
                #split the arg and values
                theMetaArgList = [x.strip() for x in aMetaArg.split(':')]
                theArg = theMetaArgList[0]
                if len(theMetaArgList)>1: theValue = theMetaArgList[1]
                ###########################
                if theArg == "duration":
                    #if an explicit duration is provided, use that
                    theStop = float(theStart+float(theValue))
            ############
            if theStop=="":
                while (os.path.splitext(theSlideList[theSRTVIndexList[i+1]])[1] in audioSuffixList) or (os.path.exists(os.path.join(theSlideDir,theSlideList[theSRTVIndexList[i+1]])) == False):
                    i=i+1
                theStop = float(startDataList[theSRTVIndexList[i+1]])

        theStart = datetime.timedelta(seconds=theStart) #convert to datetime
        theStop = datetime.timedelta(seconds=theStop) #convert to datetime

        print("                %s --> %s" %(theStart, theStop))

        if theMeta == "nan": theMeta = ""
        theIndex = len(theSRTVList)+1
        theSRTVList.append(srt.Subtitle(theIndex,theStart,theStop,theSlide,theMeta))

    ###save an actual srt file
    if theSRTList != []:
        theFileName = theLectureName+".srt"
        theFileName = os.path.join(theSRTDir, theFileName)
        with open(theFileName, "w") as theFile:
            theFile.write(srt.compose(theSRTList))
        print("          SRT file generated\n")

    ###save the data as a modified version of a srt file
    theFileName = theLectureName+".srtv"
    theFileName = os.path.join(theSRTVDir, theFileName)
    with open(theFileName, "w") as theFile:
        theFile.write(srt.compose(theSRTVList))
    print("          Hacky SRT-video file generated\n")
    #need to reindex subtitles based on start time
    #there must be a better way, but this should work
    theSRTVList = srt.compose(theSRTVList)
    theSRTVList = list(srt.parse(theSRTVList))
    return theSRTVList
    ##########################################################################################


def processAudio(theSRTVList, theAudioDir, theLectureName, lectureStartTime, lectureStopTime):
    audioFilePath = os.path.join(theAudioDir, theLectureName+".mp3")
    theLectureAudio = "" #just a place holder that gives a logic check later
    madeAnAudioEdit = False

    #I should have made things a form of json form the start
    # :( STH 2020-0805
    for anEntry in theSRTVList:    
        theMetaList = [x.strip() for x in anEntry.proprietary.split(';')]
        theGain = 0 #no ducking
        theSlide = anEntry.content
        theFileSuffix = os.path.splitext(theSlide)[1]
        ##########################################################################################
        for aMetaArg in theMetaList:

            ###########################
            #split the arg and values
            theMetaArgList = [x.strip() for x in aMetaArg.split(':')]
            theArg = theMetaArgList[0]
            if len(theMetaArgList)>1: theValue = theMetaArgList[1]
            ###########################
            if theArg == "lecture":
                theSubValue = [x.strip() for x in theValue.split(',')]
                if theSubValue[0] == "mute":
                    thePosition = ((anEntry.start).total_seconds())*1000.0 #convert to millisec
                    theStop = ((anEntry.end).total_seconds())*1000.0 #convert to millisec
                    theDuration = theStop-thePosition
                    if len(theSubValue)>1:
                        #theStop = float(theSubValue[1])*1000.0 #convert to millisec
                        #theDuration = theStop-thePosition
                        theDuration = float(theSubValue[1])*1000.0 #convert to millisec

                    #duck the lecture if indicated
                    if madeAnAudioEdit == False: print("          Audio edits detected...")
                    if theLectureAudio == "": 
                        print("          Loading audio file %s" % audioFilePath)
                        theLectureAudio = AudioSegment.from_file(audioFilePath)
                    theGain = -100 #duck the audio if the meta data says to mute the lecture audio
                    
                    print("              Ducking audio at time %s seconds" % (thePosition/1000))
                    print("                 Duration will be %s seconds" % (theDuration/1000))
                    #make a silent audio clip
                    theSilence= AudioSegment.silent(duration=theDuration)
                    theLectureAudio = theLectureAudio.overlay(theSilence, position=(thePosition), gain_during_overlay=theGain)
                    #the following might be a saner way to do this:
                    #theLectureAudio = theLectureAudio.fade(to_gain=theGain, start=thePosition, end=theStop)
                    madeAnAudioEdit = True

        ##########################################################################################
        #insert pad (silent) audio if needed
        #will probably need to provide a way to insert into existing audio
        #but for simplicity right now, just assume that pad gets put at the start
        #STH 2020-0621
        if 'lecture:insert' in theMetaList:
            if madeAnAudioEdit == False: print("          Audio edits detected...")
            if theLectureAudio == "": 
                print("          Loading audio file %s" % audioFilePath)
                theLectureAudio = AudioSegment.from_file(audioFilePath)
            theDuration = 5.0 #just give it a default
            for j in theMetaList:
                theSublist = [x.strip() for x in j.split(':')]
                if theSublist[0].strip() == "duration":
                    theDuration = float(theSublist[1]) #if there is a defined duration, use that                  
            print("              Inserting pad silence at start. %s seconds" % (theDuration))
            theLectureAudio = AudioSegment.silent(duration=theDuration*1000)+theLectureAudio #x1000 to convert sec to millisec
        ##########################################################################################
        #This section does things like insert the correct word if you screwed up in lecture
        #The cannonical example is saying "latitude" when you(I) mean "longitude"
        if theFileSuffix in audioSuffixList:
            #only load the lecture audio once
            if madeAnAudioEdit == False: print("          Audio edits detected...")
            if theLectureAudio == "": 
                print("          Loading audio file %s" % audioFilePath)
                theLectureAudio = AudioSegment.from_file(audioFilePath)       
            thePosition = ((anEntry.start).total_seconds()+allPadDuration)*1000.0 #convert to millisec
            #theStop = ((anEntry.end).total_seconds())*1000.0 #convert to millisec
            if 'replace' in theMeta:
                #theAudioClip = AudioSegment.from_file(audioFilePath)
                theAudioClip = AudioSegment.from_file(theSlide)  
                theGain = -100 #duck the audio if the meta data says replace
            print("              Replacing audio at time %s seconds" % (thePosition/1000))
            theLectureAudio = theLectureAudio.overlay(theAudioClip, position=(thePosition), gain_during_overlay=theGain)
            madeAnAudioEdit = True


    ##########################################################################################
    #trim the audio to fit lectureStartTime & lectureStopTime
    #multiply lectureStartTime & lectureStopTime by 1000 because pydup does things in milliseconds
    #This is important: this trim action is done at the end because the srtv file records the timing
    #of all events from start of audio, not from start point. 
    #if you duck audio, the time is from start of audio, not from designated start
    #if you trim first the time of the duck is thrown off.
    #This can be fixed 
    theLastTimePoint = theSRTVList[-1].end
    if (lectureStartTime != 0.0) or (lectureStopTime != theLastTimePoint):
        if madeAnAudioEdit == False: print("          Audio edits detected...")
        if theLectureAudio == "": 
            print("          Loading audio file %s" % audioFilePath)
            theLectureAudio = AudioSegment.from_file(audioFilePath)
        print("          Editing audio length")
        theLectureAudio = theLectureAudio[int(lectureStartTime*1000.0):int(lectureStopTime*1000.0)]
        madeAnAudioEdit = True

    ##########################################################################################
    if madeAnAudioEdit==True:
        print("          Saving edited audio as a new copy...")
        (thePath, theName) = os.path.split(audioFilePath)
        theName="EDITED - "+theName
        audioFilePath = os.path.join(thePath,theName)
        theLectureAudio.export(audioFilePath, format="mp3")
    return audioFilePath



def makeVideoFromSRTVList(theSRTVList, theSlideDir, audioFilePath, theLectureName, theCandidateVideoDir):
    theSlideList = []
    theCompositList = []
    theTextClipList = []
    cutList = []
    #####insert the slate at the start
    theSlideDir = os.path.join(theSlideDir,theLectureName)
    theSlate = os.path.join(theSlideDir,"Slide0.png")
    theCandidateVideoPath = os.path.join(theCandidateVideoDir,theLectureName+".mp4")
    if os.path.exists(theSlate):
        theSlateSize = Image.open(theSlate).size   #This will be used to resize videos later

        ################################################################################
        #load in the lecture audio file
        #need to load this in first in case you need to duck lecture audio 
        print("          Loading audio file %s" % audioFilePath)
        theLectureAudio = AudioSegment.from_file(audioFilePath)
        theAudioFrameRate = theLectureAudio.frame_rate #needed later to convert numpy array

        ################################################################################
        ###There can be a situation where there are no slides immediately after the slate
        ###This inserts a black filler slide
        ###Do this once to make a leader if needed
        if ((theSRTVList[0].start).total_seconds() != 0.0) and ("start" not in theSRTVList[0].proprietary):
                #theDuration = theSRTVList[0].start.total_seconds()-theSlateDuration #subtract out the duration of the start slate
                theDuration = theSRTVList[0].start.total_seconds() #no need to subtract the slate duration if slate gets inserted at the end of the process
                theSlideList.append(ImageClip(theLeaderImage).set_duration(theDuration))

        for i in theSRTVList:
            overlayClip = False

            theMetaList = [x.strip() for x in i.proprietary.split(';')]
            if "start" in theMetaList:
                theStartOffset = (i.start).total_seconds()
            if "stop" in theMetaList:break

            theContent= i.content
            theDuration = (i.end-i.start).total_seconds()
            theFileSuffix = os.path.splitext(theContent)[1]
            if theFileSuffix in videoSuffixList:
                print("          Generating video clip...")
                theVideoClip = VideoFileClip(theContent)

                # resize (keep aspect ratio)
                #theVideoClip = theVideoClip.fx(vfx.resize, width=theSlateSize[0]*0.8)
                if theVideoClip.w>theSlateSize[0]:
                    print("          Video is too wide. Resizing...")
                    theVideoClip = theVideoClip.fx(vfx.resize, width=theSlateSize[0])
                if theVideoClip.h>theSlateSize[1]:
                    print("          Video is too high. Resizing...")
                    #theVideoClip = theVideoClip.fx(vfx.resize, height=theSlateSize[1]*0.8)
                    theVideoClip = theVideoClip.fx(vfx.resize, height=theSlateSize[1])
                for aMetaArg in theMetaList:
                    ###########################
                    #split the arg and values
                    theMetaArgList = [x.strip() for x in aMetaArg.split(':')]
                    theArg = theMetaArgList[0]
                    if len(theMetaArgList)>1: theValue = theMetaArgList[1]
                    ###########################
                    # print("          Generating video clip...")
                    # theVideoClip = VideoFileClip(theContent)

                    # # resize (keep aspect ratio)
                    # #theVideoClip = theVideoClip.fx(vfx.resize, width=theSlateSize[0]*0.8)
                    # if theVideoClip.w>theSlateSize[0]:
                    #     print("          Video is too wide. Resizing...")
                    #     theVideoClip = theVideoClip.fx(vfx.resize, width=theSlateSize[0])
                    # if theVideoClip.h>theSlateSize[1]:
                    #     print("          Video is too high. Resizing...")
                    #     #theVideoClip = theVideoClip.fx(vfx.resize, height=theSlateSize[1]*0.8)
                    #     theVideoClip = theVideoClip.fx(vfx.resize, height=theSlateSize[1])

                    ###########################
                    if theArg == "overlay" in theMetaList:
                        #default location placement should be slide center
                        #This should probably be abstracted out to a function. 
                        #it's going to be used in multiple locations probably
                        SWC = int(theSlateSize[0]/2) #SlideWidthCenter (SWC)
                        SHC = int(theSlateSize[1]/2) #SlideHeightCenter (SHC)
                        CWC = int(theVideoClip.w/2) #ClipWidthCenter (CWC)
                        CHC = int(theVideoClip.h/2) #ClipHeightCenter (CHC)
                        #theVideoClip=theVideoClip.set_position((SWC-CWC, SHC-CHC))
                        theVideoClip=theVideoClip.set_position((SWC-CWC, SHC-CHC))
                        overlayClip = True
                    if theArg == "video":
                        if theValue == "mute": 
                            #theVideoClip = VideoFileClip(theContent, audio=False)
                            theVideoClip = theVideoClip.without_audio()
                        #else:
                            #theVideoClip = VideoFileClip(theContent, audio=True)
                    if theArg == "loop":
                        theVideoClip = theVideoClip.fx(vfx.loop, duration=theDuration)
                    if theArg == "duration":
                        theDuration = float(theValue)
                        if theDuration > theVideoClip.duration:
                            #the specified duration is longer than the video. Loop it
                            theVideoClip = theVideoClip.fx(vfx.loop, duration=theDuration)
                        if theDuration < theVideoClip.duration:
                            #the specified duration is less than the video. Trim it
                            theVideoClip = theVideoClip.set_end(theDuration)
                    if theArg == "resize":
                        theParams = [x.strip() for x in theValue.split(',')]
                        holdTime = float(theParams[0])
                        theSizeRatio = float(theParams[1])
                        ###
                        theStartSizeW = theVideoClip.w
                        theEndSizeW = theStartSizeW*theSizeRatio
                        theEndSizeW = theSizeRatio
                        orgX = theVideoClip.pos(0)[0]
                        orgY = theVideoClip.pos(0)[1]
                        ###
                        theVideoClip = theVideoClip.resize(lambda t : (resize(t,holdTime,theStartSizeW,theEndSizeW)))
                        #after you resize, make sure th xy location remains the same
                        #theVideoClip = theVideoClip.set_position((orgX,orgY))
                    if theArg == "move":
                        theMoveParams = [x.strip() for x in theValue.split(',')]
                        holdTime = theMoveParams[0]
                        endX = theMoveParams[1]
                        endY = theMoveParams[2]
                        ###
                        startX = theVideoClip.pos(0)[0] #what is the X position of the clip at time 0
                        startY = theVideoClip.pos(0)[1] #what is the Y position of the clip at time 0
                        theClipSize = theVideoClip.size
                        theVideoClip = theVideoClip.set_position(lambda t:(move(t,holdTime,startX,endX,startY,endY,theSlateSize,theClipSize)))
                    if theArg == "animove":
                        #does not work great
                        #STH 2020-0803
                        theMoveParams = [x.strip() for x in theValue.split(',')]
                        holdTime = theMoveParams[0]
                        endX = theMoveParams[1]
                        endY = theMoveParams[2]
                        startX = theVideoClip.pos(0)[0] #what is the X position of the clip at time 0
                        startY = theVideoClip.pos(0)[1] #what is the Y position of the clip at time 0
                        theClipSize = theVideoClip.size
                        theVideoClip = theVideoClip.set_position(lambda t:(calcPos(t,holdTime,startX,endX,startY,endY,theSlateSize,theClipSize)))
                    if theArg == "aniresize":
                        #does not work great
                        #STH 2020-0803
                        #this needs to be fixed to make it more like move(allowing for hold time)
                        theSize = float(theValue)
                        theVideoClip = theVideoClip.resize(lambda t : 1-0.02*t)

                    ###########################


                if overlayClip == True:
                    theVideoClip=theVideoClip.set_start(i.start.total_seconds()-theStartOffset+theSlateDuration)
                    # #default location placement should be slide center
                    # #This should probably be abstracted out to a function. 
                    # #it's going to be used in multiple locations probably
                    # SWC = int(theSlateSize[0]/2) #SlideWidthCenter (SWC)
                    # SHC = int(theSlateSize[1]/2) #SlideHeightCenter (SHC)
                    # CWC = int(theVideoClip.w/2) #ClipWidthCenter (CWC)
                    # CHC = int(theVideoClip.h/2) #ClipHeightCenter (CHC)
                    # #theVideoClip=theVideoClip.set_position((SWC-CWC, SHC-CHC))
                    # theVideoClip=theVideoClip.set_position((SWC-CWC, SHC-CHC))
                    theCompositList.append(theVideoClip)
                else:
                    theSlideList.append(theVideoClip)
                ########################################################
            elif theFileSuffix in audioSuffixList:
                print("          Generating audio clip...")
                if "replace" in theMetaList:
                    bla=1
            elif theFileSuffix in imageSuffixList:
                print("          Generating image clip...")
                aSlide = ImageClip(theContent).set_duration(theDuration)
                if aSlide.w>theSlateSize[0]:
                    print("          Image is too wide. Resizing...")
                    #aSlide = aSlide.fx(vfx.resize, width=theSlateSize[0]*0.9)
                    aSlide = aSlide.fx(vfx.resize, width=theSlateSize[0])
                if aSlide.h>theSlateSize[1]:
                    print("          Image is too high. Resizing...")
                    #aSlide = aSlide.fx(vfx.resize, width=theSlateSize[1]*0.9)
                    aSlide = aSlide.fx(vfx.resize, height=theSlateSize[1])
                theSlideList.append(aSlide)
            else:
                print("          Not video, image, or audio...")
                for aMetaArg in theMetaList:
                    try:
                        aMetaArg = aMetaArg.replace("'", '"')
                        jsonDict = json.loads(aMetaArg)
                        if 'cut' in jsonDict.keys():
                            if 'duration' in jsonDict['cut'].keys():
                                theStart = (i.start).total_seconds()
                                # theStop = (i.end).total_seconds()
                                theStop = (i.end).total_seconds()+theSlateDuration
                                cutList.append([theStart,theStop])
                    except:
                       continue


        ################################################################################        
        #insert the slate at the start
        theSlateClip = ImageClip(theSlate).set_duration(theSlateDuration)
        theSlideList.insert(0,theSlateClip)

        ################################################################################
        #with length editing, the slate should be inserted right at the end, after subclip is made
        print("          Concatenating image and video clips...")
        catedVideo = concatenate_videoclips(theSlideList, method="compose")
        #Set the size back to slate size
        #there is a bug related to clip resizing I have not tracked down yet
        #STH 0802-2020
        catedVideo = catedVideo.fx(vfx.resize, width=theSlateSize[0])
        #catedVideo = catedVideo.fx(vfx.resize, (theSlateSize[0],theSlateSize[1]))
        
        ################################################################################
        #insert the initial silence for the opening slate
        if theSlateDuration > 0:
            print("          Adding slate intro buffer...")
            theLectureAudio = AudioSegment.silent(duration=theSlateDuration*1000)+theLectureAudio #x1000 to convert sec to millisec
        #durationInSeconds = len(theLectureAudio)/1000

        ################################################################################
        #convert the pydub audio into something moviepy can use
        theLectureAudio = pydub_to_moviepy(theLectureAudio, theAudioFrameRate)
        ################################################################################


        #composit the video audio with the lecture audio
        #print("          Combining video and lecture audio...")
        #print(vars(video.audio))
        #print(vars(theLectureAudio))
        ################################################################################
        if catedVideo.audio != None:
            theMoviePyAudio = catedVideo.audio
            theCompositeAudio = CompositeAudioClip([theMoviePyAudio, theLectureAudio])
        else:
            theCompositeAudio = theLectureAudio

        ################################################################################
        finalVideo = catedVideo.set_audio(theCompositeAudio)

        if theCompositList!=[]:
            #use wisely
            #doing this is a slow process.
            #theCompositList.append(finalVideo)
            theCompositList.insert(0,finalVideo)
            #finalVideo = CompositeVideoClip([finalVideo,theCompositList[0].set_start(2)])
            finalVideo = CompositeVideoClip(theCompositList)

        ################################################################################
        finalVideo.write_videofile(theCandidateVideoPath, fps=12, audio=True, write_logfile=False, threads=4)
        return cutList

    else:
        print("Slate slide not found")


if __name__ == '__main__':
    timerStartTime = datetime.datetime.now()

    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--mksrt', metavar='', dest='mksrt', default=True, required=False, help='make srt & srvt files?' )
    parser.add_argument('--editaudio', metavar='', dest='editaudio', default=True, required=False, help='make edits to audio according to alignment file?' )
    parser.add_argument('--mkvideo', metavar='', dest='mkvideo', default=True, required=False, help='generate the final video?' )
    parser.add_argument('--addsrt', metavar='', dest='addsrt', default=True, required=False, help='add text overlays from srt(if exists)?' )

    parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='output/lecture_alignments', required=False, help='path to alignment file directory')
    parser.add_argument('--srtvDir', metavar='', dest='theSRTVDir', default='output/lecture_srtv', required=False, help='path to SRTV file directory')
    parser.add_argument('--srtDir', metavar='', dest='theSRTDir', default='output/lecture_srt', required=False, help='path to SRT file directory')
    parser.add_argument('--audioDir', metavar='', dest='theAudioDir', default='output/processed_audio', required=False, help='path to folder containing processed mp3s' )
    parser.add_argument('--slideDir', metavar='', dest='theSlideDir', default='output/lecture_slides', required=False, help='general path to slide images')
    parser.add_argument('--videoOut', metavar='', dest='theCandidateVideoDir', default='output/candidate_video', required=False, help='path to the folder videos will be written to')
    args = parser.parse_args()
    print(args)

    #check and see if boolean things are boolean
    if isinstance(args.mksrt, str):
        args.mksrt = booleanCheck(args.mksrt)
    if isinstance(args.editaudio, str):
        args.editaudio = booleanCheck(args.editaudio)
    if isinstance(args.mkvideo, str):
        args.mkvideo = booleanCheck(args.mkvideo)
    if isinstance(args.addsrt, str):
        args.addsrt = booleanCheck(args.addsrt)

    theSlideDir = pathExistsMake(args.theSlideDir)
    theAlignmentDir = pathExistsMake(args.theAlignmentDir)
    theAudioDir = pathExistsMake(args.theAudioDir)
    theSRTDir = pathExistsMake(args.theSRTDir, True)
    theSRTVDir = pathExistsMake(args.theSRTVDir, True)
    theCandidateVideoDir = pathExistsMake(args.theCandidateVideoDir, True)
    theLeaderImage = pathExistsMake(theLeaderImage)

    ###Start reading in alignment files from the alignment directory
    tempVar = os.path.join(theAlignmentDir, "*.csv")
    for theFileName in glob.glob(tempVar):
        theLectureName = os.path.basename(theFileName)
        print("         File found. Opening '%s'" % theLectureName)
        theLectureName = os.path.splitext(theLectureName)[0]
        theAlignmentFile = pd.read_csv(theFileName, header=None, names=['word','match','start','stop','token','slide','meta'], encoding = "ISO-8859-1")

        startDataList = list(theAlignmentFile['start'])
        stopDataList = list(theAlignmentFile['stop'])
        theSlideList = list(theAlignmentFile['slide'])
        metaDataList = list(theAlignmentFile['meta'])

        ###Read the alignment file and try to get lecture start/stop data
        lectureStartTime, lectureStopTime = readStartStopTimes(theAlignmentFile, metaDataList)

        theSRTVIndexList=indexListMatchingElement(theSlideList, "nan")

        theSRTVList = []
        if args.mksrt == True:
            if theSRTVIndexList:
                theSRTVList = makeSRTVFile(theLectureName, theSRTVIndexList, theSlideList, theSlideDir, metaDataList, startDataList, stopDataList, lectureStartTime, lectureStopTime, theSRTVDir, theSRTDir)
            else:
                print("         No slide info found. Skipping.\n")
        elif (args.editaudio == True) or (args.mkvideo == True):
            #need the srtv file for processing audio and/or making the video
            theFileName = theLectureName+".srtv"
            theFileName = os.path.join(theSRTVDir, theFileName)
            theFileName = pathExistsMake(theFileName)
            print("         Opening '%s'" % (theLectureName+".srtv"))
            with open(theFileName) as theFile:
                theFileData = theFile.read()
            theFile.close()
            print("         Parsing '%s'" % (theLectureName+".srtv"))
            theSRTVList=srt.parse(theFileData)
        

        #next will be to use the list returned from makeSRTVFile() to process it and make necessary changes to the audio file
        #should also be an option to read in file eventually
        if args.editaudio == True:
            audioFilePath = processAudio(theSRTVList, theAudioDir, theLectureName, lectureStartTime, lectureStopTime)
        elif args.mkvideo == True:
            #need the audio to make the video
            theFileName = "EDITED - "+theLectureName+".mp3"
            audioFilePath = os.path.join(theAudioDir, theFileName)
            audioFilePath = pathExistsMake(audioFilePath)
            print("         Found '%s'" % (theFileName))
        if args.mkvideo == True:
            if theSRTVList:
               cutList = makeVideoFromSRTVList(theSRTVList, theSlideDir, audioFilePath, theLectureName, theCandidateVideoDir)

        if args.addsrt ==True:
            theSRTFileName = theLectureName+".srt"
            theSRTFileName = os.path.join(theSRTDir, theSRTFileName)
            theSRTFileName = pathExistsMake(theSRTFileName)
            print("         Found '%s'" % (theLectureName+".srt"))
            theVideoFileName = theLectureName+".mp4"
            theVideoFileName = os.path.join(theCandidateVideoDir, theVideoFileName)
            theVideoFileName = pathExistsMake(theVideoFileName)
            print("         Found '%s'" % (theLectureName+".mp4"))

            theCandidateVideoPath = os.path.join(theCandidateVideoDir,theLectureName+"-b.mp4")

            stream = ffmpeg.input(theVideoFileName)
            stream = ffmpeg.output(stream, theCandidateVideoPath, **{'vf': "subtitles="+theSRTFileName+":force_style='Fontname=Impact'"}, **{'c:a': 'copy'}).overwrite_output()
            #print(ffmpeg.compile(stream))
            ffmpeg.run(stream)
            theVideoFileName = theCandidateVideoPath

        if cutList !=[]: 
            print("         Attempting to make cuts to video...")
            stream = ffmpeg.input(theVideoFileName)
            theConcatList = []
            ###############
            cutList = list(itertools.chain.from_iterable(cutList)) #flaten the cutlist
            cutList = [0.0] + cutList  #append 0.0 to the beginning
            cutList = cutList + ['end'] #throw 'end' at the end
            cutList = list(zip(itertools.islice(cutList,None,None,2), itertools.islice(cutList,1,None,2))) #break the flat cutlist into diads
            for cutItem in cutList:
                startTime = cutItem[0]
                stopTime = cutItem[1]
                if stopTime == "end":
                    streamV = stream.trim(start=startTime).setpts ('PTS-STARTPTS')
                    streamA = stream.filter_('atrim', start = startTime).filter_('asetpts', 'PTS-STARTPTS')
                else:
                    theDuration = (stopTime-startTime)+theSlateDuration
                    streamV = stream.trim(start=startTime, duration=theDuration).setpts ('PTS-STARTPTS')
                    streamA = stream.filter_('atrim', start = startTime, duration=theDuration).filter_('asetpts', 'PTS-STARTPTS')
                theConcatList.append(streamV)
                theConcatList.append(streamA)

            joinedStreams = ffmpeg.concat(*theConcatList, v=1, a=1).node
            theCandidateVideoPath = os.path.join(theCandidateVideoDir,theLectureName+"-c.mp4")
            stream = ffmpeg.output(joinedStreams[0], joinedStreams[1], theCandidateVideoPath).overwrite_output()
            print(ffmpeg.compile(stream))
            #sys.exit()
            ffmpeg.run(stream)




            # stream = ffmpeg.input(theVideoFileName)
            # theConcatList = []
            # ###Get the initial part
            # startTime = 0.0
            # stopTime = cutList[0][0] #start time of the first element
            # theDuration = stopTime-startTime
            # streamV = stream.trim(start=startTime, duration=theDuration).setpts ('PTS-STARTPTS')
            # streamA = stream.filter_('atrim', start = startTime, duration=theDuration).filter_('asetpts', 'PTS-STARTPTS')
            # theConcatList.append(streamV)
            # theConcatList.append(streamA)
            # ################
            # i = 0
            # theLength = len(cutList)
            # for cutItem in cutList:
            #     i = i+1
            #     if i< theLength:
            #         startTime = stopTime
            #         stopTime = cutList[i][0]
            #         theDuration = stopTime-startTime
            #         ##############
            #         streamV = stream.trim(start=startTime, duration=theDuration).setpts ('PTS-STARTPTS')
            #         streamA = stream.filter_('atrim', start = startTime, duration=theDuration).filter_('asetpts', 'PTS-STARTPTS')
            #         theConcatList.append(streamV)
            #         theConcatList.append(streamA)
            #         ##############
            # print(startTime+theDuration)
            # ###This includes the final chunk
            # startTime = cutList[-1][1] #stop time of the last element
            # startTime = startTime+theDuration
            # streamV = stream.trim(start=startTime).setpts ('PTS-STARTPTS')
            # streamA = stream.filter_('atrim', start = startTime).filter_('asetpts', 'PTS-STARTPTS')
            # theConcatList.append(streamV)
            # theConcatList.append(streamA)

            # print(theConcatList)


            # joinedStreams = ffmpeg.concat(*theConcatList, v=1, a=1).node

            # theCandidateVideoPath = os.path.join(theCandidateVideoDir,theLectureName+"-c.mp4")
            # stream = ffmpeg.output(joinedStreams[0], joinedStreams[1], theCandidateVideoPath).overwrite_output()
            # print(ffmpeg.compile(stream))
            # sys.exit()
            # print("****************")
            # ffmpeg.run(stream)


    print(datetime.datetime.now() - timerStartTime)
