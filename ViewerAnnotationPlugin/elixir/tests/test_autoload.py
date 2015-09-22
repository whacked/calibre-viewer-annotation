"""
test autoloaded entities
"""

from sqlalchemy import Table, Column, ForeignKey
from elixir import *
import elixir

def setup_entity_raise(cls):
    try:
        setup_entities([cls])
    except Exception, e:
        pass
    else:
        assert False, "Exception did not occur setting up %s" % cls.__name__

# ------

def setup():
    elixir.options_defaults.update(dict(autoload=True, shortnames=True))

def teardown():
    elixir.options_defaults.update(dict(autoload=False, shortnames=False))

# -----------

class TestAutoload(object):
    def setup(self):
        metadata.bind = 'sqlite://'

    def teardown(self):
        cleanup_all(True)

    def test_simple(self):
        conn = metadata.bind.connect()
        conn.execute("CREATE TABLE a ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name VARCHAR(32))")
        conn.close()

        class A(Entity):
            pass

        setup_all()

        a1 = A(name="a1")
        a2 = A(name="a2")

        session.commit()
        session.expunge_all()

        a1 = A.get_by(name="a1")
        a2 = A.get_by(name="a2")
        assert a1.name == 'a1'
        assert a2.name == 'a2'

    def test_fk_auto_join_sa(self):
        # SQLAlchemy produces the join in this case
        person_table = Table('person', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(32)))

        animal_table = Table('animal', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(30)),
            Column('owner_id', Integer, ForeignKey('person.id')))

        metadata.create_all()
        metadata.clear()

        class Person(Entity):
            pets = OneToMany('Animal')

        class Animal(Entity):
            owner = ManyToOne('Person')

        setup_all()

        snowball = Animal(name="Snowball")
        snowball2 = Animal(name="Snowball II")
        slh = Animal(name="Santa's Little Helper")
        homer = Person(name="Homer", pets=[slh, snowball])
        lisa = Person(name="Lisa", pets=[snowball2])

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        lisa = Person.get_by(name="Lisa")
        slh = Animal.get_by(name="Santa's Little Helper")

        assert len(homer.pets) == 2
        assert homer == slh.owner
        assert lisa.pets[0].name == "Snowball II"

    def test_fk_auto_join_colname(self):
        person_table = Table('person', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(32)))

        animal_table = Table('animal', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(30)),
            Column('owner_id', Integer, ForeignKey('person.id')),
            Column('feeder_id', Integer, ForeignKey('person.id')))

        metadata.create_all()
        metadata.clear()

        class Person(Entity):
            pets = OneToMany('Animal', inverse='owner')
            animals = OneToMany('Animal', inverse='feeder')

        class Animal(Entity):
            owner = ManyToOne('Person', colname='owner_id')
            feeder = ManyToOne('Person', colname='feeder_id')

        setup_all()

        snowball = Animal(name="Snowball II")
        slh = Animal(name="Santa's Little Helper")
        homer = Person(name="Homer", animals=[snowball, slh], pets=[slh])
        lisa = Person(name="Lisa", pets=[snowball])

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        lisa = Person.get_by(name="Lisa")
        slh = Animal.get_by(name="Santa's Little Helper")

        assert len(homer.animals) == 2
        assert homer == lisa.pets[0].feeder
        assert homer == slh.owner

    def test_selfref(self):
        person_table = Table('person', metadata,
            Column('id', Integer, primary_key=True),
            Column('father_id', Integer, ForeignKey('person.id')),
            Column('name', String(32)))

        metadata.create_all()
        metadata.clear()

        class Person(Entity):
            father = ManyToOne('Person')
            children = OneToMany('Person')

        setup_all()

        grampa = Person(name="Abe")
        homer = Person(name="Homer")
        bart = Person(name="Bart")
        lisa = Person(name="Lisa")

        grampa.children.append(homer)
        homer.children.append(bart)
        lisa.father = homer

        session.commit()
        session.expunge_all()

        p = Person.get_by(name="Homer")

        assert p in p.father.children
        assert p.father.name == "Abe"
        assert p.father is Person.get_by(name="Abe")
        assert p is Person.get_by(name="Lisa").father

    def test_m2m(self):
        person_table = Table('person', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(32)))

        category_table = Table('category', metadata,
            Column('name', String(30), primary_key=True))

        person_category_table = Table('person_category', metadata,
            Column('person_id', Integer, ForeignKey('person.id')),
            Column('category_name', String(30), ForeignKey('category.name')))

        metadata.create_all()
        metadata.clear()

        class Person(Entity):
            categories = ManyToMany('Category',
                                    tablename='person_category')

        class Category(Entity):
            persons = ManyToMany('Person',
                                 tablename='person_category')

        setup_all()

        stupid = Category(name="Stupid")
        simpson = Category(name="Simpson")
        old = Category(name="Old")

        grampa = Person(name="Abe", categories=[simpson, old])
        homer = Person(name="Homer", categories=[simpson, stupid])
        bart = Person(name="Bart")
        lisa = Person(name="Lisa")

        simpson.persons.extend([bart, lisa])

        session.commit()
        session.expunge_all()

        c = Category.get_by(name="Simpson")
        grampa = Person.get_by(name="Abe")

        assert len(c.persons) == 4
        assert c in grampa.categories

     # currently fails. See elixir/relationships.py:_get_join_clauses
