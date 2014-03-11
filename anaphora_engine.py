#!/usr/bin/python
#coding: utf-8
# An@phora resolution
import codecs,sys
from lemmatizer import lemmatizer
from lemmatizer import GetGroups
from lemmatizer import GetConjunctions
import datetime,os

def printbrat(antecedent,anaphora,filename):
    (token,offset,length) = antecedent
    offset_end = offset+length
    (an_token,an_offset,an_length,an_type,an_count) = anaphora
    if an_token == u'её':
	an_token = u'ее'
    an_offset_end = an_offset+an_length
    ent_number_antecedent = an_count+(an_count-1)
    ent_number_anaphora = ent_number_antecedent+1
    output = codecs.open('/var/www/brat/data/anaphora/%s' % filename+'.ann','a','utf-8')
    output.write('T%d\tantecedent %d %d\t%s\n' % (ent_number_antecedent,offset,offset_end,token))
    output.write('T%d\t%s %d %d\t%s\n' % (ent_number_anaphora,an_type,an_offset,an_offset_end,an_token))
    output.write('R%d\tanaphora Arg1:T%d Arg2:T%d\n' % (an_count,ent_number_anaphora,ent_number_antecedent))
    

def anaphora_res(text,window):
    text = text.replace(u' её',u' ее')
    os.chdir('/var/www/anaphora')
    d = datetime.datetime.now()
    filename = d.strftime("%d.%m.%Y%I-%M%S")
    output = codecs.open('/var/www/brat/data/anaphora/%s' % filename+'.txt','w','utf-8')
    output.write(text)
    output.close()
    open('/var/www/brat/data/anaphora/%s' % filename+'.ann', 'a').close()
    pronouns = []
    reflexives = []
    relatives = []
    for word in codecs.open('prons.txt','r','utf-8'):
	pronouns.append(word.strip())

    for word in codecs.open('reflexives.txt','r','utf-8'):
	reflexives.append(word.strip())

    for word in codecs.open('relatives.txt','r','utf-8'):
	relatives.append(word.strip())

    anaphora_count = 0
    curOffset = 0

    words = []
    res = text
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
	    previous_nouns = [word for word in ab if word[2].startswith('N') and not '.' in word[0]]
	    #print 'Pronoun',token+'\t'+tag+'\t'+lemma
	    if lemma == u"его" and tag.startswith('R'):
		for w in reversed(previous_nouns):
		    if w[2][4] != "F" and w[2][3] == tag[2]:
			#print w[0]+'\t'+w[1]+'\t'+str(w[2])+'\t<---\t'+token+'\t'+str(offset)
			anaphora_count += 1
			antecedent = (w[0],w[4],w[5])
			anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			printbrat(antecedent,anaphora,filename)
			break
		continue
	    elif lemma == u"он" or lemma == u"она" or lemma == u'они' or lemma == u'их' or lemma == u'оно':
		if token == u"Ним":
		    continue
		if tag[3] == "F":
		    for w in reversed(previous_nouns):
			if w[2][4] == "F":
			    if w[2][2] == "N" and w[2][5] == "A" and w[2][3] == tag[2]:
				#print w[0]+'\t'+w[2]+'\t'+str(w[2])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				printbrat(antecedent,anaphora,filename)
				found = True
				break
		    if found == False:
			for w in reversed(previous_nouns):
			    if w[2][4] == "F" and w[2][3] == tag[2]:
				#print w[0]+'\t'+w[2]+'\t'+str(w[2])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				printbrat(antecedent,anaphora,filename)
				break
		if tag[3] != "F":
		    for w in reversed(previous_nouns):
			if w[2][2] == "N" and w[2][5] == "A" and w[2][3] == tag[2] and w[2][4] != "F":
			    if tag[1] == "N" and tag[2] == "S" and w[2][4] != tag[3] and w[2][4] != "C":
				continue
			    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printbrat(antecedent,anaphora,filename)
			    found = True
			    break
		    if found == False:
			for w in reversed(previous_nouns):
			    if w[2][3] == tag[2]:
				if tag[2] == 'S' and w[2][4] == "F":
				    continue
				if tag[1] == "N" and tag[2] == "S" and w[2][4] != tag[3] and w[2][4] != "C":
				    continue
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'pronoun',anaphora_count)
				printbrat(antecedent,anaphora,filename)
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
                    printbrat(antecedent,anaphora,filename)
                    break
		continue

	    else:
		for w in reversed(previous_nouns):
		    if w[2][3] == 'P' and tag[2] == 'P':
			#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			anaphora_count += 1
			antecedent = (w[0],w[4],w[5])
			anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			printbrat(antecedent,anaphora,filename)
			break
		    if w[2][3] == 'S' and tag[2] == 'S':
			if w[2][4] == "F" and tag[3] == "F":
			    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printbrat(antecedent,anaphora,filename)
			    break
			if w[2][4] != "F" and tag[3] != "F":
			    #print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'pronoun',anaphora_count)
			    printbrat(antecedent,anaphora,filename)
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
			printbrat(antecedent,anaphora,filename)
			break
	    elif lemma == u"свой":
		for w in reversed(previous_nouns):
		    if w[2][2] == "N" and w[2][0] == "N" or w[2][0] == "E" and w[2][1] == "N":
			if w[0] != u"что" and w[0] != u"Что":
			#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
			    anaphora_count += 1
			    antecedent = (w[0],w[4],w[5])
			    anaphora = (token,offset,len(token),'reflexive',anaphora_count)
			    printbrat(antecedent,anaphora,filename)
			    break

	elif lemma in relatives:
	    ab = GetGroups(words)
	    previous_nouns = [word for word in ab if word[2].startswith('N') or word[2].startswith('Fc')]
	    #print 'Relatives',token+'\t'+tag+'\t'+lemma
	    #for i in ab:
	#	print i[0],i[2]
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
				printbrat(antecedent,anaphora,filename)
				break
			if w[2][3] == 'S' and tag[2] == 'S':
			    if w[2][4] == "F" and tag[3] == "F":
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'relative',anaphora_count)
				printbrat(antecedent,anaphora,filename)
				break
			    if w[2][4] != "F" and tag[3] != "F":
				#print w[0]+'\t'+w[2]+'\t'+str(w[4])+'\t<---\t'+token+'\t'+str(offset)
				anaphora_count += 1
				antecedent = (w[0],w[4],w[5])
				anaphora = (token,offset,len(token),'relative',anaphora_count)
				printbrat(antecedent,anaphora,filename)
				break
    return filename