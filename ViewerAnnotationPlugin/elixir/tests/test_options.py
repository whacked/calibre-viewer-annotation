"""
test options
"""

from sqlalchemy import UniqueConstraint, create_engine, Column
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exceptions import SQLError, ConcurrentModificationError
from elixir import *

class TestOptions(object):
    def setup(self):
        metadata.bind = 'sqlite://'

    def teardown(self):
        cleanup_all(True)

    # this test is a rip-off SQLAlchemy's activemapper's update test
    def test_version_id_col(self):
        class Person(Entity):
            name = Field(String(30))

            using_options(version_id_col=True)

        setup_all(True)

        p1 = Person(name='Daniel')
        session.commit()
        session.expunge_all()

        person = Person.query.first()
        person.name = 'Gaetan'
        session.commit()
        assert person.row_version == 2
        session.expunge_all()

        person = Person.query.first()
        person.name = 'Jonathan'
        session.commit()
        assert person.row_version == 3
        session.expunge_all()

        # check that a concurrent modification raises exception
        p1 = Person.query.first()
        s2 = sessionmaker()()
        p2 = s2.query(Person).first()
        p1.name = "Daniel"
        p2.name = "Gaetan"
        s2.commit()
        try:
            session.commit()
            assert False
        except ConcurrentModificationError:
            pass
        s2.close()

    def test_allowcoloverride_false(self):
        class MyEntity(Entity):
            name = Field(String(30))

        setup_all(True)

        try:
            MyEntity._descriptor.add_column(Column('name', String(30)))
            assert False
        except Exception:
            pass

    def test_allowcoloverride_true(self):
        class MyEntity(Entity):
            name = Field(String(30))
            using_options(allowcoloverride=True)

        setup_all()

        # Note that this test is bogus as you cannot just change a column this
        # way since the mapper is already constructed at this point and will
        # use the old column!!! This test is only meant as a way to check no
        # exception is raised.
        #TODO: provide a proper test (using autoloaded tables)
        MyEntity._descriptor.add_column(Column('name', String(30),
                                               default='test'))

    def test_tablename_func(self):
        import re

        def camel_to_underscore(entity):
            return re.sub(r'(.+?)([A-Z])+?', r'\1_\2', entity.__name__).lower()

        options_defaults['tablename'] = camel_to_underscore

        class MyEntity(Entity):
            name = Field(String(30))

        class MySuperTestEntity(Entity):
            name = Field(String(30))

        setup_all(True)

        assert MyEntity.table.name == 'my_entity'
        assert MySuperTestEntity.table.name == 'my_super_test_entity'

        options_defaults['tablename'] = None


class TestSessionOptions(object):
    def setup(self):
        metadata.bind = None

    def teardown(self):
        cleanup_all()

    def test_manual_session(self):
        engine = create_engine('sqlite://')

        class Person(Entity):
            using_options(session=None)
            name = Field(String(30))

        setup_all()
        create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        homer = Person(name="Homer")
        bart = Person(name="Bart")

        session.add(homer)
        session.add(bart)
        session.commit()

        bart.delete()
        session.commit()

        assert session.query(Person).filter_by(name='Homer').one() is \
               homer
        assert session.query(Person).count() == 1

    def test_scoped_session(self):
        engine = create_engine('sqlite://')
        Session = scoped_session(sessionmaker(bind=engine))

        class Person(Entity):
            using_options(session=Session)
            name = Field(String(30))

        setup_all()
        create_all(engine)

        homer = Person(name="Homer")
        bart = Person(name="Bart")
        Session.commit()

        assert Person.query.session is Session()
        assert Person.query.filter_by(name='Homer').one() is homer

    def test_scoped_session_no_save_on_init(self):
        metadata.bind = 'sqlite://'

        class Person(Entity):
            using_mapper_options(save_on_init=False)
            name = Field(String(30))

        setup_all(True)

        homer = Person(name="Homer")
        bart = Person(name="Bart")
        assert homer not in session
        assert bart not in session
        session.add(homer)
        session.add(bart)
        session.commit()

        assert Person.query.filter_by(name='Homer').one() is homer

    def test_global_scoped_session(self):
        global __session__

        engine = create_engine('sqlite://')
        session = scoped_session(sessionmaker(bind=engine))
        __session__ = session

        class Person(Entity):
            name = Field(String(30))

        setup_all()
        create_all(engine)

        homer = Person(name="Homer")
        bart = Person(name="Bart")
        session.commit()

        assert Person.query.session is session()
        assert Person.query.filter_by(name='Homer').one() is homer

        del __session__


class TestTableOptions(object):
    def setup(self):
        metadata.bind = 'sqlite://'

    def teardown(self):
        cleanup_all(True)

    def test_unique_constraint(self):
        class Person(Entity):
            firstname = Field(String(30))
            surname = Field(String(30))

            using_table_options(UniqueConstraint('firstname', 'surname'))

        setup_all(True)

        homer = Person(firstname="Homer", surname='Simpson')
        bart = Person(firstname="Bart", surname='Simpson')

        session.commit()

        homer2 = Person(firstname="Homer", surname='Simpson')

        try:
            session.commit()
            assert False
        except SQLError:
            pass

    def test_several_statements(self):
        class A(Entity):
            name1 = Field(String(30))
            name2 = Field(String(30))
            name3 = Field(String(30))
            using_table_options(UniqueConstraint('name1', 'name2'))
            using_table_options(UniqueConstraint('name2', 'name3'))

        setup_all(True)

        a000 = A(name1='0', name2='0', name3='0')
        a010 = A(name1='0', name2='1', name3='0')
        session.commit()

        a001 = A(name1='0', name2='0', name3='1')
        try:
            session.commit()
            assert False
        except SQLError:
            session.close()

        a100 = A(name1='1', name2='0', name3='0')
        try:
            session.commit()
            assert False
        except SQLError:
            session.close()

    def test_unique_constraint_many_to_one(self):
        class Author(Entity):
            name = Field(String(50))

        class Book(Entity):
            title = Field(String(200), required=True)
            author = ManyToOne("Author")

            using_table_options(UniqueConstraint("title", "author_id"))

        setup_all(True)

        tolkien = Author(name="J. R. R. Tolkien")
        lotr = Book(title="The Lord of the Rings", author=tolkien)
        hobbit = Book(title="The Hobbit", author=tolkien)

        session.commit()

        tolkien2 = Author(name="Tolkien")
        hobbit2 = Book(title="The Hobbit", author=tolkien2)

        session.commit()

        hobbit3 = Book(title="The Hobbit", author=tolkien)

        raised = False
        try:
            session.commit()
        except SQLError:
            raised = True

        assert raised

