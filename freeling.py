#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: freeling.py

import os, sys, codecs, subprocess

usage = 'usage: freeling.py'

"""
This is the recommended way to check against part of speech. Add a lambda-function for the desired POS
and use it in your code in the following way: posFilters['desired_pos'](word), where word is a list
"""
posFilters = {
	'noun': lambda x: x[2].startswith('N') or x[2].startswith('PP'),
	'adj': lambda x: x[2].startswith('A') or x[2].startswith('R'),
	'properNoun': lambda x: x[2].startswith('NP'),
	'pronoun': lambda x: x[2].startswith('E'),
	'comma': lambda x: x[2] == 'Fc',
	'prep': lambda x: x[2] == 'B0',
	'insideQuote': lambda x: x[2] == 'Fra' or x[2].startswith('QuO'),
	'closeQuote': lambda x: x[2] == 'Frc',
	'firstName': lambda x: x[2].startswith('N') and x[2][6] == 'N',
	'secondName': lambda x: (x[2].startswith('N') and x[2][6] in ['F', 'S']) or (x[2].startswith('A') and x[2][5] in ['F', 'S']),
	#'conj': lambda x: x[2] == 'C0' or x[2] == 'Fc'
	'conj': lambda x: x[2] == 'C0',
	'quant': lambda x: x[2].startswith('Z')
}

"""
This is the list of groups which we are trying to extract. To disable any of the groups, just comment it
Preposition Phrases extraction is disabled in order to be closer to Gold Standard
"""
agreementFilters = {
	'adjNoun': lambda adj, noun: 'NN' + noun[2][2:] if (posFilters['adj'](adj) and posFilters['noun'](noun) and adj[2][2] == noun[2][3]) else None,
	#'prepNP': lambda prep, noun: 'PP' if (posFilters['prep'](prep) and posFilters['noun'](noun)) else None,
	#'insideQuote': lambda quote, word: 'QuO' if posFilters['insideQuote'](quote) else None,
	#'closeQuote': lambda quote, closeQuote: 'QuC' if posFilters['insideQuote'](quote) and posFilters['closeQuote'](closeQuote) else None,
	'name': lambda name, famName: 'NN' + name[2][2:] if posFilters['firstName'](name) and posFilters['secondName'](famName) else None,
	'quantNoun': lambda quant, noun: 'NN%sP0%s' % (noun[2][2] if quant[2][1] != 'N' else 'N', noun[2][5:]) if (posFilters['quant'](quant) and posFilters['noun'](noun) and (quant[2][1] == noun[2][2] or (quant[2][1] == 'N' and noun[2][2] == 'G'))) else None
}

npConjunction = lambda word1, conj, word2: 'NN' if (posFilters['noun'](word1) and posFilters['noun'](word2) and posFilters['conj'](conj)) else None
