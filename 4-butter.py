import csv
import os
import random
import string
import sys

import pandas as pd

theSearchWord = "but"

#time in seconds the length should be to make fun of myself
thePause = 0.01

# Set the path to the CSV file
#csv_path = 'transcript.csv'
theAlignmentFile = 'intermediate/lecture_alignments/ESSP520-02butter.csv'

# Set the path to the folder containing the image files
theImageFolder = 'lecture-daemon_data/img_library/but'
theWordImages = os.listdir(theImageFolder)


print("          Opening alignment file: '%s'" % theAlignmentFile)

theAlignmentRead = pd.read_csv(theAlignmentFile, header=None, names=['index','word','start','stop','token','slide', 'meta'], dtype={'slide':'object', 'meta':'object'})
print(theAlignmentRead)
wordList = list(theAlignmentRead['word'])
#print(wordList)
theWordOccuranceList=[]
theSlide = ""
print(theAlignmentRead['slide'].index.isnull())
for i, theWord in enumerate(wordList):
    # if math.isnan(theAlignmentRead['slide'][i]==NaN:
    #     print("what")
    ###is there a previous slide?
    # if theAlignmentRead['slide'][i]!="" or theAlignmentRead['slide'][i].isnull():
    #     theSlide=theAlignmentRead['slide'][i]
    #     print(theSlide)
    if theWord == theSearchWord:
        theStartTime = theAlignmentRead['start'][i]
        theStopTime = theAlignmentRead['stop'][i]
        if theStartTime!="" and theStopTime != "":
            theStartTime = float(theStartTime)
            theStopTime = float(theStopTime)
            if theStopTime-theStartTime>=thePause:
                aRandomFile = random.choice(theWordImages)
                theNewEntry = {'start': theStartTime, 'stop': theStopTime, 'slide': aRandomFile}
                theWordOccuranceList.append(theNewEntry)

df=pd.DataFrame(theWordOccuranceList, columns=['start','stop','slide'])
#df.loc[len(df)] = theWordOccuranceList
print(df)


print("         Inserting best calculated '%s' starts..." % (theSearchWord) ) 
alignmentWithWord = pd.concat((theAlignmentRead, df))

print("         Sorting slides by start time...")
alignmentWithWord = alignmentWithWord.sort_values(by='start')

print("         Writing edited alignment file...")
#alignmentWithTiming.to_csv('test.csv', header=False)  
alignmentWithWord.to_csv("bla.csv", header=False, index=False)


# theColumnNames = ['index', 'word', 'start time', 'stop time', 'token', 'video meta', 'slide']
# # Open the CSV file and read the contents into a list of dictionaries
# with open(theCsvPath, 'r') as aCsvFile:
#     theCsvData = csv.DictReader(aCsvFile, fieldnames = theColumnNames)
#     theRows = [row for row in theCsvData]

# # Iterate through the list of lists
# for i, theRow in enumerate(theRows):
#     theWord = theRow['word']
#     theWord = theWord.rstrip(string.punctuation)
#     theWord = theWord.lower()
#     if theWord == "but":
#         if theRow['start time'] !="":
#             theStartTime = float(theRow['start time'])

#         #don't use the word end. use the start of the next word
#         #if theRows[i+1]['start time'] !="":
#         if theRow['stop time'] !="":
#             theEndTime = float(theRows[i+1]['start time'])

#         # print(start_time)
#         # print(end_time)

#         theWordDelta = theEndTime - theStartTime
#         #print(theWordDelta)

#         if theWordDelta>=theButPause:
#             aRandomFile = random.choice(theButtFiles)
#             print(aRandomFile)
#             theRows[i]['slide'] = "test"
# print(theRows)
#     # if start_time !="" and end_time!="": 
#     #     start_time =  start_time = float(row['start_time'])
#     #     end_time = end_time = float(row['end_time'])
        
#     #     # Check if the word is “but” and the time difference is greater than 0.3
#     #     if word == 'but' and (end_time - start_time) > 0.2:
#     #         
#     #         # Choose a random audio file from the list
#     #         random_file = random.choice(butt_files)

#     #         # Add the file path to the new column entry
#     #         row[6]="test"
#     #         rows[i].append(os.path.join(image_folder, random_file))

# # Write the modified list of lists back to the CSV file
# sys.exit()
# with open(csv_path, 'w', newline='') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     csv_writer.writerows(rows)