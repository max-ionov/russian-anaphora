#coding: utf-8

# test comment
import os
import codecs
import logging 
import re

from datetime import datetime
from flask import render_template, Blueprint,redirect
from flask import request,url_for
from flask import current_app
from math import ceil
from anaphora_engine import *
from lemmatizer import *

anaphora = Blueprint('anaphora', __name__, template_folder='templates')


@anaphora.route('/', methods=['GET', 'POST'])
def finder():
    #print request.method
    if request.method == 'POST':
	text = request.form['text']
	if text:
	    try:
		text = re.sub(' +', ' ', text)
		filename = anaphora_res(text,23)
		return render_template('anaphora_resolved.html', resolved = filename)
    	    except:
		logging.exception('')
		return render_template("anaphora.html", no = "Exception!")
        	        	
	else:
	    error_value = "!"
	    return render_template("anaphora.html", error=error_value)
    return render_template("anaphora.html")
