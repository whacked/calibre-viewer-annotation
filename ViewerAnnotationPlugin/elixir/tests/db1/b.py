from elixir import Entity, ManyToMany, using_options

class B(Entity):
    using_options(resolve_root='tests.db1')

    cs = ManyToMany('.c.C')
    a1s = ManyToMany('a.A1')
