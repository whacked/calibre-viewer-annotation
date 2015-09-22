from elixir import *
from elixir.ext.perform_ddl import perform_ddl, preload_data


def setup():
    metadata.bind = "sqlite://"


class TestPerformDDL(object):
    def teardown(self):
        cleanup_all(True)

    def test_one(self):
        class Movie(Entity):
            title = Field(Unicode(30), primary_key=True)
            year = Field(Integer)

            perform_ddl('after-create',
                        "insert into %(fullname)s values ('Alien', 1979)")

        setup_all(True)
        assert Movie.query.count() == 1

    def test_several(self):
        class Movie(Entity):
            title = Field(Unicode(30), primary_key=True)
            year = Field(Integer)

            perform_ddl('after-create',
                        ["insert into %(fullname)s values ('Alien', 1979)",
                         "insert into %(fullname)s " +
                            "values ('Star Wars', 1977)"])
            perform_ddl('after-create',
                        "insert into %(fullname)s (year, title) " +
                        "values (1982, 'Blade Runner')")

        setup_all(True)
        assert Movie.query.count() == 3

class TestPreloadData(object):
    def teardown(self):
        cleanup_all(True)

    def test_several(self):
        class Movie(Entity):
            title = Field(Unicode(30), primary_key=True)
            year = Field(Integer)

            preload_data(('title', 'year'),
                         [(u'Alien', 1979), (u'Star Wars', 1977)])
            preload_data(('year', 'title'),
                         [(1982, u'Blade Runner')])
            preload_data(data=[(u'Batman', 1966)])

        setup_all(True)
        assert Movie.query.count() == 4

