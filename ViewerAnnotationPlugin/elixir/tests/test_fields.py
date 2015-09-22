"""
test the different syntaxes to define fields
"""

from elixir import *

def setup():
    metadata.bind = 'sqlite://'

class TestFields(object):
    def teardown(self):
        cleanup_all(True)

    def test_attr_syntax(self):
        class Person(Entity):
            firstname = Field(String(30))
            surname = Field(String(30))

        setup_all(True)

        homer = Person(firstname="Homer", surname="Simpson")
        bart = Person(firstname="Bart", surname="Simpson")

        session.commit()
        session.expunge_all()

        p = Person.get_by(firstname="Homer")

        assert p.surname == 'Simpson'

    def test_has_field(self):
        class Person(Entity):
            has_field('firstname', String(30))
            has_field('surname', String(30))

        setup_all(True)

        homer = Person(firstname="Homer", surname="Simpson")
        bart = Person(firstname="Bart", surname="Simpson")

        session.commit()
        session.expunge_all()

        p = Person.get_by(firstname="Homer")

        assert p.surname == 'Simpson'
