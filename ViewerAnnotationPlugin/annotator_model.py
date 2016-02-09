# almost exactly as
# https://github.com/nickstenning/annotator-store-flask/blob/89b3037b995f094f73f24037123c0e818036e36c/annotator/model.py

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
    uri    = Column(Text)
    title  = Column(Text)
    text   = Column(Text)
    user   = Column(Text)
    extras = Column(Text, default=u'{}')
    timestamp = Column(DateTime, default=datetime.datetime.now)

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

    def to_dict(self, deep={}, exclude=[]):
        result = {
            'ranges': []
        }
        for k, v in self.__dict__.iteritems():
            if k.startswith('_'): continue
            result[k] = v
        for rg in self.ranges:
            result['ranges'].append(rg.to_dict())
        return result

    def delete(self, *args, **kwargs):
        for r in self.ranges:
            self._session.delete(r)
        self._session.delete(self)

    def __repr__(self):
        return '<Annotation %s "%s">' % (self.id, self.text)

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
