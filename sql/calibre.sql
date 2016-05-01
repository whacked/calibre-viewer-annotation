-- name: getAllEpubBooks
SELECT b.*
FROM books AS b, data AS d
WHERE b.id = d.book AND d.format = 'EPUB'
ORDER BY id DESC;

-- name: getEpubPathInfoById
SELECT b.path, d.name
FROM books AS b, data AS d
WHERE b.id = d.book AND d.format = 'EPUB'
AND b.id = :book_id LIMIT 1;

-- name: getEpubPathInfoByTitle
SELECT b.path, d.name
FROM books AS b, data AS d
WHERE b.id = d.book AND d.format = 'EPUB'
AND b.title LIKE :book_title
LIMIT 1;

