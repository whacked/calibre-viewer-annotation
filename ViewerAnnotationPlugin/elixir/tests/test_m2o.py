"""
test many to one relationships
"""

from elixir import *

def setup():
    metadata.bind = 'sqlite://'

class TestManyToOne(object):
    def teardown(self):
        cleanup_all(True)

    def test_simple(self):
        class A(Entity):
            name = Field(String(60))

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne('A')

        setup_all(True)

        b1 = B(name='b1', a=A(name='a1'))

        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.name == 'a1'

    def test_forward(self):
        class A(Entity):
            name = Field(String(60))

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne('A')
            c = ManyToOne('C')

        class C(Entity):
            name = Field(String(60))

        setup_all(True)

        b1 = B(name='b1', a=A(name='a1'), c=C(name='c1'))

        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.name == 'a1'
        assert b.c.name == 'c1'

    # this test is in test_o2m.py
    # def test_selfref(self):

    def test_with_key_pk(self):
        class A(Entity):
            test = Field(Integer, primary_key=True, key='testx')

        class B(Entity):
            a = ManyToOne('A')

        setup_all(True)

        b1 = B(a=A(testx=1))

        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.testx == 1

    def test_wh_key_in_m2o_col_kwargs(self):
        class A(Entity):
            name = Field(String(128), default="foo")

        class B(Entity):
            # specify a different key for the column so that
            #  it doesn't override the property when the column
            #  gets created.
            a = ManyToOne('A', colname='a',
                          column_kwargs=dict(key='a_id'))

        setup_all(True)

        assert 'id' in A.table.primary_key.columns
        assert 'a_id' in B.table.columns

        a = A()
        session.commit()
        b = B(a=a)
        session.commit()
        session.expunge_all()

        assert B.query.first().a == A.query.first()

    def test_specified_field(self):
        class Person(Entity):
            name = Field(String(30))

        class Animal(Entity):
            name = Field(String(30))
            owner_id = Field(Integer, colname='owner')
            owner = ManyToOne('Person', field=owner_id)

        setup_all(True)

        assert 'owner' in Animal.table.c
        assert 'owner_id' not in Animal.table.c

        homer = Person(name="Homer")
        slh = Animal(name="Santa's Little Helper", owner=homer)

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        animals = Animal.query.all()
        assert animals[0].owner is homer

    def test_one_pk(self):
        class A(Entity):
            name = Field(String(40), primary_key=True)

        class B(Entity):
            a = ManyToOne('A', primary_key=True)

        class C(Entity):
            b = ManyToOne('B', primary_key=True)

        setup_all()

        assert 'name' in A.table.primary_key.columns
        assert 'a_name' in B.table.primary_key.columns
        assert 'b_a_name' in C.table.primary_key.columns

    def test_m2o_is_only_pk(self):
        class A(Entity):
            pass

        class B(Entity):
            a = ManyToOne('A', primary_key=True)

        setup_all()

        assert 'id' in A.table.primary_key.columns
        assert 'a_id' in B.table.primary_key.columns
        assert 'id' not in B.table.primary_key.columns

    def test_multi_pk_in_target(self):
        class A(Entity):
            key1 = Field(Integer, primary_key=True)
            key2 = Field(String(40), primary_key=True)

        class B(Entity):
            num = Field(Integer, primary_key=True)
            a = ManyToOne('A', primary_key=True)

        class C(Entity):
            num = Field(Integer, primary_key=True)
            b = ManyToOne('B', primary_key=True)

        setup_all()

        assert 'key1' in A.table.primary_key.columns
        assert 'key2' in A.table.primary_key.columns

        assert 'num' in B.table.primary_key.columns
        assert 'a_key1' in B.table.primary_key.columns
        assert 'a_key2' in B.table.primary_key.columns

        assert 'num' in C.table.primary_key.columns
        assert 'b_num' in C.table.primary_key.columns
        assert 'b_a_key1' in C.table.primary_key.columns
        assert 'b_a_key2' in C.table.primary_key.columns

    def test_cycle_but_use_alter(self):
        class A(Entity):
            c = ManyToOne('C', use_alter=True)

        class B(Entity):
            a = ManyToOne('A', primary_key=True)

        class C(Entity):
            b = ManyToOne('B', primary_key=True)

        setup_all()

        assert 'a_id' in B.table.primary_key.columns
        assert 'b_a_id' in C.table.primary_key.columns
        assert 'id' in A.table.primary_key.columns
        assert 'c_b_a_id' in A.table.columns

    def test_multi(self):
        class A(Entity):
            name = Field(String(32))

        class B(Entity):
            name = Field(String(15))

            a_rel1 = ManyToOne('A')
            a_rel2 = ManyToOne('A')

        setup_all(True)

        a1 = A(name="a1")
        a2 = A(name="a2")
        b1 = B(name="b1", a_rel1=a1, a_rel2=a2)
        b2 = B(name="b2", a_rel1=a1, a_rel2=a1)

        session.commit()
        session.expunge_all()

        a1 = A.get_by(name="a1")
        a2 = A.get_by(name="a2")
        b1 = B.get_by(name="b1")
        b2 = B.get_by(name="b2")

        assert a1 == b2.a_rel1
        assert a2 == b1.a_rel2

    def test_non_pk_target(self):
        class A(Entity):
            name = Field(String(60), unique=True)

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne('A', target_column=['id', 'name'])

        setup_all(True)

        b1 = B(name='b1', a=A(name='a1'))

        session.commit()
        session.expunge_all()

        b = B.query.one()

        assert b.a.name == 'a1'

    # currently fails. See elixir/relationships.py:create_keys
#    def test_non_pk_forward(self):
#        class B(Entity):
#            name = Field(String(60))
#            a = ManyToOne('A', target_column=['id', 'name'])
#
#        class A(Entity):
#            name = Field(String(60), unique=True)
#
#        setup_all(True)
#
#        b1 = B(name='b1', a=A(name='a1'))
#
#        session.commit()
#        session.expunge_all()
#
#        b = B.query.one()
#
#        assert b.a.name == 'a1'

    def test_belongs_to_syntax(self):
        class Person(Entity):
            has_field('name', String(30))

        class Animal(Entity):
            has_field('name', String(30))
            belongs_to('owner', of_kind='Person')

        setup_all(True)

        santa = Person(name="Santa Claus")
        rudolph = Animal(name="Rudolph", owner=santa)

        session.commit()
        session.expunge_all()

        assert "Claus" in Animal.get_by(name="Rudolph").owner.name
