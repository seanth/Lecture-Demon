#!/usr/bin/python

import argparse, glob, os, sys

pathToUtils = "lecture-daemon_data"
###append the path to basic data files
sys.path.append(pathToUtils)
import fileUtils

def booleanCheck(theVariable):
    #assume theVariable is a string
    if theVariable.lower()=="true":
        return True
    else:   
        return False



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--boost', metavar='', dest='boostAudio', default=False, required=False, help='boost the audio? (False)' )
    parser.add_argument('--rmnoise', metavar='', dest='rmnoise', default=False, required=False, help='remove room noise using file (False)' )
    #parser.add_argument('--video', metavar='', dest='makeVideo', default=True, required=False, help='make a simple video with the provided||boosted audio? (True)' )
    #parser.add_argument('--upload', metavar='', dest='uploadVideo', default=True, required=False, help='upload simple video? (True)' )
    parser.add_argument('--audioIn', metavar='', dest='theAudioDirIn', default='input/raw_audio', required=False, help='path to folder containing mp3s' )
    
    parser.add_argument('--ambientIn', metavar='', dest='theAmbientDirIn', default='input/ambient', required=False, help='path to folder containing mp3s' )
    
    parser.add_argument('--ambientOut', metavar='', dest='theAmbientDirOut', default='intermediate/audio_profiles', required=False, help='path to folder containing mp3s' )
    parser.add_argument('--audioOut', metavar='', dest='theAudioDirOut', default='intermediate/processed_audio', required=False, help='path to folder containing mp3s of ambient room noise')
    #parser.add_argument('--image', metavar='', dest='theImagePath', default='lecture-daemon_data/testPattern.png', required=False, help='path to still image to use for video')
    #parser.add_argument('--videoOut', metavar='', dest='theRawVideoDir', default='intermediate/temp_video', required=False, help='path to the folder videos will be written to')
    #parser.add_argument('--category', default='27', help='Numeric video category. ' + 'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    #parser.add_argument('--keywords', help='Video keywords, comma separated', default='')
    #parser.add_argument('--privacy-status', metavar='', dest='privacy_status', default='unlisted', required=False, help='options are: public, private, unlisted' )
    args = parser.parse_args()

    # ###################################
    # #needed for the youtube api stuff
    # args.logging_level = 'ERROR'
    # args.noauth_local_webserver = False
    # args.auth_host_port = [8080, 8090]
    # args.auth_host_name = 'localhost'
    # ###################################

    # args.description = """        *****
    #     Cottleston Cottleston Cottleston Pie,
    #     A fly can't bird, but a bird can fly.
    #     Ask me a riddle and I reply
    #     Cottleston Cottleston Cottleston Pie.
    #     *****"""
    
    ###########################################################################
    #do some checks to see whether files and folders needed actually exist
    args.theAudioDirIn = fileUtils.pathExistsMake(args.theAudioDirIn, True)
    
    args.theAmbientDirIn = fileUtils.pathExistsMake(args.theAmbientDirIn, True)
    
    theProcessedRawAudioDir = os.path.join(args.theAudioDirIn,"processed")
    theProcessedRawAudioDir = fileUtils.pathExistsMake(theProcessedRawAudioDir, True)
    
    fileUtils.pathExistsMake("intermediate", True)
    
    args.theAudioDirOut = fileUtils.pathExistsMake(args.theAudioDirOut, True)
    args.theAmbientDirOut = fileUtils.pathExistsMake(args.theAmbientDirOut, True)
    # args.theRawVideoDir = fileUtils.pathExistsMake(args.theRawVideoDir, True)
    # theProcessedTempVideo = os.path.join(args.theRawVideoDir,"processed")
    # theProcessedTempVideo = fileUtils.pathExistsMake(theProcessedTempVideo, True)
    # args.theImagePath = fileUtils.pathExistsMake(args.theImagePath,False)
    ###########################################################################


    ###########################################################################
    #check and see if boolean things are boolean
    if isinstance(args.boostAudio, str):
        args.boostAudio = booleanCheck(args.boostAudio)
    # if isinstance(args.makeVideo, str):
    #     args.makeVideo = booleanCheck(args.makeVideo)
    # if isinstance(args.uploadVideo, str):
    #     args.uploadVideo = booleanCheck(args.uploadVideo)
    ###########################################################################

    if fileUtils.fileTypeExists(args.theAudioDirIn, "mp3") == False:
        print("       Exiting.")
        sys.exit()

    ###########################################################################
    # if args.rmnoise != False:
    #     print("lsdfhljksah")
    #     theAmbientIn = fileUtils.pathExists(args.rmnoise)
    # sys.exit()

    print(args.rmnoise)
    if(args.rmnoise!=False):
        tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            theAudioIn = os.path.join(args.theAudioDirIn,theAudioFileName+".mp3")
            theAudioOutPath = os.path.join(args.theAudioDirOut,theAudioFileName+".mp3")
            if args.rmnoise == True:
                theAmbientIn = os.path.join(args.theAmbientDirIn,theAudioFileName+"-amb.mp3")
                theAmbientIn = fileUtils.pathExists(theAmbientIn)
            elif args.rmnoise != False:
                theAmbientIn = fileUtils.pathExists(args.rmnoise)
                print(theAmbientIn)
            theAmbientOut = os.path.join(args.theAmbientDirOut,theAudioFileName+".prof")

            theCommand = "sox '%s' -n noiseprof '%s'" % (theAmbientIn, theAmbientOut)
            print("         Generating ambient audio profile...")
            os.system(theCommand)

            theCommand = "sox '%s' '%s' noisered '%s' 0.25" % (theAudioIn, theAudioOutPath, theAmbientOut) #0.01 works well for mono apparently
            print("         Making audio with reduced ambient noise...")
            os.system(theCommand)

    elif(args.boostAudio==True):
        tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            
            theAudioOutPath = os.path.join(args.theAudioDirOut,theAudioFileName+".mp3")
            print("\n     Audio file '%s' found" % theFileName)
            print("       Sending file to ffmpeg to process audio...")
            theCommand = "ffmpeg -i '%s' -ac 1 -filter:a loudnorm -b:a 128k '%s' >/dev/null" % (theFileName, theAudioOutPath)
            #print(theCommand)
            os.system(theCommand)
    else:
        tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            theAudioOutPath = os.path.join(args.theAudioDirOut,theAudioFileName+".mp3")
            print("\n     Audio file '%s' found" % theFileName)
            print("       Copying file to correct processing folder.....")
            theCommand = "cp '%s' '%s'" % (theFileName, theAudioOutPath)
            os.system(theCommand)

    tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
    for theFileName in glob.glob(tempVar):
        theAudioFileName = os.path.basename(theFileName)
        print("         Move raw audio file %s to processed folder..." % theAudioFileName)
        theAudioFileName = os.path.splitext(theAudioFileName)[0]
        
        theProcessedRawAudio = os.path.join(theProcessedRawAudioDir,theAudioFileName+".mp3")
        
        theCommand = "mv '%s' '%s'" % (theFileName, theProcessedRawAudio)
        os.system(theCommand)

    # if(args.makeVideo==True):
    #     #fileTypeExists(args.theAudioDirIn, "mp3")
    #     tempVar = os.path.join(args.theAudioDirOut, "*.mp3")
    #     for theFileName in glob.glob(tempVar):
    #         theAudioFileName = os.path.basename(theFileName)
    #         theAudioFileName = os.path.splitext(theAudioFileName)[0]
            
    #         videoOutputPath = os.path.join(args.theRawVideoDir, theAudioFileName+".mp4")
    #         print("\n     Boosted audio file '%s' found" % theFileName)
    #         print("       Sending file to ffmpeg to generate video.....")    
    #         theCommand="ffmpeg -loop 1 -i '%s' -i '%s' -pix_fmt yuv420p -c:a copy -shortest '%s' >/dev/null" % (args.theImagePath, theFileName, videoOutputPath)
    #         #print(theCommand)
    #         os.system(theCommand)

    # if(args.uploadVideo==True):
    #     #authenticate that the user is all set on youtube
    #     youtube = get_authenticated_service(args)
    #     print("     YouTube authentication passed:   TRUE")

    #     #just blank the archive file
    #     open(broadcastIDFileName, 'w').close()

    #     fileUtils.fileTypeExists(args.theRawVideoDir, "mp4")
    #     tempVar = os.path.join(args.theRawVideoDir, "*.mp4")
    #     i = 0
    #     for theFileName in glob.glob(tempVar):
    #         i = i+1
    #         theVideoFileName = os.path.basename(theFileName)
    #         theVideoFileName = os.path.splitext(theVideoFileName)[0]

    #         theSuffix = relativeSinceTrinity()
    #         theUploadTitle = "%s ~ %s" % (theVideoFileName, theSuffix)

    #         args.title = theUploadTitle
    #         args.file = theFileName
    #         print("     Preparing file name %s" % theVideoFileName)


    #         try:
    #             initialize_upload(youtube, args, theVideoFileName)
    #             print("         Clean up of temp file...")
    #             theVideoFileName = os.path.basename(theFileName)
    #             theVideoFileName = os.path.splitext(theAudioFileName)[0]
    #             theProcessedTmpVideo = os.path.join(args.theRawVideoDir,theVideoFileName+".mp4")
    #             theCommand = "mv %s %s" % (theFileName, theProcessedTmpVideo)
    #             print(theCommand)
    #             os.system(theCommand)
    #         except HttpError as e:
    #             print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

    #         if i == 6:
    #             print("Pausing uploads for 24hrs because of quota limitations")
    #             time.sleep(86400)
    #             i = 0
