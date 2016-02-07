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
        result = {
            'ranges': []
        }
        for k, v in self.__dict__.iteritems():
            if k.startswith('_'): continue
            result[k] = v
        for rg in self.range_list:
            result['ranges'].append(rg.to_dict())
        return result

    def delete(self, *args, **kwargs):
        for range in self.ranges:
            range.delete()

        return super(Annotation, self).delete(*args, **kwargs)

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
            backref=backref('range_list', lazy='dynamic'))

    def __repr__(self):
        return '<Range %s %s@%s %s@%s>' % (self.id, self.start, self.startOffset, self.end, self.endOffset)

    def to_dict(self):
        return dict((k,v) for k,v in self.__dict__.iteritems()
                if not k.startswith('_'))

class Consumer(Base, DBMixin):
    __tablename__ = 'consumer'

    key    = Column(String(512), primary_key=True)
    secret = Column(String(512))
    ttl    = Column(Integer, default=3600, nullable=False)

    def __repr__(self):
        return '<Consumer %s>' % (self.key)
