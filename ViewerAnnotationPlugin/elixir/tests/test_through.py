"""
    test has_*(..., through=...) syntax
"""

from elixir import *
from datetime import datetime

def setup():
    metadata.bind = 'sqlite://'


class TestThrough(object):
    def teardown(self):
        cleanup_all(True)

    def test_rel_through(self):
        # converted from
        # http://www.sqlalchemy.org/docs/05/reference/ext/associationproxy.html
        class User(Entity):
            has_field('name', String(64))
            has_many('user_keywords', of_kind='UserKeyword')
            has_many('keywords', through='user_keywords', via='keyword',
                     creator=lambda kw: UserKeyword(keyword=kw))

        class Keyword(Entity):
            has_field('keyword', String(64))

            def __init__(self, keyword):
                self.keyword = keyword

        class UserKeyword(Entity):
            belongs_to('user', of_kind='User', primary_key=True)
            belongs_to('keyword', of_kind='Keyword', primary_key=True)

            # add some auditing columns
            has_field('updated_at', DateTime, default=datetime.now)

        setup_all(True)

        user = User(name='log')
        keywords = [Keyword('its_big'), Keyword('its_heavy'),
                    Keyword('its_wood')]
        for kw in keywords:
            user.keywords.append(kw)

        assert user.keywords == keywords

    def test_rel_through_to_value_list(self):
        class User(Entity):
            has_field('name', String(64))
            has_and_belongs_to_many('kw', of_kind='Keyword')
            has_many('keywords', through='kw', via='keyword')

        class Keyword(Entity):
            has_field('keyword', String(64))

            def __init__(self, keyword):
                self.keyword = keyword

        setup_all(True)

        user = User(name='jek')
        user.kw.append(Keyword('cheese inspector'))

        assert user.kw[0].keyword == 'cheese inspector'
        assert user.keywords == ['cheese inspector']

        user.keywords.append('snack ninja')

        assert user.keywords == ['cheese inspector', 'snack ninja']
        assert len(user.kw) == 2

    def test_field_through(self):
        class User(Entity):
            has_field('name', String(64))
            belongs_to('kw', of_kind='Keyword')
            has_field('keyword', through='kw')
            has_field('kw2', through='kw', attribute='keyword')

        class Keyword(Entity):
            has_field('keyword', String(64))

            def __init__(self, keyword):
                self.keyword = keyword

        setup_all(True)

        user = User(name='jek')
        user.kw = Keyword('cheese inspector')

        assert user.kw.keyword == 'cheese inspector'
        assert user.keyword == 'cheese inspector'

        user.keyword = 'snack ninja'

        assert user.kw.keyword == 'snack ninja'
        assert user.kw2 == 'snack ninja'

