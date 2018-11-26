import * as path from "path";
import * as yesql from "seduce";
import * as fs from "fs";

let sqlite3;
try {
    sqlite3 = require("sqlite3");
} catch (e) {
    console.error("sqlite3 NOT AVAILABLE");
    console.warn(e);
    // create a dummy object
    class DummyDatabase {
        error() {
            console.error("sqlite3 not available");
        }
        serialize(..._) { this.error() }
        each(..._) { this.error() }
        run(..._) { this.error() }
        get(..._) { this.error() }
        close(..._) {}
    }
    sqlite3 = { Database: DummyDatabase };
}

const $ANNOTATION_SQL_FILEPATH = path.join(
    __dirname, "../../sql",
    "main.sql",
);

const $HOME = process.env[(process.platform === "win32") ? "USERPROFILE" : "HOME"];
const $ADB_FILENAME = "ebook-viewer-annotation.db"
const $ADB_FILEPATH = path.join($HOME, $ADB_FILENAME);

import { OkfnAnnotation1, IOkfnAnnotation1 } from "./model";

type QueryParameter = {
    title?: string,
    note?: string,
    quote?: string,
}

/**
 * EXAMPLE:
 * 
 * AnnotationManager
 */
export namespace AnnotationManager {
    var databaseFilepath: string = $ADB_FILEPATH;
    export var Database;
    const annotationSql = yesql($ANNOTATION_SQL_FILEPATH);

    export function loadDatabase(filepath: string = null) {
        if (filepath) {
            databaseFilepath = filepath;
        }
        Database = new sqlite3.Database(databaseFilepath);
    }

    function wrapPercent(s: string) {
        return `%${s}%`;
    }

    export function loadMatchingAnnotations(
        param: QueryParameter,
        onFetchRow: Function = null,
        onComplete: Function = null,
    ) {
        if (!Database) {
            loadDatabase();
        }
        
        let sql, token;
        if(param.title) {
            token = wrapPercent(param.title);
            sql = annotationSql.getAnnotationsWithTitleLike(token);
        } else if(param.note) {
            token = wrapPercent(param.note);
            sql = annotationSql.getAnnotationsWithNoteLike(token);
        } else if(param.quote) {
            token = wrapPercent(param.quote)
            sql = annotationSql.getAnnotationsWithQuoteLike(token);
        }
        Database.serialize(
            function () {
                Database.each(sql, (function (err, row) {
                    if (err) {
                        console.warn(err);
                        return;
                    }
                    onFetchRow(new OkfnAnnotation1(row));
                }));
            },
            onComplete,
        );
    }

    export function addAnnotation(newAnnotation: IOkfnAnnotation1, onComplete: Function) {
        Database.serialize(function() {
            Database.run(
                // FIXME: this is manually building a prepared statement
                annotationSql.insertAnnotation().replace(/null/g, "?"),
                [
                    newAnnotation.created,
                    newAnnotation.updated,
                    newAnnotation.title,
                    newAnnotation.text,
                    newAnnotation.quote,
                    JSON.stringify(newAnnotation.extras),
                    newAnnotation.uri,
                    newAnnotation.user,
                ],
            );
            
            Database.serialize(
                function() {
                    let lastInserted = annotationSql.getLastInsertedId();
                    Database.get(lastInserted, function(err, row) {
                        console.log("INSERTED: ", row.id);
                        newAnnotation.id = row.id;
                        onComplete(newAnnotation);
                    });
                }
            )
        });
    }

    export function addRangeToAnnotation(
        annotation: OkfnAnnotation1,
        annotationRange,
        onComplete: Function
    ) {
        let sql = annotationSql.appendRangeToAnnotation({
            start: annotationRange.start,
            end: annotationRange.end,
            startOffset: annotationRange.startOffset,
            endOffset: annotationRange.endOffset,
            annotation_id: annotation.id,
        });
        Database.run(sql, (function(err, row) {
            onComplete(row);
        }));
    }
}
