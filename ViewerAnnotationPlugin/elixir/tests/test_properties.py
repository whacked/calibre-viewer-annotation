"""
test special properties (eg. column_property, ...)
"""

from sqlalchemy import select, func
from sqlalchemy.orm import column_property
from elixir import *

def setup():
    metadata.bind = 'sqlite://'


class TestSpecialProperties(object):
    def teardown(self):
        cleanup_all(True)

    def test_lifecycle(self):
        class A(Entity):
            name = Field(String(20))

        assert isinstance(A.name, Field)

        setup_all()

        assert not isinstance(A.name, Field)

    def test_generic_property(self):
        class Tag(Entity):
            score1 = Field(Float)
            score2 = Field(Float)

            score = GenericProperty(
                         lambda c: column_property(
                             (c.score1 * c.score2).label('score')))
        setup_all(True)

        t1 = Tag(score1=5.0, score2=3.0)
        t2 = Tag(score1=10.0, score2=2.0)

        session.commit()
        session.expunge_all()

        for tag in Tag.query.all():
            assert tag.score == tag.score1 * tag.score2

    def test_column_property(self):
        class Tag(Entity):
            score1 = Field(Float)
            score2 = Field(Float)

            score = ColumnProperty(lambda c: c.score1 * c.score2)

        setup_all(True)

        t1 = Tag(score1=5.0, score2=3.0)
        t2 = Tag(score1=10.0, score2=2.0)

        session.commit()
        session.expunge_all()

        for tag in Tag.query.all():
            assert tag.score == tag.score1 * tag.score2

    def test_column_property_eagerload_and_reuse(self):
        class Tag(Entity):
            score1 = Field(Float)
            score2 = Field(Float)

            user = ManyToOne('User')

            score = ColumnProperty(lambda c: c.score1 * c.score2)

        class User(Entity):
            name = Field(String(16))
            category = ManyToOne('Category')
            tags = OneToMany('Tag', lazy=False)
            score = ColumnProperty(lambda c:
                                   select([func.sum(Tag.score)],
                                          Tag.user_id == c.id).as_scalar())

        class Category(Entity):
            name = Field(String(16))
            users = OneToMany('User', lazy=False)

            score = ColumnProperty(lambda c:
                                   select([func.avg(User.score)],
                                          User.category_id == c.id
                                         ).as_scalar())
        setup_all(True)

        u1 = User(name='joe', tags=[Tag(score1=5.0, score2=3.0),
                                    Tag(score1=55.0, score2=1.0)])

        u2 = User(name='bar', tags=[Tag(score1=5.0, score2=4.0),
                                    Tag(score1=50.0, score2=1.0),
                                    Tag(score1=15.0, score2=2.0)])

        c1 = Category(name='dummy', users=[u1, u2])

        session.commit()
        session.expunge_all()

        category = Category.query.one()
        assert category.score == 85
        for user in category.users:
            assert user.score == sum([tag.score for tag in user.tags])
            for tag in user.tags:
                assert tag.score == tag.score1 * tag.score2

    def test_has_property(self):
        class Tag(Entity):
            has_field('score1', Float)
            has_field('score2', Float)
            has_property('score',
                         lambda c: column_property(
                             (c.score1 * c.score2).label('score')))

        setup_all(True)

        t1 = Tag(score1=5.0, score2=3.0)
        t1 = Tag(score1=10.0, score2=2.0)

        session.commit()
        session.expunge_all()

        for tag in Tag.query.all():
            assert tag.score == tag.score1 * tag.score2

    def test_deferred(self):
        class A(Entity):
            name = Field(String(20))
            stuff = Field(Text, deferred=True)

        setup_all(True)

        A(name='foo')
        session.commit()

    def test_synonym(self):
        class Person(Entity):
            name = Field(String(50), required=True)
            _email = Field(String(20), colname='email', synonym='email')

            def _set_email(self, email):
                Person.email_values.append(email)
                self._email = email

            def _get_email(self):
                Person.email_gets += 1
                return self._email

            email = property(_get_email, _set_email)
            email_values = []
            email_gets = 0

        setup_all(True)

        mrx = Person(name='Mr. X', email='x@y.com')

        assert mrx.email == 'x@y.com'
        assert Person.email_gets == 1

        mrx.email = "x@z.com"

        assert Person.email_values == ['x@y.com', 'x@z.com']

        session.commit()
        session.expunge_all()

        # test the synonym itself (ie querying)
        p = Person.get_by(email='x@z.com')

        assert p.name == 'Mr. X'

    def test_synonym_class(self):
        class Person(Entity):
            name = Field(String(30))
            primary_email = Field(String(100))
            email_address = Synonym('primary_email')

        class User(Person):
            user_name = Synonym('name')
            password = Field(String(20))

        setup_all(True)

        alexandre = Person(
            name = u'Alexandre da Silva',
            email_address = u'x@y.com'
        )
        johann = User(
            name = 'Johann Felipe Voigt',
            email_address = 'y@z.com',
            password = 'unencrypted'
        )

        session.commit(); session.expunge_all()

        p = Person.get_by(name='Alexandre da Silva')
        assert p.primary_email == 'x@y.com'

        u = User.get_by(user_name='Johann Felipe Voigt')
        assert u.email_address == 'y@z.com'

        u.email_address = 'new@z.com'
        session.commit(); session.expunge_all()

        p = Person.get_by(name='Johann Felipe Voigt')
        assert p.primary_email == 'new@z.com'

    def test_setattr(self):
        class A(Entity):
            pass

        A.name = Field(String(30))

        setup_all(True)

        a1 = A(name='a1')

        session.commit(); session.expunge_all()

        a = A.query.one()

        assert a.name == 'a1'

