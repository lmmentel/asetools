# -*- coding: utf-8 -*-

'''A module providing methods for communication between ASE and the database'''

from __future__ import unicode_literals, print_function, division

import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
from ase import Atoms
from ase.lattice.spacegroup.cell import cellpar_to_cell, cell_to_cellpar
from .model import Base, DBAtom, System, ASETemplate, DBCalculator

def get_session(dbpath, echo=False):
    '''Return the database session connection.'''

    if os.path.exists(dbpath):
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=echo)
    else:
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=echo)
        Base.metadata.create_all(engine)
    db_session =  sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()

def get_engine(dbpath):
    '''Return the db engine'''

    engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
    return engine

def numpify(atomlist, attribute):
    '''
    Create a numpy array containing an attribute of DBAtoms from a list of
    DBAtom objects.

    Args:
      atomlist : list
        List of DBAtom objects
      attribute : str
        Name of the DBAtom attribute to be extracted

    Returns:
      out : numpy array
    '''

    return np.asarray([getattr(atom, attribute) for atom in atomlist])

def get_atoms(session, system_id):
    '''
    From a db row representing a system create ase.Atoms instance and return

    Args:
      session : session
        Session object instance
      system_id : int
        Identifier of the row from the systems table

    Returns:
      atoms : ase.Atoms
        An instance of ase.Atoms class created wih values from a db row
    '''

    q = session.query(System).get(system_id)

    n = len(q.atoms)

    xyz = np.hstack((
        numpify(q.atoms, 'x').reshape(n, 1),
        numpify(q.atoms, 'y').reshape(n, 1),
        numpify(q.atoms, 'z').reshape(n, 1),
    ))

    momenta = np.hstack((
        numpify(q.atoms, 'momentum_x').reshape(n, 1),
        numpify(q.atoms, 'momentum_y').reshape(n, 1),
        numpify(q.atoms, 'momentum_z').reshape(n, 1),
    ))

    atoms = Atoms(
        numbers=numpify(q.atoms, 'atomic_number'),
        positions=xyz,
        momenta=momenta,
        tags=numpify(q.atoms, 'tag'),
        masses=numpify(q.atoms, 'mass'),
        magmoms=numpify(q.atoms, 'magmom'),
        charges=numpify(q.atoms, 'charge'),
    )

    atoms.set_cell(cellpar_to_cell([q.cell_a, q.cell_b, q.cell_c,
                                    q.cell_alpha, q.cell_beta, q.cell_gamma]))
    atoms.set_pbc([q.pbc_a, q.pbc_b, q.pbc_c])

    return atoms

def get_template(session, ids):

    if isinstance(ids, int):
        q = session.query(ASETemplate).get(ids)
    elif isinstance(ids, (str, unicode)):
        q = session.query(ASETemplate).filter(ASETemplate.name == ids).one()
    return q.template

def atoms2system(atoms, username=None, name=None, framework=None, notes={}):

    dbatoms = []

    inimagm = atoms.get_initial_magnetic_moments()
    inichar = atoms.get_initial_charges()
    #forces = atoms.get_forces()

    for atom, imagm, icharge in zip(atoms, inimagm, inichar):

        dbatoms.append(DBAtom(
            atomic_number=atom.number,
            mass=atom.mass,
            tag=atom.tag,
            x=atom.position[0],
            y=atom.position[1],
            z=atom.position[2],
            momentum_x=atom.momentum[0],
            momentum_y=atom.momentum[1],
            momentum_z=atom.momentum[2],
            charge=atom.charge,
            magmom=atom.magmom,
            initial_magmom=imagm,
            initial_charge=icharge,
        ))

    cellpar = cell_to_cellpar(atoms.get_cell())
    pbc = atoms.get_pbc()

    system = System(
        username=username,
        name=name,
        framework=framework,
        formula=atoms.get_chemical_formula(),
        cell_a=cellpar[0],
        cell_b=cellpar[1],
        cell_c=cellpar[2],
        cell_alpha=cellpar[3],
        cell_beta=cellpar[4],
        cell_gamma=cellpar[5],
        pbc_a=pbc[0],
        pbc_b=pbc[1],
        pbc_c=pbc[2],
        atoms=dbatoms,
        )

    # add the notes to the system instance
    for key, value in notes.items():
        system[key] = value

    # if the calculation was done extract the forces and energies
    if atoms.get_calculator() is not None:
        system.energy = atoms.get_potential_energy()

    return system

def calculator2db(calc, attrs='basic', notes=None):
    '''
    A function to convert the calculator to DBCalculator instance to be stored
    in the database.

    Args:
      calc : Calculator
        Calculator instance to be stored in the database
      attrs: str of list of str
        Attributes of the calculator to be stored in the database. If the value
        is a ``str`` it should be: ``all`` or ``basic`` where either all
        attributes or just a small set are stored respectively. Also a list of
        strings with attributes can be passed directly, then only the specified
        ones will be stored.
      notes : dict
        A dictionary with the key value pairs to identify the calculator in the
        database.

    Returns:
      out : DBCalculator
        DBCalculator instance obtained from the ``calc``
    '''

    # check if the claculator has a get_name method or name attribute
    name = hasattribute(calc, "name")
    # check if the claculator has a get_version method or version attribute
    version = hasattribute(calc, "version")

    dbcalc = DBCalculator(name=name, version=version)

    cases = {'all'   : sorted(calc.__dict__.keys()),
             'basic' : ['calcmode', 'convergence', 'dw', 'kpts', 'pw', 'sigma',
                        'spinpol', 'xc']}

    if isinstance(attrs, str):
        if attrs in ['all', 'basic']:
            attrnames = cases[attrs]
    elif isinstance(attrs, (list, tuple)):
        attrnames = attrs
    else:
        raise ValueError('<attr> should be a <str> or <list>, got: {}'.\
                         format(type(attrs)))

    for a in attrnames:
        if hasattr(calc, a):
            value = getattr(calc, a, None)
            if isinstance(value, (int, float, str, bool)) or value is None:
                dbcalc[a] = value
            else:
                dbcalc[a] = json.dumps(value)

    return dbcalc

def hasattribute(obj, name, default=None):
    '''Check if a given instance has a specified method or attribute'''

    getter = "get_" + name

    method = getattr(obj, getter, None)
    if callable(method):
        out = method()
    elif hasattr(obj, name):
        out = getattr(obj, name)
    else:
        out = default
    return out
