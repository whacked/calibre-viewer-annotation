"""
test integrating Elixir entities with plain SQLAlchemy defined classes
"""

from sqlalchemy.orm import *
from sqlalchemy import *
from elixir import *

class TestSQLAlchemyToElixir(object):
    def setup(self):
        metadata.bind = "sqlite://"

    def teardown(self):
        cleanup_all(True)

    def test_simple(self):
        class A(Entity):
            name = Field(String(60))

        # Remember the entity need to be setup before you can refer to it from
        # SQLAlchemy.
        setup_all(True)

        b_table = Table('b', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(60)),
            Column('a_id', Integer, ForeignKey(A.id))
        )
        b_table.create()

        class B(object):
            pass

        mapper(B, b_table, properties={
            'a': relation(A)
        })

        b1 = B()
        b1.name = 'b1'
        b1.a = A(name='a1')

        session.add(b1)
        session.commit()
        session.expunge_all()

        b = session.query(B).one()

        assert b.a.name == 'a1'


class TestElixirToSQLAlchemy(object):
    def setup(self):
        metadata.bind = "sqlite://"

    def teardown(self):
        cleanup_all(True)

    def test_m2o(self):
        a_table = Table('a', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(60)),
        )
        a_table.create()

        class A(object):
            pass

        mapper(A, a_table)

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne(A)

        setup_all(True)

        a1 = A()
        a1.name = 'a1'
        b1 = B(name='b1', a=a1)

        session.add(b1)
        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.name == 'a1'

    def test_m2o_non_pk_target(self):
        a_table = Table('a', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(60), unique=True)
        )
        a_table.create()

        class A(object):
            pass

        mapper(A, a_table)

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne(A, target_column=['name'])
# currently fails
#            c = ManyToOne('C', target_column=['id', 'name'])

#        class C(Entity):
#            name = Field(String(60), unique=True)

        setup_all(True)

        a1 = A()
        a1.name = 'a1'
        b1 = B(name='b1', a=a1)

        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.name == 'a1'

#    def test_m2m(self):
#        a_table = Table('a', metadata,
#            Column('id', Integer, primary_key=True),
#            Column('name', String(60), unique=True)
#        )
#        a_table.create()
#
#        class A(object):
#            pass
#
#        mapper(A, a_table)
#
#        class B(Entity):
#            name = Field(String(60))
#            many_a = ManyToMany(A)
#
#        setup_all(True)
#
#        a1 = A()
#        a1.name = 'a1'
#        b1 = B(name='b1', many_a=[a1])
#
#        session.commit()
#        session.expunge_all()
#
#        b = B.query.one()
#
#        assert b.many_a[0].name == 'a1'

