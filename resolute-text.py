#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: resolute-text.py input pronouns model

import os, sys, codecs
import lemmatizer, anaphoramllib

usage = 'usage: resolute-text.py input pronouns model'

if(__name__ == '__main__'):
	if len(sys.argv) < 4:
		print (usage)
		sys.exit()

	text = ''
	pronouns = anaphoramllib.LoadPronouns(sys.argv[2])
	inpFile = codecs.open(sys.argv[1], encoding = 'utf-8')
	for line in (line_raw for line_raw in inpFile):
		text += line
	
	words, curOffset = lemmatizer.lemmatizer(text)#, loadFrom = sys.argv[1])
	groups = lemmatizer.GetGroups(words)#, loadFrom = sys.argv[1])

	mlResolutor = anaphoramllib.AnaphoraResolutorML()
	mlResolutor.LoadPronouns(pronouns)
	mlResolutor.SetWindow(20, 0)
	mlResolutor.LoadModel(sys.argv[3], sys.argv[3] + '.labels')

	for group in groups:
		if group[1] in mlResolutor.pronounIndex:
			antecedent = mlResolutor.FindAntecedent(group, groups)
			if len(antecedent) == 0:
				print 'no results for group at offset %d' % group[-2]
			else:
				print group[0], ' ---> ', antecedent[0][1][0]
				#print antecedent