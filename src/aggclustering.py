import sys
import time
import os
import cPickle
from numpy import *
import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as ssd


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

def getptns(inputFilename):
    global nodeHash, tfHash

    tfHash = {}
    nodeHash = {}

    inputFile = file(inputFilename)
    docNum = inputFile.readline()
    nId = 0
    while 1:
        line = inputFile.readline()[:-1]
        if len(line) < 1:
            break
        arr = line.split(" ")
        for word in arr:
            if word not in nodeHash:
                nodeHash[word] = nId
                nId += 1
        updateTF(arr)

    print "..Nodes are loaded from " + inputFilename + ". #node: " + str(len(nodeHash))
    #print sorted(nodeHash.items(), key = lambda a:a[1])
    inputFile.close()

    [newNodeHash, newTFHash] = ptnFiltering(nodeHash, tfHash, 4)
    nodeHash = newNodeHash
    tfHash = newTFHash

    '''
    # test for filtering patterns by TF
    print [len(tfHash), sum(tfHash.values()), min(tfHash.values()), max(tfHash.values())]
    for tf in range(1, 11):
        oHash = getsubHash(tfHash, tf)
        print ".. TF: " + str(tf) + " --> items: " + str(len(oHash))
    '''


def getsubHash(egHash, val):
    outHash = dict([(ptn, egHash[ptn]) for ptn in egHash if egHash[ptn] == val])
    return outHash


def ptnFiltering(nodeHash, tfHash, TFthreshold):
    newNodeHash = dict([(ptn, nodeHash[ptn]) for ptn in nodeHash if tfHash[nodeHash[ptn]] > TFthreshold])
    newTFHash = {}

    nId = 0
    for ptn in newNodeHash:
        oldId = newNodeHash[ptn]
        newNodeHash[ptn] = nId
        newTFHash[nId] = tfHash[oldId]
        nId += 1

    print "..After filtering by TF(" + str(TFthreshold) + ") New #node: " + str(len(newNodeHash))
    return newNodeHash, newTFHash


def getPairId(x, y):
    return str(min(x,y))+"-"+str(max(x,y))


def getNodeIds(str):
    [x, y] = [int(id) for id in str.split("-")]
    return [x, y]


def getNodeId(ptn):
    if ptn in nodeHash:
        return nodeHash[ptn]
    else:
        return -1


def updateGDis(arr1, arr2, value):
    #global gDis
    global cDis
    for i in range(len(arr1)):
        nID1 = getNodeId(arr1[i])
        if arr1 == arr2:
            start = i+1
        else:
            start = 0

        for j in range(start, len(arr2)):
            nID2 = getNodeId(arr2[j])
            if (nID1*nID2 == 1) or (nID1 == nID2):
                continue
            #gDis[min(nID1, nID2)][max(nID1, nID2)] = value
            #cDis[min(nID1, nID2)][max(nID1, nID2)] += toCval(value)
            pairId = getPairId(nID1, nID2)
            if pairId not in cDis:
                cDis[pairId] = toCval(value)
            else:
                cDis[pairId] += toCval(value)

def toCval(val):
    return 1 - math.log(val, 4)

def updateTF(arr):
    for word in arr:
        nID = nodeHash[word]
        if nID in tfHash:
            tfHash[nID] += 1
        else:
            tfHash[nID] = 1

def getSim(inputFilename):

    #gDis = zeros((len(nodeHash), len(nodeHash)))
    #print gDis
    global cDis
    cDis = {}#zeros((len(nodeHash), len(nodeHash)))
    #PMI = {}
    PMI = zeros((len(nodeHash), len(nodeHash)))

    lnIdFile = file(inputFilename+".kptln")
    kptlnHash = cPickle.load(lnIdFile)
    lnIdFile.close()
    kptlnList = sorted(kptlnHash.keys())

    inputFile = open(inputFilename)

    while 1:
        textArr = inputFile.readlines()
        if not textArr:
            print "..End of file " + str(time.asctime())
            break

        del textArr[0]
        textArr = [line[:-1] for line in textArr]

        for idx in range(len(textArr)):
            arr = textArr[idx].split(" ")

            # update cDis, gDis
            # get words located in same sentence
            updateGDis(arr, arr, 1)

            if idx > len(textArr)-3:
                continue
            for j in range(1, 3):
                idxNew = idx + j
                #print [idx, idxNew]
                # get words located in neighboring sentence
                if kptlnList[idx] == kptlnList[idxNew] - 1:
                    arrP1 = textArr[idxNew].split(" ")
                    updateGDis(arr, arrP1, 2)
                # get words located in 2-distance sentence
                if kptlnList[idx] == kptlnList[idxNew] - 2:
                    arrP2 = textArr[idxNew].split(" ")
                    updateGDis(arr, arrP2, 3)

    cSum = sum(cDis.values())
    tfSum = sum(tfHash.values())
    #print [cSum, tfSum, min(tfHash.values()), max(tfHash.values())]
    print "..Start to calculate PMI" + str(time.asctime())
    for i in range(len(nodeHash)):
        for j in range(i):
            pairId = getPairId(i, j)
            
            if pairId in cDis:
                pDis = cDis[pairId]*1.0/cSum
                pi = tfHash[i]*1.0/tfSum
                pj = tfHash[j]*1.0/tfSum
                '''
                if pi*pj < 0.00001:
                    print pairId, 
                    print [pi, pj]
                '''
                val = pDis/(pi*pj)
                '''
                if val > 0:
                    PMI[pairId] = val
                '''
                PMI[j][i] = val
                PMI[i][j] = val
        if i % 1000 == 0:
            print "....calculating node: " + str(i)

    inputFile.close()
    save('pmi.npy', PMI)
    print "..PMI has been saved into pmi.npy " + str(time.asctime())
    #print [len(PMI), min(PMI.values()), max(PMI.values())]
    return PMI

