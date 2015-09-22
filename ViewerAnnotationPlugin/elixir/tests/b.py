from elixir import *

class B(Entity):
    name = Field(String(30))
    many_a = OneToMany('tests.a.A')

