russian-anaphora
================

System for automatic pronominal resolution for Russian

The repository is a mess right now. Here are the main moments:
These are rule-based, machine learning and hybrid systems for pronominal anaphora resolution in Russian.
To get antecedents for anaphors using only ML, one can use resolute-text.py

Usage: resolute-text.py input-text pronouns-list model

* input-text may be a file or '-' to read from STDIN. It should be in UTF-8 encoding.
* pronouns-list is a list with all the pronouns with their type. An example is config.txt in the repository.
* model is a file with a stored model. There is ready-to-use model in the repository: model.rf.all.dat: Random Forest classifier trained on approx. 8000 cases.
Note, that each model should be accompanied with *model-name.dat.label* file with labels.

Here is the example:
echo 'Мальчик сидел за столом. Он был задумчив.' | ./resolute-text.py - config.txt model.rf.all.dat
