# -*- coding: utf-8 -*-

''' a database for storing the ase atoms abjects'''

from __future__ import unicode_literals, print_function, division

from sqlalchemy import (Column, LargeBinary, Integer, String, Float,
        PickleType, ForeignKey, DateTime, Unicode, UnicodeText, Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import os
from operator import attrgetter
import datetime

# code  below is taken from:
# http://docs.sqlalchemy.org/en/latest/_modules/examples/vertical/dictlike-polymorphic.html

from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy import event, cast, case, null, literal_column

class ProxiedDictMixin(object):
    """Adds obj[key] access to a mapped class.

    This class basically proxies dictionary access to an attribute
    called ``_proxied``.  The class which inherits this class
    should have an attribute called ``_proxied`` which points to a dictionary.
    """

    def __len__(self):
        return len(self._proxied)

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, key):
        return self._proxied[key]

    def __contains__(self, key):
        return key in self._proxied

    def __setitem__(self, key, value):
        self._proxied[key] = value

    def __delitem__(self, key):
        del self._proxied[key]

class PolymorphicVerticalProperty(object):
    """A key/value pair with polymorphic value storage.

    The class which is mapped should indicate typing information
    within the "info" dictionary of mapped Column objects; see
    the AnimalFact mapping below for an example.

    """

    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    @hybrid_property
    def value(self):
        fieldname, discriminator = self.type_map[self.type]
        if fieldname is None:
            return None
        else:
            return getattr(self, fieldname)

    @value.setter
    def value(self, value):
        py_type = type(value)
        fieldname, discriminator = self.type_map[py_type]

        self.type = discriminator
        if fieldname is not None:
            setattr(self, fieldname, value)

    @value.deleter
    def value(self):
        self._set_value(None)

    @value.comparator
    class value(PropComparator):
        """A comparator for .value, builds a polymorphic comparison via CASE.

        """
        def __init__(self, cls):
            self.cls = cls

        def _case(self):
            pairs = set(self.cls.type_map.values())
            whens = [
                (
                    literal_column("'%s'" % discriminator),
                    cast(getattr(self.cls, attribute), String)
                ) for attribute, discriminator in pairs
                if attribute is not None
            ]
            return case(whens, self.cls.type, null())
        def __eq__(self, other):
            return self._case() == cast(other, String)
        def __ne__(self, other):
            return self._case() != cast(other, String)

    def __repr__(self):
        return '<%s %r=%r>' % (self.__class__.__name__, self.key, self.value)

@event.listens_for(PolymorphicVerticalProperty, "mapper_configured", propagate=True)
def on_new_class(mapper, cls_):
    """Look for Column objects with type info in them, and work up
    a lookup table."""

    info_dict = {}
    info_dict[type(None)] = (None, 'none')
    info_dict['none'] = (None, 'none')

    for k in mapper.c.keys():
        col = mapper.c[k]
        if 'type' in col.info:
            python_type, discriminator = col.info['type']
            info_dict[python_type] = (k, discriminator)
            info_dict[discriminator] = (k, discriminator)
    cls_.type_map = info_dict

# end of the borrowed code

Base = declarative_base()

class DBCalculatorAttribute(PolymorphicVerticalProperty, Base):
    '''class to handle storing key-value pairs for the calculator attributes'''

    __tablename__ = 'calculator_attributes'

    calculator_id = Column(ForeignKey('calculators.id'), primary_key=True)
    key = Column(Unicode(64), primary_key=True)
    type = Column(Unicode(16))

    # add information about storage for different types
    # in the info dictionary of Columns
    int_value = Column(Integer, info={'type': (int, 'integer')})
    float_value = Column(Float, info={'type': (float, 'float')})
    char_value = Column(UnicodeText, info={'type': (str, 'string')})
    boolean_value = Column(Boolean, info={'type': (bool, 'boolean')})

class DBCalculator(ProxiedDictMixin, Base):

    __tablename__ = 'calculators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    description = Column(String)

    attributes = relationship("DBCalculatorAttribute",
                    collection_class=attribute_mapped_collection('key'))
    _proxied = association_proxy("attributes", "value",
                        creator=
                        lambda key, value: DBCalculatorAttribute(key=key, value=value))

    @classmethod
    def with_attr(self, key, value):
        return self.attributes.any(key=key, value=value)

