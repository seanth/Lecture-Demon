from natsort import natsorted #pip install pandas, https://pypi.org/project/natsort/3.3.0/
import pandas as pd #pip install pandas

import xml.etree.ElementTree as ET
from zipfile import ZipFile
import glob, os, csv, argparse, sys

pathToUtils = "lecture-daemon_data"
###append the path to basic data files
sys.path.append(pathToUtils)
import fileUtils


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
    parser.add_argument('--path', metavar='', dest='thePath', required=True, help='Path to the powerpoint file OR path to the timing csv' )
    parser.add_argument('--align', metavar='', dest='mergeTiming', default=True, required=False, help='insert slide timing to alignment csv?' )
    parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='intermediate/lecture_alignments', required=False, help='path to place alignments')
    
    args = parser.parse_args()

    #check and see whether destination folders exist
    theAlignmentDir = fileUtils.pathExistsMake(args.theAlignmentDir)

    #does the  file exit?
    theFilePath = fileUtils.pathExists(args.thePath)
    theBaseName = os.path.basename(theFilePath)
    theBaseName = os.path.splitext(theBaseName)[0]


    if args.mergeTiming == True:
        theBaseName = theBaseName.rstrip("-timing")
        print(theBaseName)
        #does the alignment file exist?
        theAlignmentFilePath = os.path.join(theAlignmentDir,theBaseName+".csv")
        theAlignmentFilePath = fileUtils.pathExists(theAlignmentFilePath)

        insertTimings(theAlignmentFilePath, theFilePath)

    print("Done")

