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

import { OkfnAnnotation1 } from "./model";

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
    var databaseFilepath: string;
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
}
