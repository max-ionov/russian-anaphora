#!/usr/bin/python
#coding: utf-8
# An@phora resolution
import codecs,sys
from lemmatizer import lemmatizer
from lemmatizer import GetGroups
from lemmatizer import GetConjunctions

def print_usage(file_used):
    print 'Usage: ' + file_used + ' <file to analyze> <length of analysis window, in words> <output format: plain,xml,brat>'

if len(sys.argv) > 4 or len(sys.argv) < 2:
    print_usage(sys.argv[0])
    exit(1)

argument = sys.argv[1]
window = 23
currentOutput = 'plain'

for arg in sys.argv[2:]:
    if arg.isdigit() and 1 < int(arg) < 500:
	window = int(arg)
	continue
    else:
	if arg.strip() == 'plain' or arg.strip() == 'xml' or arg.strip() == 'brat':
	    currentOutput = arg.strip()
	    continue
	else:
	    print_usage(sys.argv[0])
	    exit(1)

pronouns = []
reflexives = []
demonstratives = []
relatives = []

def printxml(antecedent,anaphora):
    print "<chain>"
    (token,offset,length) = antecedent
    print '<item sh="%s" ln="%s" type="anaph">' % (offset,length)
    print '<cont><![CDATA[%s]]></cont>' % token.encode('utf-8')
    print "</item>"
    (token,offset,length,an_type,an_count) = anaphora
    print '<item sh="%s" ln="%s" comment="%s" type="anaph">' % (offset,length,an_type)
    print '<cont><![CDATA[%s]]></cont>' % token.encode('utf-8')
    print "</item>"
    print "</chain>"
    
def printplain(antecedent,anaphora):
    (token,offset,length) = antecedent
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

if currentOutput == "xml":
    print '<document file="%s">' % argument.replace('AnaphFiles/','')

