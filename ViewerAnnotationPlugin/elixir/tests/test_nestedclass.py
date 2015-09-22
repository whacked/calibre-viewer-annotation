from elixir import *

def setup():
    global Thing

    class Thing(Entity):
        name = Field(String(40))
        type = Field(String(40))

        class Stuff(Entity):
            ping = Field(String(32))
            pong = Field(String(32))

        other = Field(String(40))

    setup_all()

class TestNestedClass(object):
    def test_nestedclass(self):
        assert 'name' in Thing.table.columns
        assert 'type' in Thing.table.columns
        assert 'other' in Thing.table.columns
        assert 'ping' not in Thing.table.columns
        assert 'pong' not in Thing.table.columns

        assert 'name' not in Thing.Stuff.table.columns
        assert 'type' not in Thing.Stuff.table.columns
        assert 'other' not in Thing.Stuff.table.columns
        assert 'ping' in Thing.Stuff.table.columns
        assert 'pong' in Thing.Stuff.table.columns
