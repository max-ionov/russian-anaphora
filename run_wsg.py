from flask import Flask,request
from anaphora_main import *
from lemmatizer import *

app = Flask(__name__)

app.register_blueprint(anaphora)

if __name__ == "__main__":
	app.run()