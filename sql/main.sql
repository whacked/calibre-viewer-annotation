-- name: getBooksWithTitleLike
SELECT *
FROM annotation
WHERE title LIKE :title;

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
