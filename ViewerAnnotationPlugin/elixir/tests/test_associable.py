"""
Test the associable statement generator
"""

from sqlalchemy import and_

from elixir import *
from elixir.ext.associable import associable


def setup():
    metadata.bind = 'sqlite://'

class TestOrders(object):
    def teardown(self):
        cleanup_all(True)

    def test_empty(self):
        class Foo(Entity):
            pass

        class Bar(Entity):
            pass

        is_fooable = associable(Foo)
        is_barable = associable(Bar)

        class Quux(Entity):
            is_fooable()
            is_barable()

        setup_all(True)

    def test_basic(self):
        class Address(Entity):
            street = Field(String(130))
            city = Field(String(100))
            using_options(shortnames=True)

        class Comment(Entity):
            id = Field(Integer, primary_key=True)
            name = Field(String(200))
            text = Field(Text)

        is_addressable = associable(Address, 'addresses')
        is_commentable = associable(Comment, 'comments')

        class Person(Entity):
            id = Field(Integer, primary_key=True)
            name = Field(String(50))
            orders = OneToMany('Order')
            using_options(shortnames=True)
            is_addressable()
            is_commentable()

        class Order(Entity):
            order_num = Field(Integer, primary_key=True)
            item_count = Field(Integer)
            person = ManyToOne('Person')
            using_options(shortnames=True)
            is_addressable('address', uselist=False)

        setup_all(True)

        home = Address(street='123 Elm St.', city='Spooksville')
        work = Address(street='243 Hooper st.', city='Cupertino')
        user = Person(name='Jane Doe')
        user.addresses.append(home)
        user.addresses.append(work)

        neworder = Order(item_count=4)
        neworder.address = home
        user.orders.append(neworder)

        session.commit()
        session.expunge_all()

        # Queries using the added helpers
        people = Person.select_by_addresses(city='Cupertino')
        assert len(people) == 1

        streets = [adr.street for adr in people[0].addresses]
        assert '243 Hooper st.' in streets
        assert '123 Elm St.' in streets

        people = Person.select_addresses(and_(Address.street=='132 Elm St',
                                              Address.city=='Smallville'))
        assert len(people) == 0

    def test_with_forward_ref(self):
        class Checkout(Entity):
            by = ManyToOne('Villian', ondelete='cascade')
            stamp = Field(DateTime)

        can_checkout = associable(Checkout, 'checked_out')

        class Article(Entity):
            title = Field(String(200))
            content = Field(Text)
            can_checkout('checked_out_by', uselist=False)
            using_options(tablename='article')

        class Villian(Entity):
            name = Field(String(50))
            using_options(tablename='villian')

        setup_all(True)

        art = Article(title='Hope Soars')

        session.commit()
        session.expunge_all()
