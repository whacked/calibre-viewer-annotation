import time
from datetime import datetime

from elixir import *
from elixir.ext.versioned import acts_as_versioned


class TestVersioning(object):
    def teardown(self):
        cleanup_all(True)

    def test_versioning(self):
        nextOneValue = {'value': 0}

        def nextOne():
            nextOneValue['value'] += 2
            return nextOneValue['value']

        class Director(Entity):
            name = Field(String(60))
            movies = OneToMany('Movie', inverse='director')
            using_options(tablename='directors')

        class Movie(Entity):
            id = Field(Integer, primary_key=True)
            title = Field(String(60), primary_key=True)
            description = Field(String(512))
            releasedate = Field(DateTime)
            ignoreme = Field(Integer, default=0)
            autoupd = Field(Integer, default=nextOne, onupdate=nextOne)
            director = ManyToOne('Director', inverse='movies')
            actors = ManyToMany('Actor', inverse='movies',
                                tablename='movie_casting')
            using_options(tablename='movies')
            acts_as_versioned(ignore=['ignoreme', 'autoupd'],
                              column_names=['version_no', 'timestamp_value'])

        class Actor(Entity):
            name = Field(String(60))
            movies = ManyToMany('Movie', inverse='actors',
                                tablename='movie_casting')
            using_options(tablename='actors')

        metadata.bind = 'sqlite://'
        setup_all(True)

        gilliam = Director(name='Terry Gilliam')
        monkeys = Movie(id=1, title='12 Monkeys',
                        description='draft description', director=gilliam)
        bruce = Actor(name='Bruce Willis', movies=[monkeys])
        session.commit(); session.expunge_all()

        time.sleep(1)
        after_create = datetime.now()
        time.sleep(1)

        movie = Movie.get_by(title='12 Monkeys')
        assert movie.version_no == 1
        assert movie.title == '12 Monkeys'
        assert movie.director.name == 'Terry Gilliam'
        assert movie.autoupd == 2, movie.autoupd
        movie.description = 'description two'
        session.commit(); session.expunge_all()

        time.sleep(1)
        after_update_one = datetime.now()
        time.sleep(1)

        movie = Movie.get_by(title='12 Monkeys')
        movie.description = 'description three'
        session.commit(); session.expunge_all()

        # Edit the ignored field, this shouldn't change the version
        monkeys = Movie.get_by(title='12 Monkeys')
        monkeys.ignoreme = 1
        session.commit(); session.expunge_all()

        time.sleep(1)
        after_update_two = datetime.now()
        time.sleep(1)

        movie = Movie.get_by(title='12 Monkeys')
        assert movie.autoupd == 8, movie.autoupd
        oldest_version = movie.get_as_of(after_create)
        middle_version = movie.get_as_of(after_update_one)
        latest_version = movie.get_as_of(after_update_two)

        initial_timestamp = oldest_version.timestamp_value

        assert oldest_version.version_no == 1
        assert oldest_version.description == 'draft description'
        assert oldest_version.ignoreme == 0
        assert oldest_version.autoupd is not None
        assert oldest_version.autoupd > 0

        assert middle_version.version_no == 2
        assert middle_version.description == 'description two'
        assert middle_version.autoupd > oldest_version.autoupd

        assert latest_version.version_no == 3, \
               'version=%i' % latest_version.version_no
        assert latest_version.description == 'description three'
        assert latest_version.ignoreme == 1
        assert latest_version.autoupd > middle_version.autoupd

        differences = latest_version.compare_with(oldest_version)
        assert differences['description'] == \
               ('description three', 'draft description')

        assert len(movie.versions) == 3
        assert movie.versions[0] == oldest_version
        assert movie.versions[1] == middle_version
        assert [v.version_no for v in movie.versions] == [1, 2, 3]

        movie.description = 'description four'

        movie.revert_to(2)
        session.commit(); session.expunge_all()

        movie = Movie.get_by(title='12 Monkeys')
        assert movie.version_no == 2, \
               "version=%i, should be 2" % movie.version_no
        assert movie.description == 'description two', movie.description

        movie.description = "description 3"
        session.commit(); session.expunge_all()

        movie = Movie.get_by(title='12 Monkeys')
        movie.description = "description 4"
        session.commit(); session.expunge_all()

        movie = Movie.get_by(title='12 Monkeys')
        assert movie.version_no == 4
        movie.revert_to(movie.versions[-2])
        movie.description = "description 5"
        session.commit(); session.expunge_all()

        movie = Movie.get_by(title='12 Monkeys')
        assert movie.version_no == 4
        assert movie.versions[-2].description == "description 3"

