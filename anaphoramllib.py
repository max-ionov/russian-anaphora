#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: anaphoramllib.py

import os, sys, codecs, re
import cPickle
import lemmatizer

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn import tree, svm
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

classifiers = {
				'rf': RandomForestClassifier(n_estimators = 150, min_samples_split = 2, n_jobs = -1),
				'dt': tree.DecisionTreeClassifier(), 
				'svm': svm.SVC(),
				'part': ExtraTreesClassifier(n_estimators = 30, min_samples_split = 2, n_jobs = -1),
				'featureselection': Pipeline([
					('feature_selection', LinearSVC(penalty="l1", dual = False)),
					('classification', RandomForestClassifier())
					])
			}

def LoadPronouns(filename):
	pronouns = {}
	pronounIndex = {}
	inpFile = codecs.open(filename, encoding = 'utf-8')
	for line in (line_raw.strip('\r\n') for line_raw in inpFile):
		pronounType, pronounList = line.split('\t', 1)
		pronouns[pronounType] = [item for item in line.split('\t')]
		for item in pronouns[pronounType]:
			pronounIndex[item] = pronounType

	return pronouns

def GetClassNumber(name, labels):
	if not name in labels:
		labels[name] = len(labels)
	return labels[name]


def Intersects(offset1, offset2):
	return (offset1[0] <= offset2[0] and not (offset1[0] + offset1[1]) < (offset2[0])) or \
			(offset2[0] <= offset1[0] and not (offset2[0] + offset2[1]) < (offset1[0]))


