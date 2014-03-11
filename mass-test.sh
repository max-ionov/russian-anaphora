#!/bin/sh

echo 'Window = 20'
echo '<?xml version="1.0" encoding="utf-8"?>' >> ofc.xml
echo '<rueval collectionid="RUEVAL-COREF2014" trackid="anaphora" systemid="ofc">' >> ofc.xml
echo '<documents>' >> ofc.xml


for f in `find AnaphFiles/OFC/ -name '*.*'` ; do
python anaphora.py $f 20 >> ofc.xml
done

echo "</documents>" >> ofc.xml
echo "</rueval>" >> ofc.xml

python precision.py ofc
