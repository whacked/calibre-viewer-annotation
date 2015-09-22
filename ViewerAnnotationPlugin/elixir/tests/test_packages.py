"""
Test spreading entities accross several modules
"""

import sys

import elixir
from elixir import *

def setup():
    metadata.bind = 'sqlite://'
    for module in ('a', 'b', 'db1', 'db1.a', 'db1.b', 'db1.c', 'db2', 'db2.a'):
        sys.modules.pop('tests.%s' % module, None)


class TestPackages(object):
    def teardown(self):
        # This is an ugly workaround because when nosetest is run globally (ie
        # either on the tests directory or in the "trunk" directory, it imports
        # all modules, including a and b. Then when any other test calls
        # setup_all(), A and B are also setup, but then the other test also
        # calls cleanup_all(), so when we get here, A and B are already dead
        # and reimporting their modules does nothing because they were already
        # imported. Additionally, if I remove the __init__.py file from the
        # tests/ directory, nosetests doesn't import all modules, but does
        # import a and b (probably because they are not prefixed with "test_").
        # the result is almost the same, even if less messy.
        sys.modules.pop('tests.a', None)
        sys.modules.pop('tests.b', None)
        cleanup_all(True)

    def test_full_entity_path(self):
        from tests.a import A
        from tests.b import B

        setup_all(True)

        b1 = B(name='b1', many_a=[A(name='a1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()

        assert a in a.b.many_a

    def test_ref_to_imported_entity_using_class(self):
        from tests.a import A
        import tests.b

        class C(Entity):
            name = Field(String(30))
            a = ManyToOne(A)

        setup_all(True)

        assert 'a_id' in C.table.columns

    def test_ref_to_imported_entity_using_name(self):
        import tests.a
        import tests.b

        class C(Entity):
            name = Field(String(30))
            a = ManyToOne('A')

        setup_all(True)

        assert 'a_id' in C.table.columns

    def test_resolve_root(self):
        import tests.a
        import tests.b

        class C(Entity):
            using_options(resolve_root='tests')

            name = Field(String(30))
            a = ManyToOne('a.A')

        setup_all(True)

        assert 'a_id' in C.table.columns

    def test_relative_collection(self):
        original_collection = elixir.entities

        elixir.entities = elixir.collection.RelativeEntityCollection()

        import db1
        import db2

        setup_all(True)

        try:
            assert len(elixir.entities) == 5
        finally:
            elixir.entities = original_collection
