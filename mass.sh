#!/bin/sh

echo 'Window = 20'
echo '<?xml version="1.0" encoding="utf-8"?>' >> penguin.xml
echo '<rueval collectionid="RUEVAL-COREF2014" trackid="anaphora" systemid="penguin">' >> penguin.xml
echo '<documents>' >> penguin.xml


for f in `find TestSet -name '*.*'` ; do
python anaphora.py $f 20 >> penguin.xml
done

echo "</documents>" >> penguin.xml
echo "</rueval>" >> penguin.xml

#python precision.py ofc