#    def test_m2m_extra_fk(self):
#        person_table = Table('person', metadata,
#            Column('id', Integer, primary_key=True),
#            Column('name', String(32), unique=True))
#
#        category_table = Table('category', metadata,
#            Column('name', String(30), primary_key=True))
#
#        person_category_table = Table('person_category', metadata,
#            Column('person_id', Integer, ForeignKey('person.id')),
#            Column('category_name', String(30), ForeignKey('category.name')),
#            Column('person_name', String(32), ForeignKey('person.name')))
#
#        metadata.create_all()
#        metadata.clear()
#
#        class Person(Entity):
#            categories = ManyToMany('Category',
#                                    tablename='person_category',
#                                    local_colname='person_id')
#
#        class Category(Entity):
#            persons = ManyToMany('Person',
#                                 tablename='person_category')
#
#        setup_all()
#
#        stupid = Category(name="Stupid")
#        simpson = Category(name="Simpson")
#        old = Category(name="Old")
#
#        grampa = Person(name="Abe", categories=[simpson, old])
#        homer = Person(name="Homer", categories=[simpson, stupid])
#        bart = Person(name="Bart")
#        lisa = Person(name="Lisa")
#
#        simpson.persons.extend([bart, lisa])
#
#        session.commit()
#        session.expunge_all()
#
#        c = Category.get_by(name="Simpson")
#        grampa = Person.get_by(name="Abe")
#
#        assert len(c.persons) == 4
#        assert c in grampa.categories

    def test_m2m_selfref(self):
        person_table = Table('person', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(32)))

        person_person_table = Table('person_person', metadata,
            Column('person_id1', Integer, ForeignKey('person.id')),
            Column('person_id2', Integer, ForeignKey('person.id')))

        metadata.create_all()
        metadata.clear()

        class Person(Entity):
            appreciate = ManyToMany('Person',
                                    tablename='person_person',
                                    local_colname='person_id1')
            isappreciatedby = ManyToMany('Person',
                                         tablename='person_person',
                                         # this one is not necessary
                                         local_colname='person_id2')

        setup_all()

        barney = Person(name="Barney")
        homer = Person(name="Homer", appreciate=[barney])

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        barney = Person.get_by(name="Barney")

        assert barney in homer.appreciate
        assert homer in barney.isappreciatedby

    # ----------------
    # overrides tests
    # ----------------
    def _create_table_a(self):
        a_table = Table('a', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(32)))

        metadata.create_all()
        metadata.clear()

    def test_override_pk_fails(self):
        self._create_table_a()

        class A(Entity):
            id = Field(Integer, primary_key=True)

        setup_entity_raise(A)

    def test_override_non_pk_fails(self):
        self._create_table_a()

        class A(Entity):
            name = Field(String(30))

        setup_entity_raise(A)

    def test_override_pk(self):
        self._create_table_a()

        class A(Entity):
            using_options(allowcoloverride=True)

            id = Field(Integer, primary_key=True)

        setup_entities([A])

    def test_override_non_pk(self):
        self._create_table_a()

        class A(Entity):
            using_options(allowcoloverride=True)

            name = Field(String(30))

        setup_entities([A])
        assert isinstance(A.table.columns['name'].type, String)

    # ---------------

    def test_nopk(self):
        table = Table('a', metadata,
            Column('id', Integer),
            Column('name', String(32)))

        metadata.create_all()
        metadata.clear()

        class A(Entity):
            using_mapper_options(primary_key=['id'])

        setup_all()

        a1 = A(id=1, name="a1")

        session.commit()
        session.expunge_all()

        res = A.query.all()

        assert len(res) == 1
        assert res[0].name == "a1"

    def test_inheritance(self):
        table = Table('father', metadata,
            Column('id', Integer, primary_key=True),
            Column('row_type', elixir.options.POLYMORPHIC_COL_TYPE))

        metadata.create_all()
        metadata.clear()

        class Father(Entity):
            pass

        class Son(Father):
            pass

        setup_all()

    def test_autoload_mixed(self):
        # mixed autoloaded entity with a non autoloaded one
        conn = metadata.bind.connect()
        conn.execute("CREATE TABLE user ("
                     "user_id INTEGER PRIMARY KEY AUTOINCREMENT)")
        conn.close()

        class User(Entity):
            using_options(tablename='user', autoload=True)

        class Item(Entity):
            using_options(autoload=False)

            owner = ManyToOne('User')

        setup_all(True)

        colname = Item.table.c['owner_user_id'].foreign_keys[0].column.name
        assert colname == 'user_id'

