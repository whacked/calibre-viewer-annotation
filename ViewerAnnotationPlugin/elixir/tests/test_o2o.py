from elixir import *

def setup():
    metadata.bind = "sqlite://"

class TestOneToOne(object):
    def teardown(self):
        cleanup_all(True)

    def test_simple(self):
        class A(Entity):
            name = Field(String(60))
            b = OneToOne('B')

        class B(Entity):
            name = Field(String(60))
            a = ManyToOne('A')

        setup_all(True)

        b1 = B(name='b1', a=A(name='a1'))

        session.commit()
        session.expunge_all()

        b = B.query.one()
        a = b.a

        assert b == a.b


