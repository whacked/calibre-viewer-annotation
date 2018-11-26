// TODO: migrate to openannotation format
// see https://github.com/hypothesis/h/blob/master/h/schemas/annotation.py

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
type Uri = string;
type MimeType = string;
type Language = string;

class WebAnnotationBody {
    id: any;
    format: MimeType;
    language: Language;
    value?: string;
}

class Relationship {

}

class WebAnnotationDataModel {
    id: any; // FIXME
    type: string;
    body: WebAnnotationBody;
    target: Relationship;
}

// https://github.com/openannotation/annotator
class OkfnAnnotation1Def {
    id?: any;
    uri?: any;
    title?: any;

    text?: string;
    noteText?: string; // kindle

    quote?: string;
    highlightText?: string; // kindle

    user?: any;

    extras?: any; // (JSON.parse data.extras)
    ranges?: any;
    created?: any;
    updated?: any;

    // https://www.w3.org/TR/annotation-model/
    body?: {

    }
}

export interface IOkfnAnnotation1 extends OkfnAnnotation1Def {}

export class OkfnAnnotation1 extends OkfnAnnotation1Def {
    constructor(data: IOkfnAnnotation1) {
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

        this.extras = this.extras || {};
        this.ranges = this.ranges || [];
    }

    getRanges() {
        if(!this.ranges) {
            // ??? FIXME
            this.ranges = ["STUFF"];
        }
        return this.ranges;
    }

    getExtras(key) {
        return this.extras[key];
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

type KindleHighlightColor = "Yellow" | "Blue" | "Red" | "Orange";

export class KindleAnnotation {
    asin: any;
    customerId: any;
    embeddedId: any;
    timestamp?: any;
    howLongAgo: any;
    startLocation?: number;
    endLocation?: any;
    pageNumber?: number;
    note: any;
    highlight: any;
    highlightColor?: KindleHighlightColor;

    constructor(data: any) {
        this.asin = data.asin;
        this.customerId = data.customerId;
        this.embeddedId = data.embeddedId;
        this.endLocation = data.endLocation;
        this.highlight = data.highlight || data.highlightText;
        this.howLongAgo = data.howLongAgo;
        this.startLocation = data.startLocation;
        this.pageNumber = data.pageNumber;
        this.timestamp = data.timestamp;
        this.note = data.note || data.noteText;
        this.highlightColor = data.highlightColor;
    }

    toOkfnAnnotation1(): OkfnAnnotation1 {
        var extras = {};
        for(const key of [
            "pageNumber",
            "startLocation",
            "endLocation",
            "howLongAgo",
            "highlightColor",
        ]) {
            if(this[key]) {
                extras[key] = this[key];
            }
        }

        var out = new OkfnAnnotation1({
            user: this.customerId,

            text: this.note,
            quote: this.highlight,
            
            created: this.timestamp,
            updated: this.timestamp,

            extras: extras,
        });
        return out
    }
}

export class CalibreAnnotation extends OkfnAnnotation1 {
    verification: any;
    dbEntry: any;
     
    constructor(data: any) {
        super(data);
        
        this.verification = data.verification;
        this.dbEntry = data.dbEntry;
    }
}
