#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: lemmatizer.py

import os, sys, codecs, subprocess, re
sys.path.append('lemmatizer-filters')
from freeling import posFilters, agreementFilters, npConjunction

usage = 'usage: lemmatizer.py'

"""
This function was intended to remove extra spaces and stuff, but since we track group offsets and lengths now, this is not obligatory.
Though any post-processing could be added here
"""
def __NormalizeGroups(groups):
	for group in groups:
		group[0] = group[0].replace(u'« ', u'«').replace(u' »', u'»').replace(u' , ', u', ')
		group[1] = group[1].replace(u'« ', u'«').replace(u' »', u'»').replace(u' , ', u', ')

	#print ('\n'.join('%s\t%s\t%s\t%s' % (group[0], group[2], group[4], group[5]) for group in groups)).encode('utf-8')
	return groups

def __IsGroup(word1, word2):
	group = None
	for agr in agreementFilters:
		res = agreementFilters[agr](word1, word2)
		if res:
			group = res
			break

	return [word1[0] + ' ' + word2[0],
			word1[1] + ' ' + word2[1],
			group,# + word2[2][len(group):],
			str(float(word1[3]) * float(word2[3])),
			# With the last two fields we are able not to keep track of the original text with spaces and stuff
			word1[4],							# offset of the group
			(word2[4] + word2[5] - word1[4]) 	# length of the group
			] if group else None

def IsSaved(filename):
	#filenameNoDir = os.path.split(filename)[1]
	return os.path.isfile(filename + '.words')

def IsSavedGroups(filename):
	#filenameNoDir = os.path.split(filename)[1]
	return os.path.isfile(filename + '.groups')

def Save(filename, items):
	#filenameNoDir = os.path.split(filename)[1]

	outFile = codecs.open(filename, 'w', 'utf-8')
	for item in items:
		outFile.write('\t'.join(str(elem) if isinstance(elem, int) or isinstance(elem, float) else elem for elem in item) + '\n')

def Load(filename):
	#filenameNoDir = os.path.split(filename)[1]

	intValuesStartIndex = 4

	items = []
	inpFile = codecs.open(filename, encoding = 'utf-8')
	for line in (line_raw.strip('\r\n') for line_raw in inpFile):
		items.append([])
		for val in line.split('\t'):
			items[-1].append(val if len(items[-1]) < intValuesStartIndex else int(val))
		#items.append(line.split('\t'))

	return items

def GetConjunctions(inputGroups):
	"""
	Returns the input list of groups with found NP conjunctions
	"""
	groups = inputGroups[:]
	wasMerge = True
	while wasMerge:
		wasMerge = False
		for i in range(2, len(groups)):
			if i >= len(groups):
				continue
			if npConjunction(groups[i - 2], groups[i - 1], groups[i]):
				mainWordTags = groups[i - 2][2]
				conjGroup = [' '.join(item[0] for item in groups[i-2:i+1]),
							' '.join(item[1] for item in groups[i-2:i+1]),
							'NN%sP0%s%s00' % (mainWordTags[2], mainWordTags[5], mainWordTags[6]),
							str(float(groups[i - 2][3]) * float(groups[i - 1][3]) * float(groups[i][3])),
							groups[i - 2][4],
							groups[i][4] + groups[i][5] - groups[i - 2][4]]
				wasMerge = True
				groups.pop(i - 2)
				groups.pop(i - 2)
				groups.pop(i - 2)
				#print 'insert', conjGroup[0].encode('utf-8')
				groups.insert(i - 2, conjGroup)

	return __NormalizeGroups(groups)

def GetGroups(words, loadFrom = None):
	"""
	Returns the list of groups found in the list of words.
	Each item is a list:
	[wordform, lemma, tag, probability, offset, length]

	Probability of the group is just the product of probabilities of its elements.

	Offset and length allow us to be independent from spaces, line breaks and such stuff: we can always extract group content
	from the real text.

	For the list of possible groups see agreementFilters dictionary.
	"""

	# if loadFrom is not None and there is already saved data, we can just load it
	if loadFrom and IsSavedGroups(loadFrom):
		return Load(loadFrom + '.groups')

	groups = [word[:] + [len(word[0])] for word in words]
	wasMerge = True

	while wasMerge:
		wasMerge = False
		for i in range(1, len(groups)):
			group = __IsGroup(groups[i - 1], groups[i])
			if group:
				wasMerge = True
				groups.pop(i - 1)
				groups.pop(i - 1)
				groups.insert(i - 1, group)
				
				break

	groups = GetConjunctions(__NormalizeGroups(groups))

	# if loadFrom is not None, but we are here, then there is no saved data yet, hence we need to save it
	if loadFrom:
		Save(loadFrom + '.groups', groups)

	return groups

def lemmatizer(text, startOffset = 0, loadFrom = None):
	# if loadFrom is not None and there is already saved data, we can just load it
	if loadFrom and IsSaved(loadFrom):
		return Load(loadFrom + '.words'), len(text) + startOffset

	freeling = subprocess.Popen([u'analyzer_client', u'50005'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	tagged = freeling.communicate(text.encode('utf-8'))[0].decode('utf-8').strip().split('\n')

	taggedList = []
	offset = 0
	for word in tagged:
		if not word or word.strip().startswith('Fz'):
			continue
		taggedList.append(word.split(' '))
		wordform = taggedList[-1][0]
		if '_' in wordform and (taggedList[-1][2] == 'W' or taggedList[-1][2].startswith('Z')):
			m = re.search(wordform.replace('_', ' +'), text[offset:])
			if not m:
				sys.stderr.write('Words: %s, no underscore\n' % wordform.encode('utf-8'))
			else:
				wordform = m.group()
			#print wordform.encode('utf-8'), len(wordform)
		hypotheticOffset = text.find(wordform, offset)
		if hypotheticOffset == -1:
			sys.stderr.write('Offset is -1 in file %s\n' % loadFrom)
		else:
			offset = hypotheticOffset
		#print offset + 1, taggedList[-1][0].encode('utf-8')
		taggedList[-1].append(offset + startOffset)
	
	# if loadFrom is not None, but we are here, then there is no saved data yet, hence we need to save it
	if loadFrom:
		Save(loadFrom + '.words', taggedList)

	return taggedList, len(text) + startOffset
if(__name__ == '__main__'):
	if len(sys.argv) < 1:
		print (usage)
		sys.exit()