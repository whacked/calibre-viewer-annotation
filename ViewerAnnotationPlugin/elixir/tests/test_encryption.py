from elixir import *
from elixir.ext.encrypted import acts_as_encrypted


def setup():
    global Person, Pet

    class Person(Entity):
        name = Field(String(50))
        password = Field(String(40))
        ssn = Field(String(40))
        pets = OneToMany('Pet')
        acts_as_encrypted(for_fields=['password', 'ssn'], with_secret='secret')

    class Pet(Entity):
        name = Field(String(50))
        codename = Field(String(50))
        acts_as_encrypted(for_fields=['codename'], with_secret='secret2')
        owner = ManyToOne('Person')


    metadata.bind = 'sqlite://'
    setup_all()


def teardown():
    cleanup_all()


class TestEncryption(object):
    def setup(self):
        create_all()

    def teardown(self):
        drop_all()
        session.close()

    def test_encryption(self):
        jonathan = Person(
            name='Jonathan LaCour',
            password='s3cr3tw0RD',
            ssn='123-45-6789'
        )
        winston = Pet(
            name='Winston',
            codename='Pug/Shih-Tzu Mix'
        )
        nelson = Pet(
            name='Nelson',
            codename='Pug'
        )
        jonathan.pets = [winston, nelson]

        session.commit()
        session.expunge_all()

        p = Person.get_by(name='Jonathan LaCour')
        assert p.password == 's3cr3tw0RD'
        assert p.ssn == '123-45-6789'
        assert p.pets[0].name == 'Winston'
        assert p.pets[0].codename == 'Pug/Shih-Tzu Mix'
        assert p.pets[1].name == 'Nelson'
        assert p.pets[1].codename == 'Pug'

        p.password = 'N3wpAzzw0rd'

        session.commit()
        session.expunge_all()

        p = Person.get_by(name='Jonathan LaCour')
        assert p.password == 'N3wpAzzw0rd'

    def test_two_consecutive_updates(self):
        jonathan = Person(
            name='Jonathan LaCour',
            password='s3cr3tw0RD',
            ssn='123-45-6789'
        )
        session.commit()
        session.expunge_all()

        p = Person.get_by(name='Jonathan LaCour')
        assert p.password == 's3cr3tw0RD'
        p.name = 'JONATHAN LACOUR'
        session.flush()

        assert p.password == 'r\\x9d\\xa8\\xb4\\x8d|\\xffp\\xf5\\x0e'

        p.name = 'Jonathan LaCour'
        session.flush()

        # check that it is not further encrypted
        assert p.password == 'r\\x9d\\xa8\\xb4\\x8d|\\xffp\\xf5\\x0e'

        session.commit()
        session.expunge_all()

        p = Person.get_by(name='Jonathan LaCour')
        assert p.password == 's3cr3tw0RD'

