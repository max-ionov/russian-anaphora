#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: lemmatize-text.py input config

import os, sys, codecs, lemmatizer

usage = 'usage: lemmatize-text.py input config'

if(__name__ == '__main__'):
	if len(sys.argv) < 3:
		print (usage)
		sys.exit()

	curOffset = 0
	text = ''
	inpFile = codecs.open(sys.argv[1], encoding = 'utf-8') if not sys.argv[1] == '-' else sys.stdin
	for line in (line_raw for line_raw in inpFile):
		if sys.argv[1] == '-':
			line = line.decode('utf-8')
		text += line
	
	words, curOffset = lemmatizer.lemmatizer(text, startOffset = curOffset)#, loadFrom = sys.argv[1])
	groups = lemmatizer.GetGroups(words)#, loadFrom = sys.argv[1])

	for group in groups:
		print group[0].encode('utf-8'), group[2], group[-2], group[-1]