class AnaphoraResolutorML:
	def __init__(self):
		self.classifier = None
		self.anaphWnd = 20
		self.cataphWnd = 0
		self.labels = {}

	def LoadModel(self, model, labels):
		with open(model, 'rb') as inpFile:
			self.classifier = cPickle.load(inpFile)

		with open(labels, 'rb') as inpFile:
			self.labels = cPickle.load(inpFile)

	def LoadPronouns(self, pronouns):
		self.pronouns = pronouns
		self.pronounIndex = {}
		for pronounType in pronouns:
			for pronoun in pronouns[pronounType]:
				self.pronounIndex[pronoun] = pronounType

	def SetWindow(self, anaphWnd, cataphWnd):
		self.anaphWnd = anaphWnd
		self.cataphWnd = cataphWnd

	def FindAntecedent(self, targetGroup, groups):
		threshold = 0.3

		if not self.classifier:
			return None

		if not targetGroup[1] in self.pronounIndex:
			return None

		candidates = self.GetCandidates(groups, targetGroup)
		features = []
		for candidate in candidates:
			features.append(self.GetFeaturesVector(groups, nCandidate = candidate[0], nPronoun = groups.index(targetGroup)))
		results = self.classifier.predict_proba(features)
		resultsSimple = self.classifier.predict(features)

		# MAGIIIC. Returning three most probable candidates
		return sorted((candidates[i] + (results[i][1],) for i in range(len(results)) if results[i][1] >= threshold), key = lambda x: x[-1], reverse = True)[:3]

	def Resolute(self, groups):
		for group in groups:
			if group[1] in pronounIndex:
				results = self.FindAntecedent(group, groups)
				print results


	def TrainModel(self, features, target, classifier = 'rf'):
		if not classifier in classifiers:
			return False

		#print features, target

		self.classifier = classifiers[classifier]
		self.classifier.fit(features, target)

		return True

	def SaveModel(self, filename):
		if not self.classifier:
			return

		with open(filename, 'wb') as outFile:
			cPickle.dump(self.classifier, outFile)

		with open(filename + '.labels', 'wb') as outFile:
			cPickle.dump(self.labels, outFile)

	def GetCandidates(self, words, group):
		candidates = []
		prnIndex = words.index(group)
		if prnIndex == -1:
			prnIndex = len(words) - 1
		for i in range(prnIndex - self.anaphWnd, prnIndex + self.cataphWnd):
			if 0 <= i < len(words):
				if i == prnIndex:
					continue
				if lemmatizer.posFilters['noun'](words[i]) or lemmatizer.posFilters['pronoun'](words[i]):
					candidates.append((i, words[i] + [i - prnIndex]))

		return candidates

	def GetFeaturesVector(self, groups, nCandidate, nPronoun):
		indexFrom = groups[nCandidate][4]
		length = groups[nCandidate][5]
		indexTo = indexFrom + length

		pronounIndexFrom = groups[nPronoun][4]
		pronounLength = groups[nPronoun][5]
		pronounIndexTo = pronounIndexFrom + pronounLength

		nSymbols = length
		nWords = len(groups[nCandidate][0].split(' '))

		distInSymbols = pronounIndexFrom - indexTo if nPronoun > nCandidate else -(indexFrom - pronounIndexTo)
		distInGroups = nPronoun - nCandidate
		distInWords = sum(len(group[0].split(' ')) for group in groups[min(nPronoun, nCandidate):max(nPronoun, nCandidate)])
		#len(text[indexTo:pronounIndexFrom].split(' ')) if nPronoun > nCandidate else -len(text[pronounIndexTo:indexFrom].split(' '))

		numberCandidate = groups[nCandidate][2][3]
		numberPronoun = groups[nPronoun][2][2]

		caseCandidate = groups[nCandidate][2][2]
		casePronoun = groups[nPronoun][2][1]
		agrNumber = numberCandidate == numberPronoun
		agrCase = caseCandidate == casePronoun

		isName = groups[nCandidate][2][6] != '0'
		isAnimate = groups[nCandidate][2][5] == 'A'

		nGroupsLikeThis = len([item for item in groups if item[1] == groups[nCandidate][1]])
		#print nGroupsLikeThis, groups[nCandidate][0]

		pronounType = self.pronounIndex[groups[nPronoun][1]] if groups[nPronoun][1] in self.pronounIndex else 'UNK'
		pronounText = groups[nPronoun][0]

		# nSymbols — length of antecedent candidate in symbols
		# nWords — length of antecedent candidate in words (groups)
		# distInGroups — distance in groups
		# distInSymbols — distance in symbols
		# distInWords — distance in words
		# numberCandidate — grammatical number of antecedent candidate
		# numberPronoun — grammatical number of a pronoun
		# BOOL agrNumber — do they agree by number
		# caseCandidate — grammatical case of antecedent candidate
		# casePronoun — grammatical case of a pronoun
		# agrCase — BOOL do they agree by case
		# isName
		# isAnimate
		# BOOL isName — is antecedent candidate a name
		# pronounType — type of a prnoun
		# pronoun — pronoun wordform
		# isRightAnswer — is this candidate a real antecedent for this pronoun
		return [nSymbols, 
				nWords, 
				distInGroups, 
				distInSymbols, 
				distInWords, 
				GetClassNumber(numberCandidate, self.labels), 
				GetClassNumber(numberPronoun, self.labels), 
				int(agrNumber), 
				GetClassNumber(caseCandidate, self.labels),
				GetClassNumber(casePronoun, self.labels), 
				int(agrCase), 
				int(isName), 
				#int(isAnimate),
				nGroupsLikeThis,
				GetClassNumber(pronounType, self.labels),
				GetClassNumber(pronounText, self.labels)]
		"""
		return (
					(
						(indexFrom, indexTo),
						(pronounIndexFrom, pronounIndexTo)
					), 
					(
						'\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%d\t%s\t%s\t%d\t%d\t%s\t%s\t%d' % 
						(
							inputFilename, indexFrom, length, pronounIndexFrom, pronounLength, nSymbols, nWords, distInGroups, distInSymbols, distInWords, numberCandidate, numberPronoun, int(agrNumber), caseCandidate, casePronoun, int(agrCase), int(isName), pronounType, pronounText, int(isRightAnswer) 
						)
					)
				)
		"""
