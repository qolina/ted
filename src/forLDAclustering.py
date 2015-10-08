
import sys
import time

'''
# format of LDA data
    [M]
    [document_1]
    [document_2]
    ...
    [document_M]

  in which the first line is the total number for documents [M]. Each line 
  after that is one document. [document_i] is the i^th document of the dataset 
  that consists of a list of Ni words/terms.

    [document_i] = [word_i1] [word_i2] ... [word_iNi]

  in which all [word_ij] (i=1..M, j=1..Ni) are text strings and they are 
  separated by the space character.
'''

def preprocess(inputFilename, outputFilename):
    inputFile = file(inputFilename)
    outputFile = file(outputFilename, "w")

    textArr = inputFile.readlines()
    lineNum = len(textArr)

    outputFile.write(str(lineNum) + "\n")
    for text in textArr:
        text = text.lower()
        outputFile.write(text)

    inputFile.close()
    outputFile.close()


if __name__ == "__main__":

    print "Program prepareForLDAclustering starts at " + str(time.asctime())

    if len(sys.argv) != 3:
        print "Usage: forLDAclustering.py inputfilename outputfilename"
        sys.exit()

    preprocess(sys.argv[1], sys.argv[2])

    print "Program prepareForLDAclustering ends at " + str(time.asctime())