words = []
if True:
    res = text.replace(u' ее',u' её')
    if currentOutput == 'plain':
	print res.strip().encode('utf-8')
    #processed, curOffset = lemmatizer(res, startOffset = curOffset, loadFrom = argument)
    processed, curOffset = lemmatizer(res, startOffset = curOffset)
    for i in processed:
	found = False
	(token,lemma,tag,prob,offset) = i
	words.append(i)
	if len(words) > window:
	    dif = len(words) - window
	    words = words[dif:]
	if lemma in pronouns:
	    ab = GetGroups(words)
	    previous_nouns = [word for word in ab if word[2].startswith('N') and not '.' in word[0] or word[2].startswith('F') or word[2].startswith('C')]
	    #print 'Pronoun',token+'\t'+tag+'\t'+lemma
	    if lemma == u"его" and tag.startswith('R'):
		clause = 0
		for w in reversed(previous_nouns):
		    if w[2].startswith('F') or w[2].startswith('C'):
			clause = 1
			continue
		    if clause == 1 and w[2].startswith('N'):
			if w[2][4] != "F" and w[2][3] == tag[2]:
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printFunctions[currentOutput](antecedent,anaphora)
			    break
		continue
	    elif lemma == u"он" or lemma == u"она" or lemma == u'они' or lemma == u'их' or lemma == u'оно':
		if token == u"Ним":
		    continue
		if tag[3] == "F":
		    clause = 0
		    for w in reversed(previous_nouns):
			if w[2].startswith('F') or w[2].startswith('C'):
			    clause = 1
			    continue
			if clause == 1 and w[2].startswith('N'):
			    if w[2][4] == "F":
				if w[2][2] == "N" and w[2][5] == "A" and w[2][3] == tag[2]:
				    anaphora_count += 1
				    antecedent = (w[0],w[4],w[5])
				    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				    printFunctions[currentOutput](antecedent,anaphora)
				    found = True
				    break
		    if found == False:
			clause = 0
			for w in reversed(previous_nouns):
			    if w[2].startswith('F') or w[2].startswith('C'):
				clause = 1
				continue
			    if clause == 1 and w[2].startswith('N'):
				if w[2][4] == "F" and w[2][3] == tag[2]:
				    anaphora_count += 1
				    antecedent = (w[0],w[4],w[5])
				    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				    printFunctions[currentOutput](antecedent,anaphora)
				    break
		if tag[3] != "F":
		    clause = 0
		    for w in reversed(previous_nouns):
			if w[2].startswith('F') or w[2].startswith('C'):
				clause = 1
				continue
			if clause == 1 and w[2].startswith('N'):
			    if w[2][2] == "N" and w[2][5] == "A" and w[2][3] == tag[2] and w[2][4] != "F":
				if tag[1] == "N" and tag[2] == "S" and w[2][4] != tag[3] and w[2][4] != "C":
				    continue
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				printFunctions[currentOutput](antecedent,anaphora)
				found = True
			        break
		    if found == False:
			clause = 0
			for w in reversed(previous_nouns):
			    if w[2].startswith('F') or w[2].startswith('C'):
				clause = 1
				continue
			    if clause == 1 and w[2].startswith('N'):
				if w[2][3] == tag[2]:
				    if tag[2] == 'S' and w[2][4] == "F":
					continue
				    if tag[1] == "N" and tag[2] == "S" and w[2][4] != tag[3] and w[2][4] != "C":
					continue
				    anaphora_count += 1
				    antecedent = (w[0],w[4],w[5])
				    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				    printFunctions[currentOutput](antecedent,anaphora)
				    break
		continue

	    elif lemma == u"мой":
		previous_pronouns = [word for word in ab if word[2].startswith('E') and word[2][5] == "1" and not '.' in word[0]]
		for w in reversed(previous_pronouns):
		    if tag[2] == "S" and w[2][2] == "P":
			continue
		    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
		    anaphora_count += 1
		    antecedent = (w[0],w[4],w[5])
		    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
		    printFunctions[currentOutput](antecedent,anaphora)
		    break
		continue
	    
	    else:
		for w in reversed(previous_nouns):
		    if w[2][3] == 'P' and tag[2] == 'P':
			#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			anaphora_count += 1
			antecedent = (w[0],w[4],w[5])
			anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			printFunctions[currentOutput](antecedent,anaphora)
			break
		    if w[2][3] == 'S' and tag[2] == 'S':
			if w[2][4] == "F" and tag[3] == "F":
			    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printFunctions[currentOutput](antecedent,anaphora)
			    break
			if w[2][4] != "F" and tag[3] != "F":
			    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printFunctions[currentOutput](antecedent,anaphora)
			    break
	
	
	elif lemma in reflexives:
	    ab = GetGroups(words)
	    previous_nouns = [word for word in ab if word[2].startswith('N') or word[2].startswith('E') and not '.' in word[0]]
	    #print 'Reflexive',token+'\t'+tag+'\t'+lemma
	    if lemma == u"себе":
		if words[-2][1] == u'сам':
		    continue
		previous_nouns = previous_nouns[:-1]
		for w in reversed(previous_nouns):
		    if w[0] != u"что" and w[0] != u"Что":
			#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			anaphora_count += 1
			antecedent = (w[0],w[4],w[5])
			anaphora = (token,offset,len(token),'reflexive',anaphora_count)
			printFunctions[currentOutput](antecedent,anaphora)
			break
	    elif lemma == u"свой":
		for w in reversed(previous_nouns):
		    if w[2][2] == "N" or w[2][0] == "E" and w[2][1] == "N":
			if w[0] != u"что" and w[0] != u"Что":
			#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'reflexive',anaphora_count)
			    printFunctions[currentOutput](antecedent,anaphora)
			    break


	elif lemma in relatives:
	    ab = GetGroups(words)
	    previous_nouns = [word for word in ab if word[2].startswith('N') or word[2].startswith('Fc')]
	    #print 'Relatives',token+'\t'+tag+'\t'+lemma
	    comma = 0
	    for w in reversed(previous_nouns):
		if w[0] == ',':
		    comma = 1
		    continue
		if comma == 1:
		    if w[2].startswith('N'):
			if w[2][3] == 'P':
			    if tag[2] == 'P' or token == u"которым":
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'relative',anaphora_count)
				printFunctions[currentOutput](antecedent,anaphora)
				break
			if w[2][3] == 'S' and tag[2] == 'S':
			    if w[2][4] == "F" and tag[3] == "F":
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'relative',anaphora_count)
				printFunctions[currentOutput](antecedent,anaphora)
				break
			    if w[2][4] != "F" and tag[3] != "F":
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'relative',anaphora_count)
				printFunctions[currentOutput](antecedent,anaphora)
				break

if currentOutput == "xml":
    print "</document>"

if currentOutput == "plain":
    print 'Anaphoric expressions:', anaphora_count