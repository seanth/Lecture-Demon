from natsort import natsorted #pip install pandas, https://pypi.org/project/natsort/3.3.0/
import pandas as pd #pip install pandas

import xml.etree.ElementTree as ET
from zipfile import ZipFile
import glob, os, csv, argparse, sys


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

def pathExists(thePath):
  ###does the folder containing audio files exist?
    theFeedback="     Path '%s' found:    %s"
    if os.path.exists(thePath)==False:
        print(theFeedback % (thePath, "FALSE"))
        print("        Exiting.")
        sys.exit()
    else:
        print(theFeedback % (thePath, "TRUE"))
        return os.path.abspath(thePath)




def pptxSlideXML(theFilePath): 
    theArchive = ZipFile(theFilePath, 'r')
    theFileList = theArchive.namelist()
    print("          Parsing file: '%s'" % os.path.basename(theFilePath)) 

    #first get the list of files in the pptx under
    #ppt/slides/ and make sure they are sorted correctly
    #based on their name
    xmlList = []
    for aFile in theFileList:
        if aFile.startswith('ppt/slides/slide') and aFile.endswith('.xml'):
            xmlList.append(aFile)
            xmlList = natsorted(xmlList)
            #print(xmlList)
    theArchive.close()
    return xmlList

def slideTiming(theFilePath,xmlList):
    print("          Extracting slide timings from: '%s'" % os.path.basename(theFilePath)) 
    theArchive = ZipFile(theFilePath, 'r')
    #now read in each xml file and try to recover
    #information about the timing of the slides
    timingList = []
    for aFile in xmlList:
        #recover the slide name and reform it
        #this should result in strings like: Slide1.png
        theSlideName = os.path.basename(aFile)
        theSlideName = os.path.splitext(theSlideName)[0]
        theSlideName = theSlideName.capitalize()+".png"

        theFileData = theArchive.open(aFile)

        xmlTree=ET.iterparse(theFileData, events=("start", "end"))
        xmlTree =iter(xmlTree)
        #the event will be either the start <b> of something or the end </b>
        theDuration = 0.0
        for theEvent,theElement in xmlTree:
            if theEvent == "start" and 'advTm' in theElement.keys():
                theDuration = theElement.get('advTm')
                if type(theDuration)==int:  
                    exit
        #the duration is in milliseconds.
        #convert to seconds
        print(theDuration)
        theDuration = float(theDuration)/1000.0
        timingList.append([theDuration,theSlideName])
    theArchive.close()
    return timingList

def saveTiming(timingList, theTimingDir, theBaseName):
    #now write out that info on slide duration and slide name
    timingFileName = theBaseName+"-timing.csv"
    timingFilePath = os.path.join(theTimingDir,timingFileName)
    print("          Saving timings to: '%s'" % timingFilePath) 
    with open(timingFilePath, 'w', newline='') as csvFile:
        theWriter = csv.writer(csvFile, delimiter=',')
        for aCueTime in timingList:
            theWriter.writerow(aCueTime)

def insertTimings(theAlignmentFile, theTimingFile):
    print("          Opening alignment file: '%s'" % theAlignmentFile)
    theFileName = os.path.basename(theAlignmentFile)
    theAlignmentRead = pd.read_csv(theAlignmentFile, header=None, names=['word','match','start','stop','token','slide', 'meta'], dtype={'slide':'object', 'meta':'object'})
    theTimingRead = pd.read_csv(theTimingFile, header=None, names=['start','slide'])
    #theTimingRead = theTimingRead[1:]
    metaDataList = list(theAlignmentRead['meta'])
    ##########################################################################################
    #look at the alignment file and see if the meta data defines the start and stop points
    startRow=''
    if 'start' in metaDataList:
        startDataList = list(theAlignmentRead['start'])
        startRow = metaDataList.index('start')
        lectureStartTime=startDataList[startRow]
        print("         Lecture start meta data found: %s" % lectureStartTime)
        ####if there is not a slide listed next to the start meta, insert slide 1
        if type(theAlignmentRead.at[startRow,'slide']) == float: 
            print("         No start slide found. Inserting....")
            theAlignmentRead.at[startRow,'slide'] = 'Slide1.png'

    else:
        lectureStartTime = 0.0 #seconds
        print("         No explicit start. Start set to: %s" % lectureStartTime)
        #print("             Inserting start notation and slide marker....")
        #theAlignmentRead.at[0,'meta'] ='start' 
        #theAlignmentRead.at[0,'slide'] ='Slide1.png'

    #this list is the _duration_ of each slide.
    #we're going to turn it into the start time 
    #of when a slide appears
    ###we call the duration column 'start' so we
    ###can align it with the alignment file column
    ###that uses the name 'start'
    durationList = list(theTimingRead['start'])
    timingList=[]
    t=lectureStartTime

    for i,aDuration in enumerate(durationList):
        #the timing of the first slide can be pretty
        #long leading into lecture as the start slide
        #is on display. Ignore that start value and
        #set the start value to 0
        #if i==0: aDuration = 0.0
        # if i==0:
        #     theStart=t
        #     t=t+aDuration
        #     timingList.append(theStart)
        # else:
        theStart=t
        t=t+aDuration
        timingList.append(theStart)

    theTimingRead['start'] = timingList

    if startRow != '':
        theTimingRead = theTimingRead[1:]

    # #now append that timing data to the end of the 
    # #alignment data frame and sort it by 'start'
    print("         Inserting best calculated slide starts...")
    alignmentWithTiming = pd.concat([theAlignmentRead, theTimingRead])

    print("         Sorting slides by start time...")
    alignmentWithTiming = alignmentWithTiming.sort_values(by='start')

    print("         Writing edited alignment file...")
    #alignmentWithTiming.to_csv('test.csv', header=False)  
    alignmentWithTiming.to_csv(theAlignmentFile, header=False)  



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--path', dest='thePath', required=True, help='Path to the powerpoint file OR path to the timing csv' )
    parser.add_argument('--timing', metavar='', dest='makeTiming', default=True, required=False, help='read pptx and make timing csv?' )
    parser.add_argument('--align', metavar='', dest='mergeTiming', default=True, required=False, help='insert slide timing to alignment csv?' )

    parser.add_argument('--timingDir', metavar='', dest='theTimingDir', default='output/lecture_timing', required=False, help='path to place timings')
    parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='output/lecture_alignments', required=False, help='path to place alignments')
    
    args = parser.parse_args()

    #check and see whether destination folders exist
    theAlignmentDir = pathExistsMake(args.theAlignmentDir)
    theTimingDir = pathExistsMake(args.theTimingDir, True)

    #does the  file exit?
    theFilePath = pathExists(args.thePath)
    theBaseName = os.path.basename(theFilePath)
    theBaseName = os.path.splitext(theBaseName)[0]

    if args.makeTiming == True:        
        xmlFileList = pptxSlideXML(theFilePath)
        #print(xmlFileList)

        #format is: [timing in seconds(float), slide image name(str)]
        timingList = slideTiming(theFilePath,xmlFileList)
        #print(timingList)
        
        saveTiming(timingList, theTimingDir, theBaseName)


    if args.mergeTiming == True:
        theBaseName = theBaseName.strip("-timing")
        #does the alignment file exist?
        theAlignmentFilePath = os.path.join(theAlignmentDir,theBaseName+".csv")
        theAlignmentFilePath = pathExists(theAlignmentFilePath)

        theTimingFilePath = os.path.join(theTimingDir,theBaseName+"-timing.csv")
        theTimingFilePath = pathExists(theTimingFilePath)
        insertTimings(theAlignmentFilePath, theTimingFilePath)

    print("Done")

