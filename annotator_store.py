import json
from annotator_model import Annotation, Range, session
import socket

CURRENT_USER_ID = unicode(socket.gethostname())

__all__ = ["app", "store", "setup_app"]

# We define our own jsonify rather than using flask.jsonify because we wish
# to jsonify arbitrary objects (e.g. index returns a list) rather than kwargs.
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=2)
    return res

def unjsonify(str):
    return json.loads(str)

def get_current_userid():
    return CURRENT_USER_ID

# INDEX
## @store.route('/annotations')
def index():
    annotations = [a.to_dict() for a in Annotation.query.all() if a.authorise('read', get_current_userid())]
    return jsonify(annotations)

# CREATE
## @store.route('/annotations', methods=['POST'])
def create_annotation(dict_of_request_json):
    dict_of_request_json[u"user"] = CURRENT_USER_ID
    annotation = Annotation()
    annotation.from_dict(dict_of_request_json)
    session.commit()

    return jsonify(annotation.to_dict())

# READ
## @store.route('/annotations/<int:id>')
def read_annotation(id):
    annotation = Annotation.get(id)

    if not annotation:
        return jsonify('Annotation not found.', status=404)

    else: # elif annotation.authorise('read', get_current_userid()):
        return jsonify(annotation.to_dict())

# UPDATE
## @store.route('/annotations/<int:id>', methods=['PUT'])
def update_annotation(id, dict_of_request_json):
    annotation = Annotation.get(id)

    if not annotation:
        return jsonify('Annotation not found. No update performed.', status=404)

    else:
    # elif request.json and annotation.authorise('update', get_current_userid()):
        annotation.from_dict(dict_of_request_json)
        session.commit()
        return jsonify(annotation.to_dict())

# DELETE
## @store.route('/annotations/<int:id>', methods=['DELETE'])
def delete_annotation(id):
    annotation = Annotation.get(id)

    if not annotation:
        return jsonify('Annotation not found. No delete performed.', status=404)

    ## elif annotation.authorise('delete', get_current_userid()):
    else:
        annotation.delete()
        session.commit()
        return None, 204

# Search
## @store.route('/search')
def search_annotations(**args):
    params = [
        (k,v) for k,v in args.items() if k not in [ 'all_fields', 'offset', 'limit' ]
    ]
    all_fields = args.get('all_fields', False)
    all_fields = bool(all_fields)
    offset = args.get('offset', 0)
    limit = int(args.get('limit', 100))
    if limit < 0:
        limit = None

    q = Annotation.query
    for k,v in params:
        kwargs = { k: unicode(v) }
        q = q.filter_by(**kwargs)

    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    if all_fields:
        rows = [ x.to_dict() for x in rows ]
    else:
        rows = [ {'id': x.id} for x in rows ]

    qrows = {
        'total': total,
        'rows': rows
    }
    return jsonify(qrows)

