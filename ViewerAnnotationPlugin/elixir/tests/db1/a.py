from elixir import Entity, ManyToOne, OneToMany, ManyToMany, using_options

class A1(Entity):
    using_options(resolve_root='tests.db1')

    a2s = OneToMany('A2')
    bs = ManyToMany('b.B')

class A2(Entity):
    a1 = ManyToOne('A1')

