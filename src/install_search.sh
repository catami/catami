#get schema
python manage.py build_solr_schema > schema.xml
sed -i.bak 's/stopwords_en.txt/lang\/stopwords_en.txt/' schema.xml
mv schema.xml ../apache-solr-4.0.0-BETA/example/solr/collection1/conf
