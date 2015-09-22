from setuptools import setup, find_packages
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name="Elixir",
      version="0.8.0",
      description="Declarative Mapper for SQLAlchemy",
      long_description="""
Elixir
======

A declarative layer on top of SQLAlchemy. It is a fairly thin wrapper, which
provides the ability to create simple Python classes that map directly to
relational database tables (this pattern is often referred to as the Active
Record design pattern), providing many of the benefits of traditional
databases without losing the convenience of Python objects.

Elixir is intended to replace the ActiveMapper SQLAlchemy extension, and the
TurboEntity project but does not intend to replace SQLAlchemy's core features,
and instead focuses on providing a simpler syntax for defining model objects
when you do not need the full expressiveness of SQLAlchemy's manual mapper
definitions.

SVN version: <http://elixir.ematia.de/svn/elixir/trunk#egg=Elixir-dev>
""",
      author="Gaetan de Menten, Daniel Haus and Jonathan LaCour",
      author_email="sqlelixir@googlegroups.com",
      maintainer="Gaetan de Menten",
      maintainer_email="gdementen@gmail.com",
      url="http://elixir.ematia.de",
      license = "MIT License",
      install_requires = [
          "SQLAlchemy >= 0.5.0"
      ],
      packages=find_packages(exclude=['ez_setup', 'tests', 'examples']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Database :: Front-Ends",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      test_suite = 'nose.collector',
      **extra)
