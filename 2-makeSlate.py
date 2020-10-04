import os, sys, glob, random, datetime, textwrap, argparse

from dateutil.relativedelta import relativedelta
from PIL import Image, ImageDraw, ImageFont 

brandingImagePath = 'autodipop_data/logo-white.png'

theSlideDir = 'output/lecture_slides'

def anthropocene():
    now = datetime.datetime.utcnow()
    bombDay = datetime.datetime(1945,7,16,5,29,21,0)+datetime.timedelta(hours=6)
    theDiff = relativedelta(now, bombDay)
    formattedAnthropocene = "%02d-%02d-%02dT%02d:%02d:%02dZ" % (theDiff.years, theDiff.months, theDiff.days, theDiff.hours, theDiff.minutes, theDiff.seconds)
    #print(formattedAnthropocene)
    return formattedAnthropocene

def isfile_or_dir(thePath):
    if os.path.isfile(thePath): return "isFile"
    if os.path.isdir(thePath): return "isDir"
    return "error"

def pathExists(thePath):
  ###does the folder containing audio files exist?
    theFeedback="     Path '%s' found:    %s"
    if os.path.exists(thePath)==False:
        #print(theFeedback % (thePath, "FALSE"))
        sys.exit()
    else:
        #print(theFeedback % (thePath, "TRUE"))
        return os.path.abspath(thePath)






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--path', metavar='', dest='thePath', required=True, help='Path to the image file to use OR the folder containing images' )
    parser.add_argument('--course', metavar='', dest='className', required=True, help='Name of the course' )
    parser.add_argument('--lecture', metavar='', dest='theLectureName', default='', required=False, help='Lecture name' )
    args = parser.parse_args()

    brandingImagePath = os.path.abspath(brandingImagePath)
    #theLecturePath = os.path.join(theSlideDir, theLectureName)

    #is the path real?
    thePath = pathExists(args.thePath)

    ###############################################################
    fileorDir = isfile_or_dir(thePath)
    if fileorDir == "isDir":
        #pick a random slide
        wildcardSlidePath = os.path.join(thePath, "*.png")
        slideList = glob.glob(wildcardSlidePath)
        if len(slideList) == 0:
            print("No potential slide images found. Exiting.")
            sys.exit()
        theSlide = random.choice(slideList)
        theLecturePath = thePath
        if args.theLectureName == '':
            args.theLectureName = os.path.split(thePath)[1]
    if fileorDir == "isFile":
        #use provided slide
        if os.path.splitext(thePath)[1] == ".png":
            theSlide = thePath
            theLecturePath = os.path.split(thePath)[0]
            args.theLectureName = os.path.split(theLecturePath)[1]
        else:
            print("No png image provided. Exiting.")
            sys.exit()
    ###############################################################

    theSlide = os.path.abspath(theSlide) 
    

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
    d.text((textX,textY), args.className, font=fnt36, fill=(255, 255, 255))

    ###############################################################
    #Lecture name
    theName="\""+args.theLectureName+"\""
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




    outputPath = os.path.join(theLecturePath, "Slide0.png")
    outputPath = os.path.abspath(outputPath)
    newImg.save(outputPath)
    print("Slide made")
