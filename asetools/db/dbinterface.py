# -*- coding: utf-8 -*-

'''A module providing methods for communication between ASE and the database'''

import argparse
import json
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np

import ase.io
from ase import Atoms
from ase.geometry import cellpar_to_cell, cell_to_cellpar

from .model import (Base, DBAtom, System, DBTemplate, DBCalculator, Vibration,
                    VibrationSet)


def get_session(dbpath, echo=False):
    '''
    Return the database session connection for the sqlite3 database

    Args:
      dbpath : str
        Path to the database file

    Returns:
      session :
        Session instance
    '''

    if os.path.exists(dbpath):
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=echo)
    else:
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=echo)
        Base.metadata.create_all(engine)
    db_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()


def get_pgsession(passwd, dbapi='psycopg2'):
    '''
    Get the database engine for the postgresql

    Args:
      passwd : str
        Password

    Returns:
      session :
        Session instance
    '''

    engine = create_engine('postgresql+{0:s}://smn_kvantekjemi_test_user:{1:s}@dbpg-hotel-utv.uio.no/smn_kvantekjemi_test'.format(dbapi, passwd))
    db_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()


def get_pgengine(passwd):
    '''
    Get the database engine from the postgresql

    Args:
      passwd : str
        Password

    Returns:
      engine :
        Database engine
    '''

    engine = create_engine('postgresql+psycopg2://smn_kvantekjemi_test_user:{}@dbpg-hotel-utv.uio.no/smn_kvantekjemi_test'.format(passwd))
    return engine


def get_engine(dbpath):
    '''Return the db engine'''

    engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
    return engine


def get_table(tablename, dbpath, **kwargs):
    '''
    Return a table from the database as pandas DataFrame

    Args:
      tablename: str
        Name of the table from the database
      dbpath: str
        Path to the database file
      kwargs:
        A dictionary of keyword arguments to pass to the `pandas.read_qsl`

    Returns:
      df: pandas.DataFrame
        Pandas DataFrame with the contents of the table
    '''

    tables = ['systems', 'calculators', 'asetemplates', 'jobs', 'atoms',
              'vibrations', 'vibrationsets']

    if tablename in tables:
        engine = get_engine(dbpath)
        df = pd.read_sql(tablename, engine, **kwargs)
        return df
    else:
        raise ValueError('Table should be one of: {}'.format(", ".join(tables)))


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
    atoms.info['name'] = q.name
    atoms.info['topology'] = q.topology

    return atoms


def get_template(session, ids):
    'Return a template string based either on the id or name'

    if isinstance(ids, int):
        q = session.query(DBTemplate).get(ids)
    elif isinstance(ids, str):
        q = session.query(DBTemplate).filter(DBTemplate.name == ids).one()
    return q.template


def atoms2db(atoms):
    '''
    Convert `ase.Atoms <https://wiki.fysik.dtu.dk/ase/ase/atoms.html#module-ase.atoms>`_
    object into a list of :py:class:`DBAtom <asetools.db.model.DBAtom>`
    objects and return

    Args:
      atoms : `ase.Atoms <https://wiki.fysik.dtu.dk/ase/ase/atoms.html#module-ase.atoms>`_
        ASE atoms object

    Returns:
      dbatoms : :py:class:`DBAtom <asetools.db.model.DBAtom>`
    '''

    dbatoms = []

    inimagm = atoms.get_initial_magnetic_moments()
    inichar = atoms.get_initial_charges()
    if atoms.get_calculator() is not None:
        try:
            forces = atoms.get_forces()
        except:
            forces = [[None] * 3 for _ in range(len(atoms))]
    else:
        forces = [[None] * 3 for _ in range(len(atoms))]

    for atom, imagm, icharge, force in zip(atoms, inimagm, inichar, forces):

        dbatoms.append(DBAtom(
            atomic_number=int(atom.number),
            mass=atom.mass,
            tag=int(atom.tag),
            x=atom.position[0],
            y=atom.position[1],
            z=atom.position[2],
            force_x=force[0],
            force_y=force[1],
            force_z=force[2],
            momentum_x=atom.momentum[0],
            momentum_y=atom.momentum[1],
            momentum_z=atom.momentum[2],
            charge=atom.charge,
            magmom=atom.magmom,
            initial_magmom=imagm,
            initial_charge=icharge,
        ))

    return dbatoms


