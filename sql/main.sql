-- to be run against ebook-viewer-annotation.db

-- name: getAnnotationsWithTitleLike
SELECT *
FROM annotation
WHERE title LIKE :title;

-- name: getFullAnnotationsWithTitleLike
SELECT a.*
, r.start, r.startOffset
, r.end, r.endOffset
FROM annotation AS a, range AS r
WHERE r.annotation_id = a.id
AND a.title LIKE :title;

-- name: getAnnotationsWithQuoteLike
SELECT *
FROM annotation
WHERE quote LIKE :quote;

-- name: getAnnotationsWithNoteLike
SELECT *
FROM annotation
WHERE note LIKE :note;

-- name: getAnnotationsWithTitleLike
SELECT *
FROM annotation
WHERE title LIKE :title;

-- name: getRangesForAnnotation
SELECT * FROM
annotation AS ann,
range AS rng
WHERE ann.id = :annotation_id
AND rng.annotation_id = ann.id;

-- name: getAnnotationsWithMatchingRanges
SELECT * FROM
annotation AS a, range AS r
WHERE r.annotation_id = a.id
AND r.start = :start AND r.startOffset = :startOffset
AND r.end = :end AND r.endOffset = :endOffset;

-- name: insertAnnotation
INSERT INTO annotation (created, updated, title, text, quote, extras, uri, user)
VALUES (:created, :updated, :title, :text, :quote, :extras, :uri, :user);

-- name: appendRangeToAnnotation
INSERT INTO range (start, end, startOffset, endOffset, annotation_id)
VALUES (:start, :end, :startOffset, :endOffset, :annotation_id);

-- name: getLastInsertedId
SELECT last_insert_rowid() AS id;
