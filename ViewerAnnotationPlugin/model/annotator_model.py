# almost exactly as
# https://github.com/nickstenning/annotator-store-flask/blob/89b3037b995f094f73f24037123c0e818036e36c/annotator/model.py

# <path_hack>
# PATH HACK!!!
# this is to allow calibre to include the local install of sqlalchemy and elixir.
# don't know how to bundle them nicely inside the plugin directory alone.
import os, sys
import os.path as _p
sys.path.insert(0, os.getcwd())

# CHANGE THIS:
sys.path.insert(0, _p.expanduser("/usr/lib/python2.7/dist-packages")) # for elixir
# </path_hack>

# attempt to force preference of the local elixir
sys.path.insert(0, _p.join(os.getcwd(), 'elixir'))

import datetime
import sqlalchemy
from elixir import *
import json

def setup_in_memory():
    metadata.bind = "sqlite:///:memory:"
    setup_all(True)

class Annotation(Entity):
    using_options(tablename='annotation')

    id     = Field(Integer, primary_key=True)
    uri    = Field(UnicodeText)
    title  = Field(UnicodeText)
    text   = Field(UnicodeText)
    user   = Field(UnicodeText)
    extras = Field(UnicodeText, default=u'{}')
    ranges = OneToMany('Range')
    timestamp = Field(DateTime, default=datetime.datetime.now)

    def authorise(self, action, user=None):
        # If self.user is None, all actions are allowed
        if not self.user:
            return True

        # Otherwise, everyone can read and only the same user can
        # do update/delete
        if action is 'read':
            return True
        else:
            return user == self.user

    def from_dict(self, data):
        obj = {
            u'extras': json.loads(self.extras if self.extras else u'{}')
        }

        for key in data:
            if hasattr(self, key):
                obj[key] = data[key]
            else:
                obj[u'extras'][key] = data[key]

        # Reserialize
        obj[u'extras'] = json.dumps(obj[u'extras'], ensure_ascii=False)

        if u'ranges' in obj:
            ranges = obj[u'ranges']
            del obj[u'ranges']
        else:
            ranges = None

        super(Annotation, self).from_dict(obj)

        if ranges:
            for range in self.ranges:
                range.delete()

            for range_data in ranges:
                if u'id' in range_data:
                    del range_data[u'id']

                range = Range()
                range.from_dict(range_data)
                self.ranges.append(range)

    def to_dict(self, deep={}, exclude=[]):
        deep.update({'ranges': {}})

        result = super(Annotation, self).to_dict(deep, exclude)

        try:
            extras = json.loads(result[u'extras'])
        except(TypeError):
            extras = {}

        del result[u'extras']

        for key in extras:
            result[key] = extras[key]

        return result

    def delete(self, *args, **kwargs):
        for range in self.ranges:
            range.delete()

        return super(Annotation, self).delete(*args, **kwargs)

    def __repr__(self):
        return '<Annotation %s "%s">' % (self.id, self.text)

class Range(Entity):
    using_options(tablename='range')

    id          = Field(Integer, primary_key=True)
    start       = Field(Unicode(255))
    end         = Field(Unicode(255))
    startOffset = Field(Integer)
    endOffset   = Field(Integer)

    annotation  = ManyToOne('Annotation')

    def __repr__(self):
        return '<Range %s %s@%s %s@%s>' % (self.id, self.start, self.startOffset, self.end, self.endOffset)

class Consumer(Entity):
    using_options(tablename='consumer')

    key    = Field(String(512), primary_key=True, required=True)
    secret = Field(String(512), required=True)
    ttl    = Field(Integer, default=3600, nullable=False)

    def __repr__(self):
        return '<Consumer %s>' % (self.key)
