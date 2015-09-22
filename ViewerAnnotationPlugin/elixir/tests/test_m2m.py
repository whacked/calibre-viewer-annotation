"""
test many to many relationships
"""

from elixir import *
import elixir

#-----------

class TestManyToMany(object):
    def setup(self):
        metadata.bind = 'sqlite://'

    def teardown(self):
        cleanup_all(True)

    def test_simple(self):
        class A(Entity):
            using_options(shortnames=True)
            name = Field(String(60))
            as_ = ManyToMany('A')
            bs_ = ManyToMany('B')

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(60))
            as_ = ManyToMany('A')

        setup_all(True)
        A.mapper.compile()

        # check m2m table was generated correctly
        m2m_table = A.bs_.property.secondary
        assert m2m_table.name in metadata.tables

        # check column names
        m2m_cols = m2m_table.columns
        assert 'a_id' in m2m_cols
        assert 'b_id' in m2m_cols

        # check selfref m2m table column names were generated correctly
        m2m_cols = A.as_.property.secondary.columns
        assert 'as__id' in m2m_cols
        assert 'inverse_id' in m2m_cols

        # check the relationships work as expected
        b1 = B(name='b1', as_=[A(name='a1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()
        b = B.query.one()

        assert a in b.as_
        assert b in a.bs_

    def test_table_kwargs(self):
        class A(Entity):
            bs_ = ManyToMany('B', table_kwargs={'info': {'test': True}})

        class B(Entity):
            as_ = ManyToMany('A')

        setup_all(True)
        A.mapper.compile()

        assert A.bs_.property.secondary.info['test'] is True

    def test_table_default_kwargs(self):
        options_defaults['table_options'] = {'info': {'test': True}}

        class A(Entity):
            bs_ = ManyToMany('B')

        class B(Entity):
            as_ = ManyToMany('A')

        setup_all(True)
        A.mapper.compile()

        options_defaults['table_options'] = {}

        assert A.bs_.property.secondary.info['test'] is True
        assert A.table.info['test'] is True
        assert B.table.info['test'] is True

    def test_custom_global_column_nameformat(self):
        # this needs to be done before declaring the classes
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.OLD_M2MCOL_NAMEFORMAT

        class A(Entity):
            bs_ = ManyToMany('B')

        class B(Entity):
            as_ = ManyToMany('A')

        setup_all(True)

        # revert to original format
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.NEW_M2MCOL_NAMEFORMAT

        # check m2m table was generated correctly
        A.mapper.compile()
        m2m_table = A.bs_.property.secondary
        assert m2m_table.name in metadata.tables

        # check column names
        m2m_cols = m2m_table.columns
        assert '%s_id' % A.table.name in m2m_cols
        assert '%s_id' % B.table.name in m2m_cols

    def test_alternate_column_formatter(self):
        # this needs to be done before declaring the classes
        elixir.options.M2MCOL_NAMEFORMAT = \
            elixir.options.ALTERNATE_M2MCOL_NAMEFORMAT

        class A(Entity):
            as_ = ManyToMany('A')
            bs_ = ManyToMany('B')

        class B(Entity):
            as_ = ManyToMany('A')

        setup_all(True)
        A.mapper.compile()

        # revert to original format
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.NEW_M2MCOL_NAMEFORMAT

        # check m2m table column names were generated correctly
        m2m_cols = A.bs_.property.secondary.columns
        assert 'as__id' in m2m_cols
        assert 'bs__id' in m2m_cols

        # check selfref m2m table column names were generated correctly
        m2m_cols = A.as_.property.secondary.columns
        assert 'as__id' in m2m_cols
        assert 'inverse_id' in m2m_cols

    def test_upgrade_rename_col(self):
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.OLD_M2MCOL_NAMEFORMAT

        class A(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            links_to = ManyToMany('A')
            is_linked_from = ManyToMany('A')
            bs_ = ManyToMany('B')

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            as_ = ManyToMany('A')

        setup_all(True)

        a = A(name='a1', links_to=[A(name='a2')])

        session.commit()
        session.expunge_all()

        del A
        del B

        # do not drop the tables, that's the whole point!
        cleanup_all()

        # simulate a renaming of columns (as given by the migration aid)
        # 'a_id1' to 'is_linked_from_id'.
        # 'a_id2' to 'links_to_id'.
        conn = metadata.bind.connect()
        conn.execute("ALTER TABLE a_links_to__a_is_linked_from RENAME TO temp")
        conn.execute("CREATE TABLE a_links_to__a_is_linked_from ("
                        "is_linked_from_id INTEGER NOT NULL, "
                        "links_to_id INTEGER NOT NULL, "
                     "PRIMARY KEY (is_linked_from_id, links_to_id), "
                     "CONSTRAINT a_fk1 FOREIGN KEY(is_linked_from_id) "
                                      "REFERENCES a (id), "
                     "CONSTRAINT a_fk2 FOREIGN KEY(links_to_id) "
                                      "REFERENCES a (id))")
        conn.execute("INSERT INTO a_links_to__a_is_linked_from "
                     "(is_linked_from_id, links_to_id) "
                     "SELECT a_id1, a_id2 FROM temp")
        conn.close()

        # ...
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.NEW_M2MCOL_NAMEFORMAT
#        elixir.options.MIGRATION_TO_07_AID = True

        class A(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            links_to = ManyToMany('A')
            is_linked_from = ManyToMany('A')
            bs_ = ManyToMany('B')

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            as_ = ManyToMany('A')

        setup_all()

        a1 = A.get_by(name='a1')
        assert len(a1.links_to) == 1
        assert not a1.is_linked_from

        a2 = a1.links_to[0]
        assert a2.name == 'a2'
        assert not a2.links_to
        assert a2.is_linked_from == [a1]

    def test_upgrade_local_colname(self):
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.OLD_M2MCOL_NAMEFORMAT

        class A(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            links_to = ManyToMany('A')
            is_linked_from = ManyToMany('A')
            bs_ = ManyToMany('B')

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            as_ = ManyToMany('A')

        setup_all(True)

        a = A(name='a1', links_to=[A(name='a2')])

        session.commit()
        session.expunge_all()

        del A
        del B

        # do not drop the tables, that's the whole point!
        cleanup_all()

        # ...
        elixir.options.M2MCOL_NAMEFORMAT = elixir.options.NEW_M2MCOL_NAMEFORMAT
#        elixir.options.MIGRATION_TO_07_AID = True

        class A(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            links_to = ManyToMany('A', local_colname='a_id1')
            is_linked_from = ManyToMany('A', local_colname='a_id2')
            bs_ = ManyToMany('B')

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(20))
            as_ = ManyToMany('A')

        setup_all()

        a1 = A.get_by(name='a1')
        assert len(a1.links_to) == 1
        assert not a1.is_linked_from

        a2 = a1.links_to[0]
        assert a2.name == 'a2'
        assert not a2.links_to
        assert a2.is_linked_from == [a1]

    def test_multi_pk_in_target(self):
        class A(Entity):
            key1 = Field(Integer, primary_key=True, autoincrement=False)
            key2 = Field(String(40), primary_key=True)

            bs_ = ManyToMany('B')

        class B(Entity):
            name = Field(String(60))
            as_ = ManyToMany('A')

        setup_all(True)

        b1 = B(name='b1', as_=[A(key1=10, key2='a1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()
        b = B.query.one()

        assert a in b.as_
        assert b in a.bs_

    def test_multi(self):
        class A(Entity):
            name = Field(String(100))

            rel1 = ManyToMany('B')
            rel2 = ManyToMany('B')

        class B(Entity):
            name = Field(String(20), primary_key=True)

        setup_all(True)

        b1 = B(name='b1')
        a1 = A(name='a1', rel1=[B(name='b2'), b1],
                          rel2=[B(name='b3'), B(name='b4'), b1])

        session.commit()
        session.expunge_all()

        a1 = A.query.one()
        b1 = B.get_by(name='b1')
        b2 = B.get_by(name='b2')

        assert b1 in a1.rel1
        assert b1 in a1.rel2
        assert b2 in a1.rel1

    def test_selfref(self):
        class Person(Entity):
            using_options(shortnames=True)
            name = Field(String(30))

            friends = ManyToMany('Person')

        setup_all(True)

        barney = Person(name="Barney")
        homer = Person(name="Homer", friends=[barney])
        barney.friends.append(homer)

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        barney = Person.get_by(name="Barney")

        assert homer in barney.friends
        assert barney in homer.friends

        m2m_cols = Person.friends.property.secondary.columns
        assert 'friends_id' in m2m_cols
        assert 'inverse_id' in m2m_cols

    def test_bidirectional_selfref(self):
        class Person(Entity):
            using_options(shortnames=True)
            name = Field(String(30))

            friends = ManyToMany('Person')
            is_friend_of = ManyToMany('Person')

        setup_all(True)

        barney = Person(name="Barney")
        homer = Person(name="Homer", friends=[barney])
        barney.friends.append(homer)

        session.commit()
        session.expunge_all()

        homer = Person.get_by(name="Homer")
        barney = Person.get_by(name="Barney")

        assert homer in barney.friends
        assert barney in homer.friends

        m2m_cols = Person.friends.property.secondary.columns
        assert 'friends_id' in m2m_cols
        assert 'is_friend_of_id' in m2m_cols

    def test_has_and_belongs_to_many(self):
        class A(Entity):
            has_field('name', String(100))

            has_and_belongs_to_many('bs', of_kind='B')

        class B(Entity):
            has_field('name', String(100), primary_key=True)

        setup_all(True)

        b1 = B(name='b1')
        a1 = A(name='a1', bs=[B(name='b2'), b1])
        a2 = A(name='a2', bs=[B(name='b3'), b1])
        a3 = A(name='a3')

        session.commit()
        session.expunge_all()

        a1 = A.get_by(name='a1')
        a2 = A.get_by(name='a2')
        a3 = A.get_by(name='a3')
        b1 = B.get_by(name='b1')
        b2 = B.get_by(name='b2')

        assert b1 in a1.bs
        assert b2 in a1.bs
        assert b1 in a2.bs
        assert not a3.bs

    def test_local_and_remote_colnames(self):
        class A(Entity):
            using_options(shortnames=True)
            key1 = Field(Integer, primary_key=True, autoincrement=False)
            key2 = Field(String(40), primary_key=True)

            bs_ = ManyToMany('B', local_colname=['foo', 'bar'],
                                  remote_colname="baz")

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(60))
            as_ = ManyToMany('A', remote_colname=['foo', 'bar'],
                                  local_colname="baz")

        setup_all(True)

        b1 = B(name='b1', as_=[A(key1=10, key2='a1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()
        b = B.query.one()

        assert a in b.as_
        assert b in a.bs_

    def test_manual_table_auto_joins(self):
        from sqlalchemy import Table, Column, ForeignKey, ForeignKeyConstraint

        # Can't use None as column types because this is unsupported in SA 0.6+
        # for composite foreign keys
        a_b = Table('a_b', metadata,
                    Column('a_key1', Integer),
                    Column('a_key2', String(40)),
                    Column('b_id', None, ForeignKey('b.id')),
                    ForeignKeyConstraint(['a_key1', 'a_key2'],
                                         ['a.key1', 'a.key2']))

        class A(Entity):
            using_options(shortnames=True)
            key1 = Field(Integer, primary_key=True, autoincrement=False)
            key2 = Field(String(40), primary_key=True)

            bs_ = ManyToMany('B', table=a_b)

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(60))
            as_ = ManyToMany('A', table=a_b)

        setup_all(True)

        b1 = B(name='b1', as_=[A(key1=10, key2='a1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()
        b = B.query.one()

        assert a in b.as_
        assert b in a.bs_

    def test_manual_table_manual_joins(self):
        from sqlalchemy import Table, Column, and_

        a_b = Table('a_b', metadata,
                    Column('a_key1', Integer),
                    Column('a_key2', String(40)),
                    Column('b_id', String(60)))

        class A(Entity):
            using_options(shortnames=True)
            key1 = Field(Integer, primary_key=True, autoincrement=False)
            key2 = Field(String(40), primary_key=True)

            bs_ = ManyToMany('B', table=a_b,
                             primaryjoin=lambda: and_(A.key1 == a_b.c.a_key1,
                                                      A.key2 == a_b.c.a_key2),
                             secondaryjoin=lambda: B.id == a_b.c.b_id,
                             foreign_keys=[a_b.c.a_key1, a_b.c.a_key2,
                                 a_b.c.b_id])

        class B(Entity):
            using_options(shortnames=True)
            name = Field(String(60))

        setup_all(True)

        a1 = A(key1=10, key2='a1', bs_=[B(name='b1')])

        session.commit()
        session.expunge_all()

        a = A.query.one()
        b = B.query.one()

        assert b in a.bs_
