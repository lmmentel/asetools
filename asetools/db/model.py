# -*- coding: utf-8 -*-

''' a database for storing the ase atoms abjects'''

from __future__ import print_function, division, unicode_literals, absolute_import

from builtins import (bytes, dict, int, list, object, range, str,
                      ascii, chr, hex, input, next, oct, open,
                      pow, round, super, filter, map, zip)

from operator import attrgetter
import datetime
import numpy as np
import os
import shutil

from sqlalchemy import (Column, LargeBinary, Integer, String, Float,
        PickleType, ForeignKey, DateTime, Unicode, UnicodeText, Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from ..asetools import AseTemplate
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

    'Database version of the Calculator class'

    __tablename__ = 'calculators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    description = Column(String)

    attributes = relationship("DBCalculatorAttribute",
                              collection_class=attribute_mapped_collection('key'),
                              cascade="all, delete-orphan")
    _proxied = association_proxy("attributes", "value",
                        creator=lambda key, value: DBCalculatorAttribute(key=key, value=value))

    @classmethod
    def with_attr(self, key, value):
        return self.attributes.any(key=key, value=value)

    def get_arguments(self):
        '''
        Return a dict with calculator init arguments (stored as attributes).

        String values are surrounded by quotes since the attributes will be rendered to a template
        for example, ``mode='scf'`` will be stored as mode='"scf"'``
        '''

        # a list of arguments that are not: str, int, float or bool
        nonbasic = ['convergence', 'kptshift', 'dipole', 'field', 'output']

        out = {}
        for k, v in self.attributes.items():
            if isinstance(v.value, str) and not k in nonbasic:
                out[k] = "'{}'".format(v.value)
            else:
                out[k] = v.value
        return out

    def __repr__(self):

        out = ["DBCalculator(id={0}, name='{1:s}', version={2:s}, description={3:s},".format(
                self.id, self.name, self.version, self.description)]
        out.extend(["\t{0:s} = {1}".format(k, v) for k, v in self.attributes.items()])

        return "\n".join(out) + ')'

class DBTemplateNote(PolymorphicVerticalProperty, Base):
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

class DBTemplate(ProxiedDictMixin, Base):

    __tablename__ = 'asetemplates'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    template = Column(String)
    ase_version = Column(String)

    notes = relationship('DBTemplateNote',
                collection_class=attribute_mapped_collection('key'),
                cascade="all, delete-orphan")

    _proxied = association_proxy('notes', 'value',
                        creator=
                        lambda key, value: DBTemplateNote(key=key, value=value))

    @classmethod
    def with_note(cls, key, value):
        'Convenience method fr querying'
        return cls.notes.any(key=key, value=value)

    def get_repl_keys(self):
        'Return the keys that will be rendered in the template'

        t = AseTemplate(self.template)
        return t.get_keys()

    def __repr__(self):

        out = ["DBTemplate(id={0}, name='{1:s}', ase_version={2:s},".format(
               self.id, self.name, self.ase_version)]
        out.extend(["\t{0:s} = {1}".format(k, v) for k, v in self.notes.items()])

        return "\n".join(out) + ')'

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

    def __repr__(self):

        return "<DBAtom(atomic_number={0:d}, mass={1:10.4f}, x={2:10.4f}, y={3:10.4f}, z={4:10.4f})>".format(
            self.atomic_number, self.mass, self.x, self.y, self.z)

class Job(Base):

    'Class for handling jobs'

    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id'))
    name = Column(String)
    username = Column(String)
    hostname = Column(String)
    jobscript = Column(String)
    abspath = Column(String)
    inpname = Column(String)
    outname = Column(String)
    status = Column(String)

    calculator_id = Column(ForeignKey('calculators.id'))
    calculator = relationship('DBCalculator')

    template_id = Column(ForeignKey('asetemplates.id'))
    template = relationship('DBTemplate')

    @hybrid_property
    def inppath(self):
        'Return the full path to the input file'
        return os.path.join(self.abspath, self.inpname)

    @hybrid_property
    def outpath(self):
        'Return the full path to the outpath file'
        return os.path.join(self.abspath, self.outname)

    def create_job(self, repl, overwrite=False):
        '''
        Create a directory for a job and write the job script to it based on
        the information from the Job instance.

        Args:
          repl : dict
            Dictionary of items to be replaced in the template
	  overwrite : bool
	    If `True`, overwrite any files already present
        '''

        if os.path.exists(self.abspath):
            if overwrite:
                shutil.rmtree(self.abspath)
            else:
                raise OSError('path: {} exists'.format(self.abspath))
        os.makedirs(self.abspath)

        t = AseTemplate(self.template.template)
        t.render_and_write(repl, output=self.inppath)

    def __repr__(self):
        return "%s(\n%s)" % (
            (self.__class__.__name__),
            ' '.join(["\t%s=%r,\n" % (key, getattr(self, key))
                      for key in sorted(self.__dict__.keys())
                      if not key.startswith('_')]))

class Vibration(Base):

    '''A single vibration'''

    __tablename__ = 'vibrations'

    id = Column(Integer, primary_key=True)
    energy_real = Column(Float, nullable=False)
    energy_imag = Column(Float, nullable=False)
    vibrationset_id = Column(Integer, ForeignKey('vibrationsets.id'), nullable=False)

    def __repr__(self):
        return "<Vibration(vibrationset_id={0:d}, energy_real={1:15.8f}, energy_imag={2:15.8f})>".format(
                self.vibrationset_id, self.energy_real, self.energy_imag)

class VibrationSet(Base):

    __tablename__ = 'vibrationsets'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    atom_ids = Column(String)

    system_id = Column(Integer, ForeignKey('systems.id'), nullable=False)

    vibrations = relationship('Vibration', cascade="all, delete-orphan")

    @hybrid_property
    def atom_indices(self):
        'Return a list of atom indices that were used for calculating vibrations'

        if self.atom_ids is not None:
            return np.array(self.atom_ids.split(','), dtype=np.int32)

    @hybrid_property
    def vibenergies(self):
        '''Return a numpy array with the vibration energies'''

        values = [v.energy_real + 1j*v.energy_imag for v in self.vibrations]
        if len(values) > 0:
            return np.asarray(values, dtype=np.complex128)
        else:
            return None

    def __repr__(self):
        return "<VibrationSet(id={0:d}, name={1:s}, system_id={2:d}, atom_ids={3:s})>".format(
                self.id, self.name, self.system_id, self.atom_ids)

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
      name : str
        Name of the system
      topology : str
        Three letter code of the zeolite framework topology
      formula : str
        Chemical formula of the system (unit cell)
      magnetic_moment: float
	The total magnetic moment
    '''

    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True)

    ctime = Column(DateTime, default=datetime.datetime.now)
    mtime = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    name = Column(String)
    topology = Column(String)
    formula = Column(String)

    articledoi = Column(String)

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
    enthalpy = Column(Float)
    internal_energy = Column(Float)
    entropy = Column(Float)
    free_energy = Column(Float)
    thermo = Column(String)
    magnetic_moment = Column(Float)
    #dipole_x = Column(Float)
    #dipole_y = Column(Float)
    #dipole_z = Column(Float)
    #stress = Column(PickleType)

    jobs = relationship('Job', cascade="all, delete-orphan")

    atoms = relationship('DBAtom', cascade="all, delete-orphan")

    vibrationsets = relationship('VibrationSet', cascade="all, delete-orphan")


    notes = relationship('SystemNote',
                collection_class=attribute_mapped_collection('key'),
                cascade="all, delete-orphan")

    _proxied = association_proxy('notes', 'value',
                        creator=
                        lambda key, value: SystemNote(key=key, value=value))

    @classmethod
    def with_note(self, key, value):
        'Convenience method for querying'
        return self.notes.any(key=key, value=value)

    @hybrid_property
    def forces(self):
        '''Return a numpy array with the forces'''

        values = [[a.force_x,a.force_y,a.force_z] for a in self.atoms]
        if len(values) > 0:
            return np.asarray(values)
        else:
            return None

    def __repr__(self):

        out = ["System(id={0}, name='{1:s}', topology={2:s}, formula={3:s},".format(
                self.id, self.name, self.topology, self.formula)]
        out.extend(["\t{0:s} = {1}".format(k, v) for k, v in self.notes.items()])

        return "\n".join(out) + ')'
