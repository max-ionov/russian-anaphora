#!/usr/bin/python
#coding: utf-8
# An@phora resolution
import codecs,sys
from lemmatizer import lemmatizer
from lemmatizer import GetGroups
from lemmatizer import GetConjunctions

import anaphoramllib
pronouns = anaphoramllib.LoadPronouns('pronouns.config.txt')
mlResolutor = anaphoramllib.AnaphoraResolutorML()
mlResolutor.LoadPronouns(pronouns)
mlResolutor.SetWindow(20, 0)
mlResolutor.LoadModel('model.dat', 'labels.dat')


argument = sys.argv[1]
window = int(sys.argv[2])
pronouns = []
reflexives = []
demonstratives = []
relatives = []

currentOutput = 'xml'

def printxml(antecedent,anaphora):
    print "<chain>"
    (token,lemma,tagset,precision,offset,length,dist) = antecedent
    print '<item sh="%s" ln="%s" type="anaph">' % (offset,length)
    print '<cont><![CDATA[%s]]></cont>' % token.encode('utf-8')
    print "</item>"
    (token,offset,length,an_type,an_count) = anaphora
    print '<item sh="%s" ln="%s" comment="%s" type="anaph">' % (offset,length,an_type)
    print '<cont><![CDATA[%s]]></cont>' % token.encode('utf-8')
    print "</item>"
    print "</chain>"
    
def printplain(antecedent,anaphora):
    (token,lemma,tagset,precision,offset,length,dist) = antecedent
    (an_token,an_offset,an_length,an_type,an_count) = anaphora
    print token+'\t<---\t'+an_token+'\t'+'\t'+an_type


def printbrat(antecedent,anaphora):
    (token,offset,length) = antecedent
    offset_end = offset+length
    (an_token,an_offset,an_length,an_type,an_count) = anaphora
    an_offset_end = an_offset+an_length
    ent_number_antecedent = an_count+(an_count-1)
    ent_number_anaphora = ent_number_antecedent+1
    print 'T%d\tantecedent %d %d\t' % (ent_number_antecedent,offset,offset_end)
    print 'T%d\t%s %d %d\t' % (ent_number_anaphora,an_type,an_offset,an_offset_end)
    print 'R%d\tanaphora Arg1:T%d Arg2:T%d' % (an_count,ent_number_anaphora,ent_number_antecedent)
    


printFunctions = {'xml': printxml, 'plain': printplain, 'brat': printbrat}

for word in codecs.open('prons.txt','r','utf-8'):
    pronouns.append(word.strip())

for word in codecs.open('reflexives.txt','r','utf-8'):
    reflexives.append(word.strip())

#for word in codecs.open('demonstratives.txt','r','utf-8'):
#    demonstratives.append(word.strip())

for word in codecs.open('relatives.txt','r','utf-8'):
    relatives.append(word.strip())


text = codecs.open(argument,'r','utf-8').read()


anaphora_count = 0
curOffset = 0

#print '<?xml version="1.0" encoding="utf-8"?>'
#print '<rueval collectionid="RUEVAL-COREF2014" trackid="anaphora" systemid="penguin">'
#print '<documents>'
if currentOutput == "xml":
    print '<document file="%s">' % argument.replace('AnaphFiles/','')

words = []
if True:
    res = text.replace(u' ее',u' её')
    if currentOutput == 'plain':
	print res.strip().encode('utf-8')
    processed, curOffset = lemmatizer(res, startOffset = curOffset)
    for i in processed:
	found = False
	(token,lemma,tag,prob,offset) = i
	words.append(i)
	if len(words) > window:
	    dif = len(words) - window
	    words = words[dif:]
	if lemma in pronouns or lemma in reflexives or lemma in relatives:
	    ab = GetGroups(words)
	    previous_nouns = [word for word in ab if word[2].startswith('N') and not '.' in word[0]]
	    #print 'Pronoun',token+'\t'+tag+'\t'+lemma
	    anaph = [token,lemma,tag,prob,offset,len(token)]
	    ant = mlResolutor.FindAntecedent(anaph,ab)
	    if ant:
			anaphora_count += 1
			antecedent = ant[0][1]
			anaphora = (token,offset,len(token),'ml',anaphora_count)
			printFunctions[currentOutput](antecedent,anaphora)
			continue


if currentOutput == "xml":
    print "</document>"

#print "</documents>"
#print "</rueval>"

if currentOutput == "plain":
    print 'Anaphoric expressions:', anaphora_count