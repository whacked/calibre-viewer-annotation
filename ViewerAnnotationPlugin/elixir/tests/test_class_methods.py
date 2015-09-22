"""
    simple test case
"""

from elixir import *

#-----------

class TestOldMethods(object):
    def setup(self):
        metadata.bind = 'sqlite://'

    def teardown(self):
        cleanup_all()

    def test_get(self):
        class A(Entity):
            name = Field(String(32))

        setup_all(True)

        a1 = A(name="a1")

        session.commit()
        session.expunge_all()

        assert A.get(1).name == "a1"

