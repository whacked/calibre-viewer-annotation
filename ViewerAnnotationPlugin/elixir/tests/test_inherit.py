"""
test inheritance
"""

from elixir import *
import elixir

def setup():
    metadata.bind = 'sqlite://'
#    metadata.bind = 'postgresql://@/test'
#    metadata.bind.echo = True
    elixir.options_defaults['shortnames'] = True

def teardown():
    elixir.options_defaults['shortnames'] = False

def do_tst(inheritance, polymorphic, expected_res):
    class A(Entity):
        using_options(inheritance=inheritance, polymorphic=polymorphic)
        data1 = Field(String(20))

    class B(A):
        using_options(inheritance=inheritance, polymorphic=polymorphic)
        data2 = Field(String(20))
        some_e = ManyToOne('E')

    class C(B):
        using_options(inheritance=inheritance, polymorphic=polymorphic)
        data3 = Field(String(20))

    class D(A):
        using_options(inheritance=inheritance, polymorphic=polymorphic)
        data4 = Field(String(20))

    class E(A):
        using_options(inheritance=inheritance, polymorphic=polymorphic)
        many_b = OneToMany('B')

    setup_all(True)

    e1 = E(data1='e1')
    a1 = A(data1='a1')
    b1 = B(data1='b1', data2='b2', some_e=e1)
    if polymorphic:
        c1 = C(data1='c1', data2='c2', data3='c3', some_e=e1)
    else:
        c1 = C(data1='c1', data2='c2', data3='c3')
    d1 = D(data1='d1', data4='d4')

    session.commit()
    session.expunge_all()

    res = {}
    for class_ in (A, B, C, D, E):
        res[class_.__name__] = class_.query.all()
        res[class_.__name__].sort(key=lambda o: o.__class__.__name__)

    for query_class in ('A', 'B', 'C', 'D', 'E'):
#        print res[query_class], expected_res[query_class]
        assert len(res[query_class]) == len(expected_res[query_class])
        for real, expected in zip(res[query_class], expected_res[query_class]):
            assert real.__class__.__name__ == expected


class TestInheritance(object):
    def teardown(self):
        cleanup_all(True)

    # this is related to SA ticket 866
    # http://www.sqlalchemy.org/trac/ticket/866
    # the problem was caused by the fact that the attribute-based syntax left
    # the class-attributes in place after initialization (in Elixir 0.4).
    def test_missing_value(self):
        class A(Entity):
            pass

        class B(A):
            name = Field(String(30))
            other = Field(Text)

        setup_all()
        create_all()

        b1 = B(name="b1") # no value for other

        session.commit()

    def test_delete_parent(self):
        class A(Entity):
            using_options(inheritance='multi')

        class B(A):
            using_options(inheritance='multi')
            name = Field(String(30))

        setup_all(True)

        b1 = B(name='b1')

        session.commit()

        A.table.delete().execute()

        # this doesn't work on sqlite (because it relies on the database
        # enforcing the foreign key constraint cascade rule).
#        assert not B.table.select().execute().fetchall()

    def test_inheritance_wh_schema(self):
        # I can only test schema stuff on postgres
        if metadata.bind.name != 'postgres':
            print "schema test skipped"
            return

        class A(Entity):
            using_options(inheritance="multi")
            using_table_options(schema="test")

            row_id = Field(Integer, primary_key=True)
            thing1 = Field(String(20))

        class B(A):
            using_options(inheritance="multi")
            using_table_options(schema="test")

            thing2 = Field(String(20))

        setup_all(True)

    def test_inverse_matching_on_parent(self):
        class Person(Entity):
            using_options(inheritance='multi')
            name = Field(UnicodeText)

        class Parent(Person):
            using_options(inheritance='multi')
            childs = ManyToMany('Child', tablename='child_parent',
                                inverse='parents')

        class Child(Person):
            using_options(inheritance='multi')
            parents = ManyToMany('Parent', tablename='child_parent',
                                 inverse='childs')

        setup_all()

    def test_multi_pk(self):
        class A(Entity):
            using_options(inheritance='multi')
            firstname = Field(String(50), primary_key=True)
            lastname = Field(String(50), primary_key=True)

        class B(A):
            using_options(inheritance='multi')

        setup_all(True)

        b1 = B(firstname='1', lastname='b')
        b2 = B(firstname='2', lastname='b')

        session.commit()

        b1.delete()

        session.commit()

        assert len(B.query.all()) == 1

    def test_multitable_polymorphic_load(self):
        class A(Entity):
            using_options(inheritance='multi')
            # we want to load children's specific data along the parent (A)
            # data when querying the parent. If we don't specify this, the
            # children data is loaded lazily
            using_mapper_options(with_polymorphic='*')
            name = Field(String(50))

        class B(A):
            using_options(inheritance='multi')
            data = Field(String(50))
            some_c = ManyToOne('C')
            some_a = ManyToOne('A')

        class C(A):
            using_options(inheritance='multi')

            data = Field(String(50))
            many_b = OneToMany('B')
        setup_all(True)
        a1 = A(name='a1')
        c1 = C(name='c1', data="c")
        b1 = B(name='b1', data="b", some_c=c1)

        session.commit()
        session.expunge_all()

        for a in A.query.all():
            if isinstance(a, (B, C)):
                # On SA 0.4.x, this test works whether with_polymorphic is
                # specified or not, because in 0.4.x, without with_polymorphic,
                # it issues as many queries as necessary to load all data,
                # while in 0.5, columns are "deferred".
                assert 'data' in a.__dict__

    def test_singletable_inheritance(self):
        do_tst('single', False, {
            'A': ('A', 'A', 'A', 'A', 'A'),
            'B': ('B', 'B', 'B', 'B', 'B'),
            'C': ('C', 'C', 'C', 'C', 'C'),
            'D': ('D', 'D', 'D', 'D', 'D'),
            'E': ('E', 'E', 'E', 'E', 'E')
        })

    def test_polymorphic_singletable_inheritance(self):
        do_tst('single', True, {
            'A': ('A', 'B', 'C', 'D', 'E'),
            'B': ('B', 'C'),
            'C': ('C',),
            'D': ('D',),
            'E': ('E',),
        })

    def test_concrete_inheritance(self):
        do_tst('concrete', False, {
            'A': ('A',),
            'B': ('B',),
            'C': ('C',),
            'D': ('D',),
            'E': ('E',),
        })

#    def test_polymorphic_concrete_inheritance(self):
#        do_tst('concrete', True, {
#            'A': ('A', 'B', 'C', 'D', 'E'),
#            'B': ('B', 'C'),
#            'C': ('C',),
#            'D': ('D',),
#            'E': ('E',),
#        })

    def test_multitable_inheritance(self):
        do_tst('multi', False, {
            'A': ('A', 'A', 'A', 'A', 'A'),
            'B': ('B', 'B'),
            'C': ('C',),
            'D': ('D',),
            'E': ('E',),
        })

    def test_polymorphic_multitable_inheritance(self):
        do_tst('multi', True, {
            'A': ('A', 'B', 'C', 'D', 'E'),
            'B': ('B', 'C'),
            'C': ('C',),
            'D': ('D',),
            'E': ('E',),
        })

