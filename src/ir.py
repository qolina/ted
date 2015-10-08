
import sys
import time
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


def analyzeText(text):
    arr = text.lower().split(" ")
    words = [item.split("/")[0] for item in arr]
    tags = [item.split("/")[1] for item in arr]
    return words, tags


def retrieveForCluster(infilename, cId, cWords):
    print "..Retrieving docs for cluster: " + str(cId)
    print cWords[:10]
    docs = []
    inputFile = file(infilename)
    idx = 0
    while 1:
        text = inputFile.readline()[:-1]
        if not text:
            print "..End of " + infilename + ". #Line: " + str(idx)
            break
            
        [words, tags] = analyzeText(text)
        common = [w for w in words if w in cWords]
        if len(common) > 0:
            docs.append(text)

        idx += 1
        if idx % 1000000 == 0:
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime()) + " #docs: " + str(len(docs))

    print "..Cluster related #docs: " + str(len(docs))
    inputFile.close()
    return docs


def retrieveDocs(clusterfilename, infilename, outfilename):
    clusterHash = loadClusters(clusterfilename)
    docHash = {}
    for i in clusterHash:
        cWords = clusterHash[i]
        cWords = [w.split(":")[0] for w in cWords]
        docs = retrieveForCluster(infilename, i, cWords)
        docHash[i] = docs
    outputFile = file(outfilename, "w")
    cPickle.dump(docHash, outputFile)
    outputFile.close()


if __name__ == "__main__":

    print "Program retrieve(posTagged)DocsForClusters starts at " + str(time.asctime())

    if len(sys.argv) != 4:
        print "Usage: ir.py clusterfilename inputfilename outputfilename"
        sys.exit()
    #clusterHash = loadClusters(sys.argv[1])
    retrieveDocs(sys.argv[1], sys.argv[2], sys.argv[3])
    print "Program retrieveDocsForClusters ends at " + str(time.asctime())
