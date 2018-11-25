import { setFlagsFromString } from "v8";

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

// https://www.w3.org/TR/annotation-model/
type Uri = String;
type MimeType = String;
type Language = String;

class WebAnnotationBody {
    id: any;
    format: MimeType;
    language: Language;
    value?: String;
}

class Relationship {

}

class WebAnnotationDataModel {
    id: any; // FIXME
    type: String;
    body: WebAnnotationBody;
    target: Relationship;
}

// https://github.com/openannotation/annotator
class AnnotationDef {
    id?: any;
    uri?: any;
    title?: any;

    text?: String;
    noteText?: String; // kindle

    quote?: String;
    highlightText?: String; // kindle

    user?: any;

    extras?: any;
    created?: any;
    updated?: any;

    _extras?: any; // (JSON.parse data.extras)
    _ranges?: any; // null

    // https://www.w3.org/TR/annotation-model/
    body?: {

    }
}

export interface IAnnotation extends AnnotationDef {}

export class Annotation extends AnnotationDef {
    constructor(data: IAnnotation) {
        super();
        for (const key of Object.keys(data)) {
            this[key] = data[key];
        }

        if(!this.text && data.noteText) {
            this.text = data.noteText;
        }
        if(!this.quote && data.highlightText) {
            this.quote = data.highlightText;
        }

        this._extras = this._extras || {};
        this._ranges = this._ranges || [];
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

export class KindleAnnotation {
    asin: any;
    customerId: any;
    embeddedId: any;
    endLocation: any;
    highlight: any;
    howLongAgo: any;
    startLocation: any;
    timestamp: any;
    note: any;

    constructor(data: any) {
        this.asin = data.asin;
        this.customerId = data.customerId;
        this.embeddedId = data.embeddedId;
        this.endLocation = data.endLocation;
        this.highlight = data.highlight || data.highlightText;
        this.howLongAgo = data.howLongAgo;
        this.startLocation = data.startLocation;
        this.timestamp = data.timestamp;
        this.note = data.note || data.noteText;
    }

    toAnnotation(): Annotation {
        var out = new Annotation({
            user: this.customerId,

            text: this.note,
            quote: this.highlight,
            
            created: this.timestamp,
            updated: this.timestamp,
        });
        return out
    }
}

export class CalibreAnnotation extends Annotation {
    verification: any;
    dbEntry: any;
    
    constructor(data: any) {
        super(data);
        
        this.verification = data.verification;
        this.dbEntry = data.dbEntry;
    }
}
