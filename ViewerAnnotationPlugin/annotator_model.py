# almost exactly as
# https://github.com/nickstenning/annotator-store-flask/blob/89b3037b995f094f73f24037123c0e818036e36c/annotator/model.py

# <path_hack>
# PATH HACK!!!
# this is to allow calibre to include the local install of sqlalchemy.
# don't know how to bundle them nicely inside the plugin directory alone.
import os, sys
import os.path as _p
# CHANGE THIS:
sys.path.insert(0, _p.expanduser("/usr/lib/python2.7/dist-packages"))
# </path_hack>

import datetime
import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import \
        Table, Column, \
        Integer, String, Text, DateTime, \
        ForeignKey
from sqlalchemy.orm import mapper, sessionmaker, relationship, backref
import json

Base = declarative_base()

class DBMixin:
    _session = None
    @classmethod
    def get(cls, id=None, **kw):
        if cls._session is None:
            return None
        if id is not None:
            return cls._session.query(cls).get(id)
        elif kw:
            return cls._session.query(cls).filter_by(**kw).first()

class Annotation(Base, DBMixin):
    __tablename__ = 'annotation'

    id     = Column(Integer, primary_key=True)
    # (official, but reappropriated) source document's URI;
    # in this case, it is a custom URI for a file within an ebook,
    # which is assumed to be an epub
    uri    = Column(Text)
    # (unofficial) title of the book
    title  = Column(Text)
    # (officlal) "the text that was annotated", i.e. original text from the
    # book
    quote  = Column(Text)
    # (officlal) "the 'content' of annotation", i.e. the attached comment from
    # the user
    text   = Column(Text)
    # (official) who annotated it. currently it's just you
    user   = Column(Text)
    # (unofficial) this came from the annotator-store reference ~2010 to store
    # all non-official data.  it will be a candidate for deprecation in the
    # future, but while the model is still small, it is easy to work with.
    extras = Column(Text, default=u'{}')
    
    # (official)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def make_uri(self, local_uri, ebook_format='epub'):
        '''
        (convenience method) constructs an ebook file relative URI,
        e.g. epub://page0022.html
        '''
        return '{}://{}'.format(ebook_format, local_uri)

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

    # NOTE: this is supposed to supercede a from_dict
    # method originally implemented in elixir.Entity;
    # though I think it makes more sense as a classmethod
    # and will probably move in that direction
    def from_dict(self, data):
        obj = {
            u'extras': json.loads(self.extras if self.extras else u'{}')
        }

        ranges = data.pop('ranges', None)
        for key in data:
            if hasattr(self, key):
                obj[key] = data[key]
            else:
                obj[u'extras'][key] = data[key]
        # Reserialize
        obj[u'extras'] = json.dumps(obj[u'extras'], ensure_ascii=False)
        for k in obj:
            setattr(self, k, obj[k])

        if ranges:
            for range in self.ranges:
                range.delete()

            for range_data in ranges:
                range = Range()
                range.from_dict(range_data)
                self.ranges.append(range)

    def to_dict(self):
        # process extras and ranges first
        out = json.loads(self.extras or '{}')
        out['ranges'] = [rg.to_dict() for rg in self.ranges]
        # process the rest
        for c in self.__table__.c:
            if c.name in out:
                continue
            else:
                out[c.name] = getattr(self, c.name)
        return out

    def delete(self, *args, **kwargs):
        for r in self.ranges:
            self._session.delete(r)
        self._session.delete(self)

    def __repr__(self):
        return '<Annotation %s "%s">' % (self.id, self.quote)

class Range(Base, DBMixin):
    __tablename__ = 'range'

    id          = Column(Integer, primary_key=True)
    start       = Column(String(255))
    end         = Column(String(255))
    startOffset = Column(Integer)
    endOffset   = Column(Integer)

    annotation_id = Column(Integer, ForeignKey('annotation.id'), nullable=False)
    annotation    = relationship('Annotation',
            backref=backref('ranges', lazy='dynamic'))

    # for backcompat, becuase elixir had such a method
    def delete(self, *args, **kwargs):
        self._session.delete(self)

    def __repr__(self):
        return '<Range %s %s@%s %s@%s>' % (self.id, self.start, self.startOffset, self.end, self.endOffset)

    def from_dict(self, dc):
        for c in self.__table__.c:
            setattr(self, c.name, dc.get(c.name))

    def to_dict(self):
        return dict((k,v) for k,v in self.__dict__.iteritems()
                if not k.startswith('_'))

# NOT USED, but see
# http://docs.annotatorjs.org/en/v1.2.x/authentication.html
# for motivation
class Consumer(Base, DBMixin):
    __tablename__ = 'consumer'

    key    = Column(String(512), primary_key=True)
    secret = Column(String(512))
    ttl    = Column(Integer, default=3600, nullable=False)

    def __repr__(self):
        return '<Consumer %s>' % (self.key)


# trigger sqla orm mapper configuration to apply backrefs,
# so class Annotation gets a `ranges` attr
from sqlalchemy.orm import configure_mappers
configure_mappers()