class ASETemplateNote(PolymorphicVerticalProperty, Base):
    '''class to handle storing key-value pairs for the calculator attributes'''

    __tablename__ = 'asetemplate_notes'

    template_id = Column(ForeignKey('asetemplates.id'), primary_key=True)
    key = Column(Unicode(64), primary_key=True)
    type = Column(Unicode(16))

    # add information about storage for different types
    # in the info dictionary of Columns
    int_value = Column(Integer, info={'type': (int, 'integer')})
    float_value = Column(Float, info={'type': (float, 'float')})
    char_value = Column(UnicodeText, info={'type': (str, 'string')})
    boolean_value = Column(Boolean, info={'type': (bool, 'boolean')})

class ASETemplate(ProxiedDictMixin, Base):

    __tablename__ = 'asetemplates'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    template = Column(String)
    ase_version = Column(String)

    notes = relationship('ASETemplateNote',
                collection_class=attribute_mapped_collection('key'))

    _proxied = association_proxy('notes', 'value',
                        creator=
                        lambda key, value: ASETemplateNote(key=key, value=value))

    @classmethod
    def with_note(self, key, value):
        return self.notes.any(key=key, value=value)

class DBAtom(Base):
    '''Atom ORM object'''

    __tablename__ = 'atoms'

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id'))

    atomic_number = Column(Integer)
    initial_magmom = Column(Float)
    initial_charge = Column(Float)
    mass = Column(Float)
    tag = Column(Integer)

    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    momentum_x = Column(Float)
    momentum_y = Column(Float)
    momentum_z = Column(Float)

    charge = Column(Float)
    force_x = Column(Float)
    force_y = Column(Float)
    force_z = Column(Float)
    magmom = Column(Float)

class SystemNote(PolymorphicVerticalProperty, Base):
    '''class to handle storing key-value pairs for the system'''

    __tablename__ = 'system_notes'

    system_id = Column(ForeignKey('systems.id'), primary_key=True)
    key = Column(Unicode(64), primary_key=True)
    type = Column(Unicode(16))

    # add information about storage for different types
    # in the info dictionary of Columns
    int_value = Column(Integer, info={'type': (int, 'integer')})
    float_value = Column(Float, info={'type': (float, 'float')})
    char_value = Column(UnicodeText, info={'type': (str, 'string')})
    boolean_value = Column(Boolean, info={'type': (bool, 'boolean')})

class System(ProxiedDictMixin, Base):
    '''
    System ORM object

    Attributes:
      username : str
        Name of the user
      name : str
        Name of the system
      framework : str
        Three letter code of the zeolite framework
      formula : str
        Chemical formula of the system (unit cell)
    '''

    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True)

    ctime = Column(DateTime, default=datetime.datetime.now)
    mtime = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    username = Column(String)

    name = Column(String)
    framework = Column(String(3))
    formula = Column(String)

    cell_a = Column(Float)
    cell_b = Column(Float)
    cell_c = Column(Float)
    cell_alpha = Column(Float)
    cell_beta = Column(Float)
    cell_gamma = Column(Float)
    pbc_a = Column(Boolean)
    pbc_b = Column(Boolean)
    pbc_c = Column(Boolean)

    # results of the calculation

    energy = Column(Float)
    internal_energy = Column(Float)
    entropy = Column(Float)
    free_energy = Column(Float)
    thermo = Column(String)
    #magmom = Column(Float)
    #dipole_x = Column(Float)
    #dipole_y = Column(Float)
    #dipole_z = Column(Float)
    #stress = Column(PickleType)

    atoms = relationship('DBAtom')

    calculator_id = Column(ForeignKey('calculators.id'))
    calculator = relationship('DBCalculator')

    template_id = Column(ForeignKey('asetemplates.id'))
    template = relationship('ASETemplate')

    notes = relationship('SystemNote',
                collection_class=attribute_mapped_collection('key'))

    _proxied = association_proxy('notes', 'value',
                        creator=
                        lambda key, value: SystemNote(key=key, value=value))

#    def __init__(self, name):
#        self.name = name

    def __repr__(self):
        return "System(%r)" % self.framework

    @classmethod
    def with_note(self, key, value):
        return self.notes.any(key=key, value=value)
