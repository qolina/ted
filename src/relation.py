
import sys
import time
import re
import cPickle
from copy import deepcopy


def loadClusters(filename):
    inputFile = file(filename)
    content = inputFile.readlines()
    content = [line[:-1] for line in content]
    clusterHash = {}
    cId = 0
    words = []
    for line in content[1:]:
        if line.startswith("Topic "):
            clusterHash[cId] = deepcopy(words)
            cId = int(line.split(" ")[1][:-3])
            del words[:]
        else:
            words.append(line.strip().split(" ")[0])

    clusterHash[cId] = deepcopy(words)
    print "..Clusters in " + filename + " have been loaded into dict. #Item: " + str(len(clusterHash))
    inputFile.close()
    return clusterHash 


def getTagIdx(tagname, tagArr, idxArr):
    ridx = idxArr[0]+1
    while ridx < idxArr[1]:
        if not tagArr[ridx].startswith(tagname):
            ridx += 1
            continue
        return ridx
    return -1


def getTagWord(tagname, tagArr, words, idxArr):
    arg1 = ""
    idx = getTagIdx(tagname, tagArr, idxArr)
    if idx != -1:
        arg1 = getWord(words, idx, idx)
    return arg1


def getWord(words, st, ed):
    if st == -1:
        return ""
    wordArr = normMen(words[st:ed+1])
    return "_".join(wordArr)


# replace mention with @usr
def normMen(relArr):
    relArrUSR = []
    for wd in relArr:
        if wd.find("#") >= 0:
            continue
        if len(wd) <= 0:
            continue
        if wd[0] == "@":
            #wd = "@usr" # op1
            continue # op2
        wd = re.sub(r"\|", "", wd) # | is used as separator later for frame
        relArrUSR.append(wd)
    return relArrUSR


def analyzeText(text):
    arr = text.lower().split(" ")
    words = [item.split("/")[0] for item in arr]
    tags = [item.split("/")[1] for item in arr]
    return words, tags


def analyzeRel(text, cWords):
    [words, tags] = analyzeText(text)
    #print "***********************************"
    #print text
    verbIdxes = [i for i in range(len(tags)) if words[i] in cWords]
    verbIdxes.insert(0, 0)
    verbIdxes.append(len(words))
    relArr = []
    for i in range(1, len(verbIdxes)-1):
        idx = verbIdxes[i]
        sub = getTagWord("nn", tags, words, verbIdxes[i-1:i+1])
        obj = getTagWord("nn", tags, words, verbIdxes[i:i+2])
        pin = getTagWord("in", tags, words, verbIdxes[i-1:i+2])
        if len(sub) > 0:
            relArr.append(words[idx]+":s:"+sub)
            #relArr.append(words[idx]+":s")
        if len(obj) > 0:
            relArr.append(words[idx]+":o:"+obj)
            #relArr.append(words[idx]+":o")
        if len(pin) > 0:
            relArr.append(words[idx]+":p:"+pin)
            #relArr.append(words[idx]+":p_in")
        if len(sub+obj+pin) == 0:
            relArr.append(words[idx])
        #print relArr
    return relArr


def getRelation(docs, cWords):
    print "..Extracting relations from docs for cluster. #words: " + str(len(cWords))
    relDocs = []
    idx = 0
    for text in docs:
        relArr = analyzeRel(text, cWords)
        #print relArr
        relDocs.append(" ".join(relArr))
            
        idx += 1
        if idx % 100000 == 0:
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime()) + " #docs: " + str(len(relDocs))
    print ".. relDocs are obtained at " + str(time.asctime()) + " #docs: " + str(len(relDocs))
    return relDocs


def relationEx(clusterfilename, docfilename, outfilename):
    clusterHash = loadClusters(clusterfilename)
    docFile = file(docfilename)
    docHash = cPickle.load(docFile)
    relDocHash = {}
    for i in clusterHash:
        cWords = clusterHash[i]
        cWords = [w.split(":")[0] for w in cWords]
        docs = docHash[i]
        relDocs = getRelation(docs, cWords)
        relDocHash[i] = relDocs

    docFile.close()

    outputFile = file(outfilename, "w")
    cPickle.dump(relDocHash, outputFile)
    outputFile.close()


if __name__ == "__main__":

    print "Program getRelationOfWordsInClusters starts at " + str(time.asctime())

    if len(sys.argv) != 4:
        print "Usage: ir.py clusterfilename docfilename outputfilename"
        sys.exit()
    relationEx(sys.argv[1], sys.argv[2], sys.argv[3])
    print "Program getRelationOfWordsInClusters ends at " + str(time.asctime())