def clustering(PMI):

    '''
    1. Initially, put each article in its own cluster.
    2. Among all current clusters, pick the two clusters with the smallest distance.
    3. Replace these two clusters with a new cluster, formed by merging the two original ones.
    4. Repeat the above two steps until there is only one remaining cluster in the pool.
    '''
    print "..Start clustering with hierarchy agglomerative clustering " + str(time.asctime())
    
    '''
    zeroCount = 0
    for (x, y) in ndindex(PMI.shape):
        if PMI[x][y] == 0:
            zeroCount += 1
    print "....zeros in PMI: " + str(zeroCount)
    '''

    maxSim = ceil(amax(PMI)) # use this one would make little difference between distances
    #maxSim = 100
    distArr = subtract(maxSim, PMI) # maxSim - values

    idenSim = identity(len(nodeHash))
    idenSim = multiply(idenSim, maxSim)
    distArr = subtract(distArr, idenSim) # zero on the main diagonal

    #distArr = distArr[:1000, :1000]
    #print distArr
    distArr = ssd.squareform(distArr)
    print "..distArray has been calculated " + str(time.asctime())

    z = hac.linkage(distArr, method="average")
    #z = hac.linkage(PMI, method="average")
    save('z.npy', z)
    print z[z.size/4-1]
    print z
    print "..z has been saved into z.npy " + str(time.asctime())


def getClusters(z, MSize):
    print "..Start getting clusters from linkage results " + str(time.asctime())
    #cAssign = hac.fcluster(z, float(sys.argv[3]), criterion="inconsistent", depth=int(sys.argv[4]))
    #print cAssign

    nodeNum = z.size/4 + 1
    clusterHash = {}
    nodes = dict([(i, [i]) for i in range(nodeNum)])
    for i in range(z.size/4):
        if z[i][3] >= MSize:
            break

        nodeList1 = nodes[z[i][0]]
        nodeList2 = nodes[z[i][1]]
        nodeList1.extend(nodeList2)
        nodes[nodeNum+i] = nodeList1
        del nodes[z[i][0]]
        del nodes[z[i][1]]
    return nodes


def outputClusters(nodes, maxClusterNum, outputFilename):
    outputFile = file(outputFilename, "w")

    scaleHash = dict([(i, len(nodes[i])) for i in nodes])
    nodeContentHash = dict([(nodeHash[word], word) for word in nodeHash])
    print "..Output Clusters with #Clusters <= " + str(maxClusterNum) + " to " + outputFilename
    cId = 0
    for it in sorted(scaleHash.items(), key = lambda a:a[1], reverse = True):
        #print "....Cluster " + str(cId+1)
        #print " ".join([nodeContentHash[nId] for nId in nodes[it[0]]])
        outputFile.write("Topic " + str(cId) + "th:\n\t")
        outputFile.write("\n\t".join([nodeContentHash[nId] for nId in nodes[it[0]]])+"\n")
        cId += 1
        if cId >= maxClusterNum:
            break
    outputFile.close()
    

def clusteringPtn(inputFilename, outputFilename):
    getptns(inputFilename)

    if not os.path.exists("pmi.npy"):
        getSim(inputFilename)

    if not os.path.exists("z.npy"):
        PMI = load("pmi.npy")
        clustering(PMI)

    z = load("z.npy")    
    if "-msize" in sys.argv:
        MSize = int(sys.argv[sys.argv.find("-msize")])
    else:
        MSize = 40
    nodes = getClusters(z, MSize)
    
    if "-cnum" in sys.argv:
        maxClusterNum = int(sys.argv[sys.argv.find("-cnum")])
    else:
        maxClusterNum = 20
    outputClusters(nodes, maxClusterNum, outputFilename)


if __name__ == "__main__":

    print "Program agglomerative clustering starts at " + str(time.asctime())

    if len(sys.argv) < 3:
        print "Usage: aggclustering.py inputfilename outputfilename -msize msize(40 default) -cnum clusterNum(20 default)"
        sys.exit()

    clusteringPtn(sys.argv[1], sys.argv[2])

    print "Program agglomerative clustering ends at " + str(time.asctime())
