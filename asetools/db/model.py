
''' a database for storing the ase atoms abjects'''

from sqlalchemy import Column, LargeBinary, Integer, String, Float, PickleType, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import os
from operator import attrgetter
import datetime

Base = declarative_base()

class Species(Base):

    __tablename__ = 'species'

    id = Column(Integer, primary_key=True)
    z = Column(Integer)
    n = Column(Integer)

class Label(Base):

    __tablename__ = 'labels'

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id'))
    label = Column(String)

    def __init__(self, label):
        self.label = label

class Kwarg(Base):

    __tablename__ = 'kwargs'

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id'))
    key = Column(String)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

class System(Base):

    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    username = Column(String)

    framework = Column(String) # framework code of the zeolite topology
    atoms = Column(PickleType)

    cell_a = Column(Float)
    cell_b = Column(Float)
    cell_c = Column(Float)
    cell_alpha = Column(Float)
    cell_beta = Column(Float)
    cell_gamma = Column(Float)
    pbc = Column(Bool)

    # results of the calculation

    energy = Column(Float)
    free_energy = Column(Float)
    forces = Column(PickleType)
    stress = Column(PickleType)
    magmom = Column(PickleType)

    _labels = relationship(Label)
    _kwargs = relationship(Kwarg)


    @hybrid_property
    def labels(self):
        return [l.label for l in self._labels]

    @hybrid_property
    def kwargs(self):
        return {kw.key:kw.value for kw in self._kwargs}

class Calculator(Base):

    __tablename__ = 'calculators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    attributes = relationship(CalculatorAttributes)

class CalculatorAttributes(Base):

    __tablename__ = 'calcattrs'

    id = Column(Integer, primary_key=True)
    attribute = column

class ASETemplate(Base):

    __tablename__ = 'asetemplates'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    template = Column(String)

def get_session(dbpath):
    '''Return the database session connection.'''

    if os.path.exists(dbpath):
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
    else:
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
        Base.metadata.create_all(engine)
    db_session =  sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()

def get_engine(dbpath):
    '''Return the db engine'''

    engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
    return engine

