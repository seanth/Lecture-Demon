#!/usr/bin/python

import argparse, glob, os, math, time, sys, json, datetime

################################################################
#The httplib module has been renamed to http.client in Python 3.
#import httplib
import http.client
from dateutil.relativedelta import relativedelta #python3 -m pip install python-dateutil

import httplib2 #python3 -m pip install httplib2
import os
import random
import time

from oauth2client.file import Storage # python3 -m pip install oauth2client
from oauth2client import client 
from oauth2client import tools 
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow

import google.oauth2.credentials #python3 -m pip install google-auth-oauthlib
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build #python3 -m pip install google-api-python-client
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'lecture-daemon_data/filled_client_secrets.json'

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

broadcastIDFileName = 'lecture-daemon_data/broadcast_id_archive.csv'
################################################################

def saveVideoID(theID,theVideoFileName):
    # # save the broadcast id to file
    with open(broadcastIDFileName, "a") as theFile:
        theFile.write("%s,%s\n"%(theID,theVideoFileName))
    print("          Broadcast id saved to file")

def relativeSinceTrinity():
    now = datetime.datetime.utcnow()
    bombDay = datetime.datetime(1945,7,16,5,29,21,0)+datetime.timedelta(hours=6)
    theDiff = relativedelta(now, bombDay)
    formattedAnthropocene = "%02d-%02d-%02dT%02d:%02d:%02dZ" % (theDiff.years, theDiff.months, theDiff.days, theDiff.hours, theDiff.minutes, theDiff.seconds)
    #print(formattedAnthropocene)
    return formattedAnthropocene

def pathExists(thePath):
  ###does the folder containing audio files exist?
    theFeedback="     Path '%s' found:    %s"
    if os.path.exists(thePath)==False:
        print(theFeedback % (thePath, "FALSE"))
        #Make the dir if it doesn't exist
        print("     Creating dir '%s'" % (thePath))
        os.mkdir(thePath)
        #sys.exit()
    else:
        print(theFeedback % (thePath, "TRUE"))
        return os.path.abspath(thePath)

def fileTypeExists(theFolderName, theFileSuffix):
    ###are there actually mp3s in the folder?
    tempVar = os.path.join(theFolderName, "*."+theFileSuffix)
    theFeedback="     %s files found in input folder: %s"
    if len(glob.glob(tempVar))<1:
        print(theFeedback % (theFileSuffix, "FALSE"))
        #sys.exit()
    else:
        print(theFeedback % (theFileSuffix, "TRUE"))

def booleanCheck(theVariable):
    #assume theVariable is a string
    if theVariable.lower()=="true":
        return True
    else:   
        return False




# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=SCOPES, message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("lecture-daemon_data/%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options, theVideoFileName):
  tags = None
  if options.keywords:
    tags = options.keywords.split(',')

  body=dict(
    snippet=dict(
        title=options.title,
        description=options.description,
        tags=tags,
        categoryId=options.category
    ),
    status=dict(
        privacyStatus=options.privacy_status
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=','.join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting 'chunksize' equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  # print(dir(insert_request))
  # print(insert_request.body)
  # print(insert_request.body_size)
  # print(insert_request.execute)
  # print(insert_request.headers)
  # print(dir(insert_request.http))
  # print(insert_request.method)
  # print(insert_request.uri)
  # sys.exit()
  resumable_upload(insert_request, theVideoFileName)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request, theVideoFileName):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
        print('     Uploading file...')
        status, response = request.next_chunk()
        if response is not None:
            if 'id' in response:
                print('          Video id "%s" was successfully uploaded.' % response['id'])
                saveVideoID(response['id'],theVideoFileName)
            else:
                exit('          The upload failed with an unexpected response: %s' % response)
    #except HttpError, e:
    except HttpError as e:
        if e.resp.status in RETRIABLE_STATUS_CODES:
            error = '          A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
        else:
            print(e)
            raise
    #except RETRIABLE_EXCEPTIONS, e:
    except RETRIABLE_EXCEPTIONS as e:
        error = '          A retriable error occurred: %s' % e

    if error is not None:
        print(error)
        retry += 1
        if retry > MAX_RETRIES:
            exit('          No longer attempting to retry.')

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print('          Sleeping %f seconds and then retrying...' % sleep_seconds)
        time.sleep(sleep_seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Who wants some popcorn?')
    parser.add_argument('--audio', metavar='', dest='boostAudio', default=False, required=False, help='boost the audio?' )
    parser.add_argument('--video', metavar='', dest='makeVideo', default=True, required=False, help='make a simple video with the provided||boosted audio?' )
    parser.add_argument('--upload', metavar='', dest='uploadVideo', default=True, required=False, help='upload simple video?' )
    parser.add_argument('--audioIn', metavar='', dest='theAudioDirIn', default='input/raw_audio', required=False, help='path to folder containing mp3s' )
    parser.add_argument('--audioOut', metavar='', dest='theAudioDirOut', default='intermediate/processed_audio', required=False, help='path to folder containing mp3s')
    parser.add_argument('--image', metavar='', dest='theImagePath', default='lecture-daemon_data/testPattern.png', required=False, help='path to still image to use for video')
    parser.add_argument('--videoOut', metavar='', dest='theRawVideoDir', default='intermediate/temp_video', required=False, help='path to the folder videos will be written to')
    parser.add_argument('--category', default='27', help='Numeric video category. ' + 'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    parser.add_argument('--keywords', help='Video keywords, comma separated', default='')
    parser.add_argument('--privacy-status', metavar='', dest='privacy_status', default='unlisted', required=False, help='options are: public, private, unlisted' )
    args = parser.parse_args()

    ###################################
    #needed for the youtube api stuff
    args.logging_level = 'ERROR'
    args.noauth_local_webserver = False
    args.auth_host_port = [8080, 8090]
    args.auth_host_name = 'localhost'
    ###################################

    args.description = """        *****
        Cottleston Cottleston Cottleston Pie,
        A fly can't bird, but a bird can fly.
        Ask me a riddle and I reply
        Cottleston Cottleston Cottleston Pie.
        *****"""
    
    ###########################################################################
    #do some checks to see whether files and folders needed actually exist
    aTest = pathExists(args.theAudioDirIn)
    if aTest:
        args.theAudioDirIn = aTest

    aTest = pathExists("intermediate")

    aTest = pathExists(args.theAudioDirOut)
    if aTest:
        args.theAudioDirOut = aTest

    aTest = pathExists(args.theImagePath)
    if aTest:
        args.theImagePath = aTest

    aTest = pathExists(args.theRawVideoDir)
    if aTest:
        args.theRawVideoDir = aTest

    #check and see if boolean things are boolean
    if isinstance(args.boostAudio, str):
        args.boostAudio = booleanCheck(args.boostAudio)
    if isinstance(args.makeVideo, str):
        args.makeVideo = booleanCheck(args.makeVideo)
    if isinstance(args.uploadVideo, str):
        args.uploadVideo = booleanCheck(args.uploadVideo)

    if(args.boostAudio==True):
        fileTypeExists(args.theAudioDirIn, "mp3")
        tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            
            theAudioOutPath = os.path.join(args.theAudioDirOut,theAudioFileName+".mp3")
            print("\n     Audio file '%s' found" % theFileName)
            print("       Sending file to ffmpeg to process audio.....")
            theCommand = "ffmpeg -i '%s' -ac 1 -filter:a loudnorm -b:a 128k '%s' >/dev/null" % (theFileName, theAudioOutPath)
            #print(theCommand)
            os.system(theCommand)
    else:
        tempVar = os.path.join(args.theAudioDirIn, "*.mp3")
        print(tempVar)
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            theAudioOutPath = os.path.join(args.theAudioDirOut,theAudioFileName+".mp3")
            print("\n     Audio file '%s' found" % theFileName)
            print("       Copying file to correct processing folder.....")
            theCommand = "cp '%s' '%s'" % (theFileName, theAudioOutPath)
            os.system(theCommand)

    if(args.makeVideo==True):
        fileTypeExists(args.theAudioDirIn, "mp3")
        tempVar = os.path.join(args.theAudioDirOut, "*.mp3")
        for theFileName in glob.glob(tempVar):
            theAudioFileName = os.path.basename(theFileName)
            theAudioFileName = os.path.splitext(theAudioFileName)[0]
            
            videoOutputPath = os.path.join(args.theRawVideoDir, theAudioFileName+".mp4")
            print("\n     Boosted audio file '%s' found" % theFileName)
            print("       Sending file to ffmpeg to generate video.....")    
            theCommand="ffmpeg -loop 1 -i '%s' -i '%s' -c:a copy -shortest '%s' >/dev/null" % (args.theImagePath, theFileName, videoOutputPath)
            #print(theCommand)
            os.system(theCommand)

    if(args.uploadVideo==True):
        #authenticate that the user is all set on youtube
        youtube = get_authenticated_service(args)
        print("     YouTube authentication passed:   TRUE")

        #just blank the archive file
        open(broadcastIDFileName, 'w').close()

        fileTypeExists(args.theRawVideoDir, "mp4")
        tempVar = os.path.join(args.theRawVideoDir, "*.mp4")
        i = 0
        for theFileName in glob.glob(tempVar):
            i = i+1
            theVideoFileName = os.path.basename(theFileName)
            theVideoFileName = os.path.splitext(theVideoFileName)[0]

            theSuffix = relativeSinceTrinity()
            theUploadTitle = "%s ~ %s" % (theVideoFileName, theSuffix)

            args.title = theUploadTitle
            args.file = theFileName
            print("     Preparing file name %s" % theVideoFileName)


            try:
                initialize_upload(youtube, args, theVideoFileName)
            except HttpError as e:
                print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

            if i == 6:
                print("Pausing uploads for 24hrs because of quota limitations")
                time.sleep(86400)
                i = 0
