#!/usr/bin/python
# coding: utf-8
import lxml, sys,os
import numpy
from lxml import etree

argument = sys.argv[1]

def ReadValues(filename, document = None):
    tree = etree.parse(filename)
    path = ('//document[@file="%s"]/chain' % document) if document else '//document/chain'
    #print path, filename

    chains = []
    for chain in tree.xpath(path):
	chains.append([])
	for item in list(chain):
	    chains[-1].append((int(item.get('sh')), int(item.get('sh'))+int(item.get('ln')), list(item)[0].text))
    #print chains
    return chains

files = os.listdir('AnaphFiles/all/')
files = [f for f in files if f.endswith('.txt')]
precision_values = []
recall_values = []

for f in files:
    #print f
    gsfile = 'all/'+f
    testing = ReadValues(argument+'.xml',gsfile)
    golden = ReadValues('anaph_all.xml',gsfile)
    if len(golden) == 0 and len(testing) == 0:
	continue
    if len(golden) == 0 and len(testing) != 0:
	precision_values.append(0)
	continue
    if len(golden) != 0 and len(testing) == 0:
	recall_values.append(0)
	continue

    good_chains = 0
    for chain in testing:
	#print word[1]
	for goldenchain in golden:
	    if chain[1][0] >= goldenchain[1][0] and chain[1][1] <= goldenchain[1][1] or chain[1][0] <= goldenchain[1][0] and chain[1][1] >= goldenchain[1][1]:
		if chain[0][0] >= goldenchain[0][0] and chain[0][1] <= goldenchain[0][1] or chain[0][0] <= goldenchain[0][0] and chain[0][1] >= goldenchain[0][1]:
		    #print chain[0][2]+'<---'+chain[1][2]
		    #print 'Golden:',goldenchain[0][2]+'<---'+goldenchain[1][2]
		    good_chains += 1
		    break
    precision = float(good_chains)/len(testing)
    #print "Precision:", precision
    precision_values.append(precision)

    present_chains = 0
    for chain in golden:
	for testchain in testing:
	    if testchain[1][0] >= chain[1][0] and testchain[1][1] <= chain[1][1] or testchain[1][0] <= chain[1][0] and testchain[1][1] >= chain[1][1]:
		if testchain[0][0] >= chain[0][0] and testchain[0][1] <= chain[0][1] or testchain[0][0] <= chain[0][0] and testchain[0][1] >= chain[0][1]:
		    #print chain[0][2]+'<---'+chain[1][2]
		    #print 'Test:',testchain[0][2]+'<---'+testchain[1][2]
		    present_chains += 1
		    break
    recall = float(present_chains)/len(golden)
    #print "Recall:", recall
    recall_values.append(recall)

print "==========="

precision = numpy.mean(precision_values)
recall = numpy.mean(recall_values)

print 'Total Precision:', precision
print 'Total Recall:', recall
fmeasure = (2*precision*recall)/float(precision+recall)
print 'F-measure:', fmeasure