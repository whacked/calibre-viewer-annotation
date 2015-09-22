from elixir import Entity, ManyToMany

class A(Entity):
    cs = ManyToMany('..db1.c.C')
