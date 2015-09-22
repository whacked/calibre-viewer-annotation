"""
test inheritance with abstract entities
"""

import re

from elixir import *
import elixir

def camel_to_underscore(entity):
    return re.sub(r'(.+?)([A-Z])+?', r'\1_\2', entity.__name__).lower()

def setup():
    # this is an ugly hack because globally defined entities of other tests
    # (a.*, b.*, db1.* and db2.*) leak into this one because of nosetests
    # habit of importing all modules before running the first test.
    # test_abstract is usually the first test to be run, so it gets all the
    # crap.
    cleanup_all()

    metadata.bind = 'sqlite://'
    elixir.options_defaults['shortnames'] = True

def teardown():
    elixir.options_defaults['shortnames'] = False

class TestAbstractInheritance(object):
    def teardown(self):
        cleanup_all(True)

    def test_abstract_alone(self):
        class AbstractPerson(Entity):
            using_options(abstract=True)

            firstname = Field(String(30))
            lastname = Field(String(30))

        setup_all(True)

        assert not hasattr(AbstractPerson, 'table')

    def test_inheritance(self):
        class AbstractPerson(Entity):
            using_options(abstract=True)
            using_options_defaults(tablename=camel_to_underscore)

            firstname = Field(String(30))
            lastname = Field(String(30))

        class AbstractEmployee(AbstractPerson):
            using_options(abstract=True)
            using_options_defaults(identity=camel_to_underscore)

            corporation = Field(String(30))

        class ConcreteEmployee(AbstractEmployee):
            service = Field(String(30))

        class ConcreteCitizen(AbstractPerson):
            country = Field(String(30))

        setup_all(True)

        assert not hasattr(AbstractPerson, 'table')
        assert not hasattr(AbstractEmployee, 'table')
        assert hasattr(ConcreteEmployee, 'table')
        assert hasattr(ConcreteCitizen, 'table')
        assert ConcreteEmployee.table.name == 'concrete_employee'
        assert ConcreteCitizen.table.name == 'concrete_citizen'

        assert 'firstname' in ConcreteEmployee.table.columns
        assert 'lastname' in ConcreteEmployee.table.columns
        assert 'corporation' in ConcreteEmployee.table.columns
        assert 'service' in ConcreteEmployee.table.columns

        assert 'firstname' in ConcreteCitizen.table.columns
        assert 'lastname' in ConcreteCitizen.table.columns
        assert 'corporation' not in ConcreteCitizen.table.columns
        assert 'country' in ConcreteCitizen.table.columns
        # test that the options_defaults do not leak into the parent base
        assert ConcreteCitizen._descriptor.identity == 'concretecitizen'

    def test_simple_relation(self):
        class Page(Entity):
            title = Field(String(30))
            content = Field(String(30))
            comments = OneToMany('Comment')

        class AbstractAttachment(Entity):
            using_options(abstract=True)

            page = ManyToOne('Page')
            is_spam = Field(Boolean())

        class Comment(AbstractAttachment):
            message = Field(String(100))

        setup_all(True)

        p1 = Page(title="My title", content="My content")
        p1.comments.append(Comment(message='My first comment', is_spam=False))

        assert p1.comments[0].page == p1
        session.commit()

    def test_simple_relation_abstract_wh_multiple_children(self):
        class Page(Entity):
            title = Field(String(30))
            content = Field(String(30))
            comments = OneToMany('Comment')
            links = OneToMany('Link')

        class AbstractAttachment(Entity):
            using_options(abstract=True)

            page = ManyToOne('Page')
            is_spam = Field(Boolean())

        class Link(AbstractAttachment):
            url = Field(String(30))

        class Comment(AbstractAttachment):
            message = Field(String(100))

        setup_all(True)

        p1 = Page(title="My title", content="My content")
        p1.comments.append(Comment(message='My first comment', is_spam=False))
        p1.links.append(Link(url="My url", is_spam=True))

        assert p1.comments[0].page == p1
        session.commit()

    def test_multiple_inheritance(self):
        class AbstractDated(Entity):
            using_options(abstract=True)
            using_options_defaults(tablename=camel_to_underscore)

            #TODO: add defaults
            created_date = Field(DateTime)
            modified_date = Field(DateTime)

        class AbstractContact(Entity):
            using_options(abstract=True)
            using_options_defaults(identity=camel_to_underscore)

            first_name = Field(Unicode(50))
            last_name = Field(Unicode(50))

        class DatedContact(AbstractContact, AbstractDated):
            pass

        setup_all(True)

        assert 'created_date' in DatedContact.table.columns
        assert 'modified_date' in DatedContact.table.columns
        assert 'first_name' in DatedContact.table.columns
        assert 'last_name' in DatedContact.table.columns
        assert DatedContact._descriptor.identity == 'dated_contact'
        assert DatedContact.table.name == 'dated_contact'

        contact1 = DatedContact(first_name=u"Guido", last_name=u"van Rossum")
        session.commit()

    def test_mixed_inheritance(self):
        class AbstractDated(Entity):
            using_options(abstract=True)
            using_options_defaults(tablename=camel_to_underscore)

            #TODO: add defaults
            created_date = Field(DateTime)
            modified_date = Field(DateTime)

        class AbstractContact(Entity):
            using_options(abstract=True)
            using_options_defaults(identity=camel_to_underscore)

            first_name = Field(Unicode(50))
            last_name = Field(Unicode(50))

        class Contact(AbstractContact):
            using_options(inheritance='multi')

        class MixedDatedContact(AbstractDated, Contact):
            using_options(inheritance='multi')

        setup_all(True)

        assert 'created_date' in MixedDatedContact.table.columns
        assert 'modified_date' in MixedDatedContact.table.columns
        assert MixedDatedContact._descriptor.identity == 'mixed_dated_contact'
        assert MixedDatedContact.table.name == 'mixed_dated_contact'

        contact1 = MixedDatedContact(first_name=u"Guido",
                                     last_name=u"van Rossum")
        session.commit()

