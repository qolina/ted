
import sys
import time
import cPickle
from copy import deepcopy

## definition of event pattern(pattern)
# 1) a verb
# 2) a noun in WordNet under Event Synset (in ../dict/EventNoun.dic)
# 3) a verb and the head word of its syntactic object.

def loadFileIntoDict(filename):
    inputFile = file(filename)
    content = inputFile.readlines()
    hash = dict([(line[:-1], 1) for line in content])
    print "..Content in " + filename + " have been loaded into dict. #Item: " + str(len(hash))
    inputFile.close()
    return hash


def analyzeText(text):
    arr = text.split(" ")
    words = [item.split("/")[0] for item in arr]
    neTags = [item.split("/")[1] for item in arr]
    tags = [item.split("/")[2] for item in arr]
    return words, tags, neTags

# extract event pattern from a string
def getPatternFromStr(text):
    [words, tags, neTags] = analyzeText(text)
    #cond1
    verbs = [i for i in range(len(tags)) if tags[i].startswith("VB")]
    #cond2
    evtNouns = [i for i in range(len(words)) if words[i] in EventNounHash]
    #cond3
    #syntactic obj? -> parsing?
    verbsCP = deepcopy(verbs)
    verbsCP.append(len(tags))
    objs = [(verbsCP[i],j) for i in range(len(verbsCP)-1) for j in range(verbsCP[i], verbsCP[i+1]) if tags[j].startswith("NN")]
    objs = [objs[i] for i in range(len(objs)) if (objs[i][0] != objs[i-1][0]) or (i==0)]
    neTypes = dict([(objs[i][0], objs[i][1]) for i in range(len(objs)) if neTags[objs[i][1]].startswith("B-")])


    verbs_noNE = [i for i in verbs if i not in neTypes]
    ptns = [words[i] for i in range(len(words)) if (i in verbs_noNE) or (i in evtNouns)]
    ptns_NE = [words[i]+":"+neTags[neTypes[i]] for i in neTypes]
    ptns.extend(ptns_NE)
    return " ".join(ptns)


# extract event pattern from a file
def getPatternFromFile(infilename, outfilename):
    inputFile = file(infilename)
    outputFile = file(outfilename, "w")
    keptLineHash = {}# only part of tweets contain event patterns (from 0)
    idx = 0
    while 1:
        text = inputFile.readline()[:-1]
        if len(text) < 1:
            print "..End of " + infilename + ". #Line: " + str(idx)
            break
        elif len(text) == 1: # In nerpos_old, some texts are empty and labelled as "-"
            idx += 1
            continue
            
        ptnStr = getPatternFromStr(text)
        #'''
        if len(ptnStr) > 1:
            #outputFile.write(str(idx) + "\t" + ptnStr + "\n")
            keptLineHash[idx] = 1
            outputFile.write(ptnStr + "\n")
        #'''

        # for comparison of pos and pos_old
        #outputFile.write(text + "\n")

        idx += 1
        if idx % 1000000 == 0:
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime())

    kptLnFile = file(outfilename+".kptln", "w")
    cPickle.dump(keptLineHash, kptLnFile)
    kptLnFile.close()
        
    inputFile.close()
    outputFile.close()

if __name__ == "__main__":

    print "Program EvtPtnExtraction starts at " + str(time.asctime())

    text_example = "see/O/VB you/O/PRP later/O/RB shitlords/O/NN !/O/. bye/O/UH 2012/O/UH. Saw/O/VBZ Baidu/B-company/NNP in/O/DT explosion/O/NN today/O/RB ./O/."

    evtNounFilePath = "../dict/EventNoun.dic" # load EventNoun for getPatternFromStr
    global EventNounHash
    EventNounHash = loadFileIntoDict(evtNounFilePath)

    '''
    # test analyzeText
    [words, tags, neTags] = analyzeText(text_example)
    print words
    print tags
    print neTags
    '''

    '''
    # test getPatternFromStr
    ptnStr = getPatternFromStr(text_example)
    '''

    # test getPatternFromFile
    if len(sys.argv) != 3:
        print "Usage: evtptn.py inputfilename outputfilename"
        sys.exit()
    getPatternFromFile(sys.argv[1], sys.argv[2])
    print "Program EvtPtnExtraction ends at " + str(time.asctime())