def atoms2system(atoms, name=None, topology=None, magnetic_moment=None,
                 notes=None, vibrations=None, vibname=None, atom_ids=None,
                 realonly=False):
    '''
    Instantiate a :py:class:`asetools.db.model.System` from `ase.Atoms`
    objects and additional parameters
    '''

    dbatoms = atoms2db(atoms)

    cellpar = cell_to_cellpar(atoms.get_cell())
    pbc = atoms.get_pbc()

    system = System(
        name=name,
        topology=topology,
        formula=atoms.get_chemical_formula(),
        cell_a=cellpar[0],
        cell_b=cellpar[1],
        cell_c=cellpar[2],
        cell_alpha=cellpar[3],
        cell_beta=cellpar[4],
        cell_gamma=cellpar[5],
        pbc_a=bool(pbc[0]),
        pbc_b=bool(pbc[1]),
        pbc_c=bool(pbc[2]),
        atoms=dbatoms,
        magnetic_moment=magnetic_moment)

    # add the notes to the system instance
    if notes:
        for key, value in notes.items():
            system[key] = value

    # if the calculation was done extract the energy
    if atoms.get_calculator() is not None:
        system.energy = atoms.get_potential_energy()

    # add vibrations, if present
    if vibrations is not None:
        vibset = vibrations2db(vibrations, name=vibname, atom_ids=atom_ids,
                               realonly=realonly)
        system.vibrationsets = [vibset]

    return system


def vibrations2db(vibrations, name=None, atom_ids=None, system_id=None,
                  realonly=False):
    '''
    Instantiate the :py:class:` VibrationSet <asetools.db.model.VibrationSet>`
    from a numpy array containing vibrational energies or a numpy (.npy) file with
    such an array and return.

    Args:
      vibrations: numpy.ndarray or str
        numpy.ndarray of type numpy.complex128 with vibrational energies or
        the name of the numpy (.npy) file with such an array
      name : str
        Name of the set of vibrations
      atom_ids : str
        Comma separated atom ids for which the vibrations were calculated
      system_id : int
        Integer identifier of the system. If VibrationSet will be attached
        to a system this will be automatically filled by sqlalchemy
      realonly : bool
        If True only the real part of vibrational energies should be passed
        in vibrations

    Returns:
      out : :py:class:`VibrationSet <asetools.db.model.VibrationSet>`
    '''

    if isinstance(vibrations, np.ndarray):
        if vibrations.dtype == np.complex and not realonly:
            viblist = [Vibration(energy_real=r, energy_imag=i) for (r, i) in zip(vibrations.real, vibrations.imag)]
        elif realonly:
            viblist = [Vibration(energy_real=r, energy_imag=i) for (r, i) in zip(vibrations, np.zeros_like(vibrations))]
    elif isinstance(vibrations, str):
        array = np.load(vibrations)
        viblist = [Vibration(energy_real=r, energy_imag=i) for (r, i) in zip(array.real, array.imag)]
    else:
        raise ValueError('<vibrations> should be either <str> or <numpy.ndarray> type, got: {}'.format(type(vibrations)))

    vibset = VibrationSet(name=name, atom_ids=atom_ids, system_id=system_id)
    vibset.vibrations = viblist

    return vibset


def calculator2db(calc, attrs='basic', description=None):
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

    dbcalc = DBCalculator(name=name, version=version, description=description)

    cases = {'all'  : sorted(calc.__dict__.keys()),
             'basic': ['calcmode', 'convergence', 'dw', 'kpts', 'pw', 'sigma',
                       'spinpol', 'xc']}

    if isinstance(attrs, str):
        if attrs in ['all', 'basic']:
            attrnames = cases[attrs]
    elif isinstance(attrs, (list, tuple)):
        attrnames = attrs
    else:
        raise ValueError('<attr> should be a <str> or <list>, got: {}'.
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


def from_traj(session, traj, name, topology, notes, calcid=None, tempid=None):
    '''
    Extract the relevant data from the trajectory file and add them as a row
    to the systems table in the database

    Args:
      session : session
        Database connection
      traj : str
        ASE trajectory file with the data
      name : str
        Name of the system to be stored
      topology : str
        Three letter framework topology code
      notes : dict
        Additional properties to be stored with the system (as dict)
      calcid : int
        Calcualtor id from the db
      tempid : int
        DBTemplate id from the db
    '''

    atoms = ase.io.read(traj)
    system = atoms2system(atoms, name=name, topology=topology, notes=notes)

    if calcid:
        system.calculator = session.query(DBCalculator).get(calcid)
    if tempid:
        system.template = session.query(DBTemplate).get(tempid)

    session.add(system)
    session.commit()


def add_system():
    '''
    Add a system to a SQLite3 database from a parsed trajectory file.
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('db', help='database file')
    parser.add_argument('traj', help='trajectory file')
    parser.add_argument('-n', '--name', help='name of the system')
    parser.add_argument('-t', '--topology', help='framework topology code')
    parser.add_argument('-c', '--calcid', help='calculator id')
    parser.add_argument('-a', '--tempid', help='ase template id')
    parser.add_argument('--notes', help='additional system info',
                        default=dict())

    args = parser.parse_args()

    if os.path.exists(args.db):
        session = get_session(args.db)
    else:
        raise ValueError('db does not exist : ', args.db)

    if not os.path.exists(args.traj):
        raise ValueError('traj does not exist : ', args.traj)

    if args.notes:
        args.notes = json.loads(args.notes)

    from_traj(session=session, traj=args.traj, name=args.name,
              topology=args.topology, notes=args.notes,
              calcid=args.calcid, tempid=args.calcid)
