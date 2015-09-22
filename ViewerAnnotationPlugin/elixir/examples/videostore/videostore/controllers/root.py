from turbogears.controllers     import RootController
from videostore.model           import Movie, Director, Actor
from turbogears                 import identity, redirect, expose
from turbogears                 import validators, validate
from cherrypy                   import request, response


class Root(RootController):

    @expose(template='videostore.templates.index')
    @identity.require(identity.not_anonymous())
    def index(self):
        return dict(movies=Movie.query.all())


    @expose(template='videostore.templates.movie')
    @identity.require(identity.not_anonymous())
    @validate(validators=dict(movieID=validators.Int()))
    def movie(self, movieID):
        return dict(movie=Movie.get(movieID))


    @expose(template='videostore.templates.actor')
    @identity.require(identity.not_anonymous())
    @validate(validators=dict(actorID=validators.Int()))
    def actor(self, actorID):
        return dict(actor=Actor.get(actorID))


    @expose(template='videostore.templates.director')
    @identity.require(identity.not_anonymous())
    @validate(validators=dict(directorID=validators.Int()))
    def director(self, directorID):
        return dict(director=Director.get(directorID))


    @expose(template='videostore.templates.login')
    def login(self, forward_url=None, previous_url=None, *args, **kw):
        if not identity.current.anonymous and \
               identity.was_login_attempted() and not \
               identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url = None
        previous_url = request.path

        if identity.was_login_attempted():
            msg = 'The credentials you supplied were not correct.'
        elif identity.get_identity_errors():
            msg = 'You must provide your credentials.'
        else:
            msg = 'Please log in.'
            forward_url = request.headers.get('Referer', '/')

        response.status = 403
        return dict(message=msg,
                    previous_url=previous_url,
                    logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)


    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
