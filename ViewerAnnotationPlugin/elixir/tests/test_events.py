from elixir import *
from elixir.events import *

from sqlalchemy import Table, Column


class TestEvents(object):
    def teardown(self):
        cleanup_all(True)

    def test_events(self):
        # initialize counters
        stateDict = {
            'reconstructor_called': 0,
            'before_insert_called': 0,
            'after_insert_called': 0,
            'before_update_called': 0,
            'after_update_called': 0,
            'before_delete_called': 0,
            'after_delete_called': 0,
            'before_any_called': 0
        }

        events = Table('events', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        insertRecord = events.insert()

        def record_event(name):
            stateDict[name] += 1
            insertRecord.execute(name=name)

        class Document(Entity):
            name = Field(String(50))

            @reconstructor
            def post_fetch(self):
                record_event('reconstructor_called')

            @before_insert
            def pre_insert(self):
                record_event('before_insert_called')

            @after_insert
            def post_insert(self):
                record_event('after_insert_called')

            @before_update
            def pre_update(self):
                record_event('before_update_called')

            @after_update
            def post_update(self):
                record_event('after_update_called')

            @before_delete
            def pre_delete(self):
                record_event('before_delete_called')

            @after_delete
            def post_delete(self):
                record_event('after_delete_called')

            @before_insert
            @before_update
            @before_delete
            def pre_any(self):
                record_event('before_any_called')

        metadata.bind = 'sqlite://'
        setup_all(True)

        d = Document(name='My Document')
        session.commit(); session.expunge_all()

        d = Document.query.one()
        d.name = 'My Document Updated'
        session.commit(); session.expunge_all()

        d = Document.query.one()
        d.delete()
        session.commit(); session.expunge_all()

        def checkCount(name, value):
            dictCount = stateDict[name]
            assert dictCount == value, \
                'global var count for %s should be %s but is %s' % \
                (name, value, dictCount)

            dbCount = events.select().where(events.c.name == name) \
                                     .count().execute().fetchone()[0]
            assert dbCount == value, \
                'db record count for %s should be %s but is %s' % \
                (name, value, dbCount)

        checkCount('before_insert_called', 1)
        checkCount('before_update_called', 1)
        checkCount('after_update_called', 1)
        checkCount('after_insert_called', 1)
        checkCount('before_delete_called', 1)
        checkCount('after_delete_called', 1)
        checkCount('before_any_called', 3)
        checkCount('reconstructor_called', 2)

    def test_multiple_inheritance(self):
        class AddEventMethods(object):
            update_count = 0

            @after_update
            def post_update(self):
                self.update_count += 1

        class A(Entity, AddEventMethods):
            name = Field(String(50))

        metadata.bind = 'sqlite://'
        setup_all(True)

        a1 = A(name='a1')
        session.commit(); session.expunge_all()

        a = A.query.one()
        a.name = 'a1 updated'
        session.commit(); session.expunge_all()

        assert a.update_count == 1

    def test_entity_wh_bad_descriptors(self):
        class BrokenDescriptor(object):
            def __get__(*args):
                raise AttributeError

        class A(Entity):
            d = BrokenDescriptor()
            name = Field(String(50))

            @after_update
            def post_update(self):
                pass

        metadata.bind = 'sqlite://'
        # we just check that setup does not trigger an exception
        setup_all(True)

