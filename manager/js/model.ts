class RangeDef {
    id: any;
    start: any;
    end: any;
    startOffset: any;
    endOffset: any;
    annotation: any;
}

export interface IRange extends RangeDef {}

export class Range extends RangeDef {
    constructor(data: IRange) {
        super();
        for (const key of Object.keys(data)) {
            this[key] = data[key];
        }
    }
}


class AnnotationDef {
    id: any;
    uri: any;
    title: any;
    text: any;
    quote: any;
    user: any;
    extras: any;
    created: any;
    updated: any;
    _extras: any; // (JSON.parse data.extras)
    _ranges: any; // null
}

export interface IAnnotation extends AnnotationDef {}

export class Annotation extends AnnotationDef {
    constructor(data: IAnnotation) {
        super();
        for (const key of Object.keys(data)) {
            this[key] = data[key];
        }
        this._extras = this._extras || {};
    }

    getRanges() {
        if(!this._ranges) {
            // ??? FIXME
            this._ranges = ["STUFF"];
        }
        return this._ranges;
    }

    getExtras(key) {
        return this._extras[key];
    }
}


// from calibre library `books` table
class BookDef {
    id: any;
    title: any;
    sort: any;
    timestamp: any;
    pubdate: any;
    series_index: any;
    author_sort: any;
    isbn: any;
    lccn: any;
    path: any;
    flags: any;
    uuid: any;
    has_cover: any;
    last_modified: any;
}

export interface IBook extends BookDef {}

export class Book extends BookDef {
    constructor(data: IBook) {
        super();
        for (const key of Object.keys(data)) {
            this[key] = data[key];
        }
    }
}
