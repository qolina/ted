
import os
import time
import sys
from nltk.corpus import wordnet as wn
from itertools import islice

#targetSyn = 'event.n.01'
#targetSyn = 'person.n.01'
#targetSyn = 'organization.n.01'
targetSyn = 'physical_entity.n.01'
personSyn = 'person.n.01'

def isUnderTarget(syn, Target):
    for path in syn.hypernym_paths():
        nodes = [synset.name for synset in path]
        if Target in nodes:
            #print nodes
            return True
    return False
    
# get all nouns under Event synset
def getDict():
    # synset number
    synList = [syn.name for syn in islice(wn.all_synsets('n'), 1000000) if isUnderTarget(syn, targetSyn) and not isUnderTarget(syn, personSyn)] 
    #if not isUnderTarget(syn, evtSyn)]
    print len(synList)

    # lemmas 
    '''
    hash = dict([(lem.name,1) for syn in islice(wn.all_synsets('n'), 1000000) if isUnderTarget(syn, targetSyn) for lem in syn.lemmas])

    perhash = dict([(lem.name,1) for syn in islice(wn.all_synsets('n'), 1000000) if isUnderTarget(syn, personSyn) for lem in syn.lemmas])
    print len(hash)
    hash = dict([(lem, 1) for lem in hash if lem not in perhash])
    print len(hash)
    print '\n'.join(sorted(hash.keys()))
    '''
   

##################
#main
getDict()
