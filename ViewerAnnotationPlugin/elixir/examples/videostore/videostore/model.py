from turbogears.database    import metadata, session
from elixir                 import Unicode, DateTime, String, Integer
from elixir                 import Entity, Field, using_options
from elixir                 import OneToMany, ManyToOne, ManyToMany
from elixir                 import setup_all
from datetime               import datetime

#
# application model
#

class Director(Entity):
    name = Field(Unicode(60))
    movies = OneToMany('Movie', inverse='director')
    using_options(tablename='directors')


class Movie(Entity):
    title = Field(Unicode(60))
    description = Field(Unicode(512))
    releasedate = Field(DateTime)
    director = ManyToOne('Director', inverse='movies')
    actors = ManyToMany('Actor', inverse='movies', tablename='movie_casting')
    using_options(tablename='movies')


class Actor(Entity):
    name = Field(Unicode(60))
    movies = ManyToMany('Movie', inverse='actors', tablename='movie_casting')
    using_options(tablename='actors')


#
# identity model
#

class Visit(Entity):
    visit_key = Field(String(40), primary_key=True)
    created = Field(DateTime, required=True, default=datetime.now)
    expiry = Field(DateTime)
    using_options(tablename='visit')

    @classmethod
    def lookup_visit(cls, visit_key):
        return Visit.get(visit_key)

class VisitIdentity(Entity):
    visit_key = Field(String(40), primary_key=True)
    user = ManyToOne('User', colname='user_id', use_alter=True)
    using_options(tablename='visit_identity')

class Group(Entity):
    group_id = Field(Integer, primary_key=True)
    group_name = Field(Unicode(16), unique=True)
    display_name = Field(Unicode(255))
    created = Field(DateTime, default=datetime.now)
    users = ManyToMany('User', inverse='groups')
    permissions = ManyToMany('Permission', inverse='groups')
    using_options(tablename='tg_group')

class User(Entity):
    user_id = Field(Integer, primary_key=True)
    user_name = Field(Unicode(16), unique=True)
    email_address = Field(Unicode(255), unique=True)
    display_name = Field(Unicode(255))
    password = Field(Unicode(40))
    created = Field(DateTime, default=datetime.now)
    groups = ManyToMany('Group', inverse='users')
    using_options(tablename='tg_user')

    @property
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

class Permission(Entity):
    permission_id = Field(Integer, primary_key=True)
    permission_name = Field(Unicode(16), unique=True)
    description = Field(Unicode(255))
    groups = ManyToMany('Group', inverse='permissions')
    using_options(tablename='permission')

# create the table and mapper instances for the above entities
setup_all()
