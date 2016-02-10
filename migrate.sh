# A quick and dirty migrator script for older annotation database files.
# this file will likely be deleted in the future

if [ $# -lt 2 ]; then
   cat <<EOF
usage: ./migrate.sh INPUT.db OUTPUT.db
EOF
   exit 0;
fi

DBOLD=$1
DBNEW=$2

if [ ! -f $DBOLD ]; then
    echo "specified input file '$DBOLD' does not exist"
    exit 0;
fi
if [ $(sqlite3 $DBOLD '.schema annotation' | grep quote | wc -l) -gt 0 ]; then
    echo 'it looks like your database is already updated. leaving...'
    exit 0;
fi    
if [ -f $DBNEW ]; then
    ext=${DBNEW##*.}
    base=${DBNEW%.*}
    now=$(date +%Y-%m-%d_%H%M%S)
    DBBCK=$base.$now.$ext
    echo "output file '$DBNEW' exists already. it will be renamed to ${DBBCK}"
    mv $DBNEW $DBBCK;
fi

cp $DBOLD $DBNEW

if [ $(sqlite3 $DBNEW '.schema' | grep 'CREATE TABLE .*range.*' | wc -l) -eq 2 ]; then
    echo 'INFO: found 2 range tables; combining them...'
    sqlite3 $DBNEW 'BEGIN TRANSACTION; INSERT INTO range ("id", "start", "end", "startOffset", "endOffset", "annotation_id") SELECT "id", "start", "end", "startOffset", "endOffset", "annotation_id" FROM annotator_model_range; COMMIT;'
    sqlite3 $DBNEW 'DROP TABLE annotator_model_range;'
fi

if [ $(sqlite3 $DBNEW '.schema' | grep 'CREATE TABLE .*annotation.*' | wc -l) -eq 2 ]; then
    echo 'INFO: found 2 range tables; combining them...'
    sqlite3 $DBNEW 'BEGIN TRANSACTION; INSERT INTO annotation ("id", "uri", "title", "text", "user", "extras", "timestamp") SELECT "id", "uri", "title", "text", "user", "extras", "timestamp" FROM annotator_model_annotation; COMMIT;'
    sqlite3 $DBNEW 'DROP TABLE annotator_model_annotation;'
fi

if [ $(sqlite3 $DBNEW '.schema' | grep 'CREATE TABLE .*consumer.*' | wc -l) -eq 2 ]; then
    echo 'INFO: found 2 consumer tables; combining them (though, they should both be empty)...'
    sqlite3 $DBNEW 'BEGIN TRANSACTION; INSERT INTO consumer ("key", "secret", "ttl") SELECT "key", "secret", "ttl" FROM annotator_model_consumer; COMMIT;'
    sqlite3 $DBNEW 'DROP TABLE annotator_model_consumer;'
fi

echo 'INFO: combine check complete, now running table conversion'

# sqlite3 does not do column renaming (need it for timestamp, unless
# you want to leave it dangling) so we will do a full
# RENAME, CREATE, INSERT, DROP
sqlite3 $DBNEW <<EOF
BEGIN TRANSACTION;
-- old table to be deleted
ALTER TABLE annotation RENAME TO annotation_old;

-- new table with new structure;
-- these are new:
--     quote
--     created
--     updated
-- these are removed:
--     timestamp
CREATE TABLE annotation (
	id INTEGER NOT NULL,
	uri TEXT,
	title TEXT,
	text TEXT,
	quote TEXT,
	user TEXT,
	extras TEXT,
	created DATETIME,
	updated DATETIME,
	PRIMARY KEY (id)
);

INSERT INTO annotation(id, uri, title, text, quote, user, extras, created,   updated  )
       SELECT          id, uri, title, text,  text, user, extras, timestamp, timestamp
       FROM annotation_old;
DROP TABLE annotation_old;
COMMIT;
EOF

echo 'INFO: all done. PLEASE DOUBLE CHECK YOUR DATA!'
