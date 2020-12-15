from natsort import natsorted #pip install pandas, https://pypi.org/project/natsort/3.3.0/

import xml.etree.ElementTree as ET

import os, sys, glob, random, datetime, textwrap, argparse, csv

from dateutil.relativedelta import relativedelta
from PIL import Image, ImageDraw, ImageFont 
from zipfile import ZipFile

pathToUtils = "lecture-daemon_data"
###append the path to basic data files
sys.path.append(pathToUtils)
import fileUtils

brandingImagePath = 'lecture-daemon_data/logo-white.png'

def anthropocene():
    now = datetime.datetime.utcnow()
    bombDay = datetime.datetime(1945,7,16,5,29,21,0)+datetime.timedelta(hours=6)
    theDiff = relativedelta(now, bombDay)
    formattedAnthropocene = "%02d-%02d-%02dT%02d:%02d:%02dZ" % (theDiff.years, theDiff.months, theDiff.days, theDiff.hours, theDiff.minutes, theDiff.seconds)
    #print(formattedAnthropocene)
    return formattedAnthropocene

def makeSlate(theSlide, theCourseName, theLectureName, theSlidePath):
    ###############################################################
    #resize slide so it's 43% size of original
    subImage = Image.open(theSlide)
    theWidth,theHeight = subImage.size
    theSubWidth=int(theWidth*0.43)
    theSubHeight=int(theHeight*0.43)
    subImage = subImage.resize((theSubWidth,theSubHeight))
    ###############################################################

    ###############################################################
    #resize brade so it's 25% size of original
    brandingImage = Image.open(brandingImagePath)
    theBrandWidth,theBrandHeight = brandingImage.size
    theBrandWidth=int(theBrandWidth*0.25)
    theBrandHeight=int(theBrandHeight*0.25)
    brandingImage = brandingImage.resize((theBrandWidth,theBrandHeight))
    ###############################################################

    newImg = Image.new('RGB', (theWidth,theHeight), color = 'black')
    #newImg = Image.new('RGB', (1080,810), color = 'black')
    #newImg = Image.new('RGB', (720,540), color = 'black')

    gutter=20
    newImg.paste(subImage,(gutter,gutter))
    #branding should be to the right, bottom.
    brandX=theWidth-theBrandWidth-gutter
    brandY=theHeight-theBrandHeight-gutter
    newImg.paste(brandingImage, (brandX, brandY), mask=brandingImage)

    ###############################################################
    #popcorn box
    popcornImg = Image.new('RGB', (int(theWidth/2), 50), color = 'white')
    popX = int(theWidth/2)
    popY = int(theHeight/2)
    newImg.paste(popcornImg, (popX, popY))
    ###############################################################

    fnt36 = ImageFont.truetype('/Library/Fonts/Arial.ttf', 36)
    fnt24 = ImageFont.truetype('/Library/Fonts/Arial.ttf', 24)
    fnt20 = ImageFont.truetype('/Library/Fonts/Arial.ttf', 20)
    d = ImageDraw.Draw(newImg)
    ###############################################################
    #Class name
    textX=int(theWidth/2)
    textY=gutter
    d.text((textX,textY), theCourseName, font=fnt36, fill=(255, 255, 255))

    ###############################################################
    #Lecture name
    theName="\""+theLectureName+"\""
    titleLines = textwrap.wrap(theName, width=30)
    textY=gutter+36+36
    for i in titleLines:
        d.text((textX,textY), i, font=fnt36, fill=(255, 255, 255))
        textY=textY+56

    ###############################################################
    #Popcorn
    popX=popX+gutter
    popY=popY+12
    d.text((popX,popY), "Popcorn:", font=fnt24, fill=(0, 0, 0))

    ###############################################################
    #bombday date next to branding at bottom
    bombday=anthropocene()
    textY=int(theHeight-gutter-20)
    d.text((textX+70,textY), bombday, font=fnt20, fill=(255, 255, 255))

    outputPath = os.path.join(theSlidePath, "Slide0.png")
    outputPath = os.path.abspath(outputPath)
    newImg.save(outputPath)

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

