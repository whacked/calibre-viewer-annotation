"""
Test collections
"""

from sqlalchemy import Table
from elixir import *
import elixir


def setup():
    metadata.bind = 'sqlite://'

def teardown():
    cleanup_all()

class TestCollections(object):
    def teardown(self):
        cleanup_all()

    def test_no_collection(self):
        class Person(Entity):
            name = Field(String(30))
            using_options(tablename='person', collection=None)

        # global collection should be empty
        assert not elixir.entities

        setup_entities([Person])

        # check the table was correctly setup
        assert isinstance(metadata.tables['person'], Table)

    def test_several_collections(self):
        collection1 = EntityCollection()
        collection2 = EntityCollection()

        class A(Entity):
            name = Field(String(30))
            using_options(collection=collection1, tablename='a')

        class B(Entity):
            name = Field(String(30))
            using_options(collection=collection2, tablename='b')

        # global collection should be empty
        assert A not in elixir.entities
        assert B not in elixir.entities

        assert A in collection1
        assert B in collection2

        setup_entities(collection1)
        setup_entities(collection2)

        assert isinstance(metadata.tables['a'], Table)
        assert isinstance(metadata.tables['b'], Table)

    def test_getattr(self):
        collection = EntityCollection()

        class A(Entity):
            name = Field(String(30))
            using_options(collection=collection)

        assert collection.A == A

    def test_setup_after_cleanup(self):
        class A(Entity):
            name = Field(String(30))
            using_options(tablename='a')

        setup_all()

        assert isinstance(metadata.tables['a'], Table)

        cleanup_all()

        assert 'a' not in metadata.tables

        # setup_all wouldn't work since the entities list is now empty
        setup_entities([A])

        assert isinstance(metadata.tables['a'], Table)

        # cleanup manually
        cleanup_entities([A])

        # metadata is not in metadatas anymore (removed by cleanup_all) and not
        # added back by setup_entities (maybe we should?)
        metadata.clear()


