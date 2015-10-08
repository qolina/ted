
import sys
import time


def merge(nerFilename, posFilename, outputFilename):
    nerFile = file(nerFilename)
    posFile = file(posFilename)
    outputFile = file(outputFilename, "w")

    idx = 0
    while 1:
        nerTxt = nerFile.readline()[:-1]
        posTxt = posFile.readline()[:-1]
        if len(nerTxt) < 1:
            print "..End of " + nerFilename + ". #Line: " + str(idx)
            break

        nerArr = nerTxt.split(" ")
        words = [item.split("/")[0] for item in nerArr]
        posArr = posTxt.split(" ")
        posHash = dict([(item.split("/")[0], item.split("/")[1]) for item in posArr])

        nerposArr = [nerArr[i]+'/'+posHash[words[i]] for i in range(len(nerArr)) if words[i] in posHash]
        if len(nerposArr) < 1:
            print "....error: empty results in line " + str(idx)
            nerposArr = ["-"]
        outputFile.write(" ".join(nerposArr) + "\n")

        idx += 1
        if idx % 1000000 == 0:
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime())

    nerFile.close()
    posFile.close()
    outputFile.close()

if __name__ == "__main__":

    print "Program mergeNER+POS_old starts at " + str(time.asctime())

    if len(sys.argv) != 4:
        print "Usage: mergeNerPos.py nerfilename posfilename outputfilename"
        sys.exit()

    merge(sys.argv[1], sys.argv[2], sys.argv[3])

    print "Program mergeNer+Pos_old ends at " + str(time.asctime())