def extractPptxMedia(theFilePath, slideFolder): 
    theArchive = ZipFile(theFilePath, 'r')
    theFileList = theArchive.namelist()
    print("          Parsing file: '%s'" % os.path.basename(theFilePath)) 

    #first get the list of files in the pptx under
    #ppt/media/ and make sure they are sorted correctly
    #based on their name
    for aFile in theFileList:
        if aFile.startswith('ppt/media/media'):
            print("          Extracting file: '%s'" % aFile) 
            theArchive.extract(aFile, slideFolder)
    theArchive.close()


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
        #print(theDuration)
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





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--path', metavar='', dest='thePath', required=True, help='Path to the powerpoint file OR path to the timing csv' )
    
    parser.add_argument('--makeSlate', metavar='', dest='makeSlate', default=True, required=False, help='Make a slate image? (True)' )
    parser.add_argument('--course', metavar='', dest='theCourseName', default='', required=False, help='Name of the course for slate (blank)' )
    parser.add_argument('--lecture', metavar='', dest='theLectureName', default='', required=False, help='Name of the lecture for slate (file name)' )
    parser.add_argument('--slateQuery', metavar='', dest='querySlateOK', default=True, required=False, help='Ask the user whether the slate is OK before proceeding (True)')

    parser.add_argument('--timing', metavar='', dest='makeTiming', default=True, required=False, help='Read pptx and make timing csv? (True)' )
    #parser.add_argument('--align', metavar='', dest='mergeTiming', default=True, required=False, help='insert slide timing to alignment csv?' )

    parser.add_argument('--media', metavar='', dest='extractMedia', default=True, required=False, help='Extract media(videos) from pptx? (True)' )

    parser.add_argument('--slideDir', metavar='', dest='theSlideDir', default='output/lecture_slides', required=False, help='Path to the parent folder for slides')
    parser.add_argument('--timingDir', metavar='', dest='theTimingDir', default='output/lecture_timing', required=False, help='Path to place timings')
    #parser.add_argument('--alignmentDir', metavar='', dest='theAlignmentDir', default='output/lecture_alignments', required=False, help='Path to place alignments')

    args = parser.parse_args()

    print("\n\n")

    #check and see whether destination folders exist
    theSlideDir = fileUtils.pathExistsMake(args.theSlideDir)
    #theAlignmentDir = fileUtils.pathExistsMake(args.theAlignmentDir)
    theTimingDir = fileUtils.pathExistsMake(args.theTimingDir, True)

    #is the path real?
    thePath = fileUtils.pathExists(args.thePath)

    ###############################################################
    fileorDir = fileUtils.isfile_or_dir(thePath)
    if fileorDir == "isDir":
        if args.makeSlate == True:
            #check whether there is a slide folder matching the name of the pptx
            #it's not enought that the folder exists. There should be pngs in
            #there with the name format 'Slide#.png'
            wildcardSlidePath = os.path.join(thePath, "*.png")
            slideList = glob.glob(wildcardSlidePath)
            if len(slideList) == 0:
                print("     *************")
                print("     No images found. Make sure you have")
                print("     exported slides as png files from your slide deck.")
                print("     *************")
                sys.exit()
            else:
                print("     Path '%s' found:    %s" % (thePath, "TRUE"))
                print("     '*.png' confirmed in folder:    %s"  % ("TRUE"))
                if args.theLectureName == '':
                    print("     *** No lecture name provided. Will use file name")
                    args.theLectureName = fileName
                print("     Lecture name:     %s"  % (args.theLectureName))
                if args.theCourseName == '':
                    print("     *** No course name provided")
                else:
                    print("     Course name:     %s"  % (args.theCourseName))

                #######
                #Send data to info to the function to make the start slate
                slateQuery = ''
                while slateQuery != 'y':
                    theSlide = random.choice(slideList)
                    makeSlate(theSlide, args.theCourseName, args.theLectureName, thePath)
                    print("     Slate made")
                    if args.querySlateOK == True:
                        slateQuery = input("     Satisfied with the slate? [y/N]")
                    else:
                        break

    if fileorDir == "isFile":
        #check whether the file type is 'pptx'
        fileName, fileSuffix = os.path.splitext(thePath)
        fileName = os.path.split(fileName)[1]
        if fileSuffix == ".pptx":
            slideFolder = os.path.join(theSlideDir, fileName)
            #########################################################################
            ###Make slate
            if args.makeSlate == True:
                #check whether there is a slide folder matching the name of the pptx
                #it's not enought that the folder exists. There should be pngs in
                #there with the name format 'Slide#.png'
                wildcardSlidePath = os.path.join(slideFolder, "Slide*.png")
                slideList = glob.glob(wildcardSlidePath)
                if len(slideList) == 0:
                    print("     *************")
                    print("     No potential slide images found. Make sure you have")
                    print("     exported slides as png files from your slide deck.")
                    print("     *************")
                    sys.exit()
                else:
                    print("     Path '%s' found:    %s" % (slideFolder, "TRUE"))
                    print("     'Slide*.png' confirmed in folder:    %s"  % ("TRUE"))
                    if args.theLectureName == '':
                        print("     *** No lecture name provided. Will use file name")
                        args.theLectureName = fileName
                    print("     Lecture name:     %s"  % (args.theLectureName))
                    if args.theCourseName == '':
                        print("     *** No course name provided")
                    else:
                        print("     Course name:     %s"  % (args.theCourseName))

                    #######
                    #Send data to info to the function to make the start slate
                    slateQuery = ''
                    while slateQuery != 'y':
                        theSlide = random.choice(slideList)
                        makeSlate(theSlide, args.theCourseName, args.theLectureName, slideFolder)
                        print("     Slate made")
                        if args.querySlateOK == True:
                            slateQuery = input("     Satisfied with the slate? [y/N]")
                        else:
                            break
            #########################################################################
            ###Extract timing from xml in pptx
            if args.makeTiming == True:        
                xmlFileList = pptxSlideXML(thePath)
                #print(xmlFileList)

                #format is: [timing in seconds(float), slide image name(str)]
                timingList = slideTiming(thePath,xmlFileList)
                #print(timingList)
                
                saveTiming(timingList, theTimingDir, fileName)
            #########################################################################
            ###Extract videos from the pptx 
            if args.extractMedia == True:
                extractPptxMedia(thePath, slideFolder)



    print("Done")

    #if fileorDir == "isDir":

    ###############################################################