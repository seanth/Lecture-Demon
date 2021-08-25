import os, sys, glob

def pathExistsMake(thePath, makeBool=False):
  ###does the folder containing audio files exist?
    theFeedback="     Path '%s' found:    %s"
    if os.path.exists(thePath)==False:
        print(theFeedback % (thePath, "FALSE"))
        if makeBool==False:
            print("       Exiting.")
            sys.exit()
        else:
            #is this a single directory, or is it nested?
            if(len(thePath.split(os.sep)))>1:
                #nested directories
                print("       Creating dirs '%s'" % (thePath))
                os.makedirs(thePath)
                return os.path.abspath(thePath)
            else:
                #Make the dir if it doesn't exist
                print("       Creating dir '%s'" % (thePath))
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

def fileTypeExists(theFolderName, theFileSuffix):
    ###are there actually mp3s in the folder?
    tempVar = os.path.join(theFolderName, "*."+theFileSuffix)
    theFeedback="     %s files found in input folder: %s"
    if len(glob.glob(tempVar))<1:
        print(theFeedback % (theFileSuffix, "FALSE"))
        return False
    else:
        print(theFeedback % (theFileSuffix, "TRUE"))
        return True

def isfile_or_dir(thePath):
    if os.path.isfile(thePath): return "isFile"
    if os.path.isdir(thePath): return "isDir"
    return "error"

