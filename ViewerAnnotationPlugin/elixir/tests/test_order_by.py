"""
test ordering options
"""

from elixir import *


def setup():
    global Record, Artist, Genre

    class Record(Entity):
        title = Field(String(100))
        year = Field(Integer)
        artist = ManyToOne('Artist')
        genres = ManyToMany('Genre')

        # order titles descending by year, then by title
        using_options(order_by=['-year', 'title'])

        def __str__(self):
            return "%s - %s (%d)" % (self.artist.name, self.title, self.year)

    class Artist(Entity):
        name = Field(String(30))
        records = OneToMany('Record', order_by=['year', '-title'])

    class Genre(Entity):
        name = Field(String(30))
        records = ManyToMany('Record', order_by='-title')

    metadata.bind = 'sqlite://'
    setup_all(True)

    # insert some data
    artist = Artist(name="Dream Theater")
    genre = Genre(name="Progressive metal")
    titles = (
        ("A Change Of Seasons", 1995),
        ("Awake", 1994),
        ("Falling Into Infinity", 1997),
        ("Images & Words", 1992),
        ("Metropolis Pt. 2: Scenes From A Memory", 1999),
        ("Octavarium", 2005),
        # 2005 is a mistake to make the test more interesting
        ("Six Degrees Of Inner Turbulence", 2005),
        ("Train Of Thought", 2003),
        ("When Dream And Day Unite", 1989)
    )

    for title, year in titles:
        Record(title=title, artist=artist, year=year, genres=[genre])

    session.commit()
    session.expunge_all()


def teardown():
    cleanup_all()


class TestOrderBy(object):
    def teardown(self):
        session.expunge_all()

    def test_mapper_order_by(self):
        records = Record.query.all()

        assert records[0].year == 2005
        assert records[2].year >= records[5].year
        assert records[3].year >= records[4].year
        assert records[-1].year == 1989

    def test_o2m_order_by(self):
        records = Artist.get_by(name="Dream Theater").records

        assert records[0].year == 1989
        assert records[2].year <= records[5].year
        assert records[3].year <= records[4].year
        assert records[-1].title == 'Octavarium'
        assert records[-1].year == 2005

    def test_m2m_order_by(self):
        records = Genre.get_by(name="Progressive metal").records

        assert records[0].year == 1989
        assert records[2].title >= records[5].title
        assert records[3].title >= records[4].title
        assert records[-1].year == 1995

