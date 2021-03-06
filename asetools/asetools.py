
'''asetools package'''

from __future__ import print_function, division, unicode_literals, absolute_import

from builtins import (bytes, dict, int, list, object, range, str,
                      ascii, chr, hex, input, next, oct, open,
                      pow, round, super, filter, map, zip)

import os
import sys
import math
from collections import Counter
from string import Template
import numpy as np
from scipy.constants import value
from ase import Atom


N_A = value('Avogadro constant')
eV2J = value('electron volt-joule relationship')
Ry_to_eV = value('Rydberg constant times hc in eV')
# inverse cm to eV relationship is m1_to_eV*100.0
m1_to_eV = value('inverse meter-electron volt relationship')
eV_to_m1 = value('electron volt-inverse meter relationship')


class AseTemplate(Template):
    '''
    A subclass of the string.Template with altered delimiter and extra
    methods
    '''

    delimiter = '%'
    idpattern = r'[a-z][_a-z0-9]*'

    def get_keys(self):
        '''Parse the string and return a dict with possible keys to substitute.
        For most use case only the `named` fields are interesting'''

        keys = {}
        match = self.pattern.findall(self.template)
        for k, v in self.pattern.groupindex.items():
            keys[k] = [x[v - 1] for x in match if x[v - 1] != '']
        return keys

    def render_and_write(self, subs, output='input.py', safe=True):
        '''
        Write a file rendered template to a file.

        Args:
          subs : dict
            Subsitution to be made in the template string
          output : str
            Name of the file to be written
        '''

        # add additional quotes for string arguments
        subs = {k: ("'{0:s}'".format(v) if isinstance(v, str) else v)
                for k, v in subs.items()}

        if safe:
            rendered = self.safe_substitute(subs)
        else:
            rendered = self.substitute(subs)
        with open(output, 'w') as fout:
            fout.write(rendered)

    @staticmethod
    def list_templates():
        '''Return a list of all the available template file names'''

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "templates")
        return os.listdir(path)

    @classmethod
    def from_file(cls, tname=None):
        '''
        Instantiates `AseTemplate` from a template file *tname* if it can be
        found in the templates path, otherwise raise an error.

        Args:
          tname : str
            Name of the template file

        Returns:
          contents : AseTemplate
            AseTemplate class instance

        Raises:
          ValueError:
            when `tname` is `None`
          IOerror:
            when template file cannot be found
        '''

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "templates")
        tempfilepath = os.path.join(path, tname)

        if tname is None:
            raise ValueError("File name not specified")

        if os.path.exists(tempfilepath):
            with open(tempfilepath) as tfile:
                contents = tfile.read()
            return cls(contents)
        else:
            raise IOError("File: '{f:s}' not found in {p:s}".format(f=tname,
                                                                    p=path))


def eV_to_kJmol(energy):
    '''
    Convert the energy from eV to kJ/mol

    Args:
      energy : float
        Energy in eV
    '''

    return energy * eV2J * N_A / 1000.0


def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z


def get_config(fname=None):
    '''
    Retrieve the information on the batch submission and environment from
    the asetools_site_config.py'''

    if fname is None:
        fname = ".asetools_site_config.py"
        fpath = os.path.join(os.getenv("HOME"), fname)
    else:
        fpath = fname

    siteinfo = {}
    exec(open(fpath).read(), siteinfo)
    return siteinfo['config']


def which(prog):
    '''
    Python equivalent of the unix which command, returns the absolute path of
    the "prog" if it is found on the system PATH.

    Args:
      prog : str
        Program name (execuatable)

    Returns:
      fprog : str
        Path to the executable
    '''

    if sys.platform == "win32" and os.path.splitext(prog)[1].lower() != '.exe':
        prog += '.exe'
    for path in os.getenv('PATH').split(os.path.pathsep):
        fprog = os.path.join(path, prog)
        if os.path.exists(fprog) and os.access(fprog, os.X_OK):
            return fprog


def interp_positions(image1, image2, no=1):
    images = []
    ipos = image1.get_positions()
    dpos = (image2.get_positions() - ipos) / (no + 1.0)
    for i in range(no):
        image = image1.copy()
        image.set_positions(ipos + dpos * (i + 1))
        images.append(image)
    return images


def get_maxforce(atoms):
    try:
        return get_maxlength(atoms.get_forces())
    except:
        raise


def get_maxlength(vec):
    '''Return the length of the longest vector in an array of vectors'''
    return np.sqrt(np.sum(vec**2.0, axis=1)).max()


def swap(a, i, j):
    '''Swap items i and j in the list a'''

    a[i], a[j] = a[j], a[i]

    return a


def swap_atompositions(atoms, i, j):
    '''Swap the positions of atom no i and j in an atoms object'''
    pos = atoms.get_positions()
    newpos = pos.copy()
    newpos[i] = pos[j]
    newpos[j] = pos[i]
    atoms.set_positions(newpos)
    return atoms


def swap_atoms(atoms, i, j):
    '''Swap the atoms no i and j in an atoms object'''
    acopy = atoms.copy()
    swap_atompositions(atoms, i, j)

    atoms[i].index = j
    atoms[j].index = i
    atoms[i].symbol = acopy[j].symbol
    atoms[j].symbol = acopy[i].symbol
    return atoms


def move_atom(atoms, i, j):
    '''function that moves atom i to position j'''

    a = atoms.copy()
    newsymbols = a.get_chemical_symbols()
    pos = a.get_positions()
    if j < i:
       newsymbols = np.delete(np.insert(newsymbols, j, a[i].symbol), i + 1)
       newpos = np.concatenate((pos[:j], [pos[i]], pos[j:i], pos[i + 1:]))
    else:
       newsymbols = np.insert(np.delete(newsymbols, i), j, a[i].symbol)
       newpos = np.concatenate((pos[:i], pos[i + 1:j + 1], [pos[i]], pos[j + 1:]))
    a.set_chemical_symbols(newsymbols)
    a.set_positions(newpos)
    return a


def get_indices_by_symbols(atoms, symbollist, mode='include'):
    '''
    Function that given an Atoms object and a list of atom symbols returns a
    list of indices of the atoms from the list, that are present in the Atoms
    object. If no atoms are present, an empty list is returned.

    Args:
      atoms : ase.atoms.Atoms
        System of atoms as ase Atoms instance
      symbollist : list
        List of atomic symbols to be included/excluded
      mode : str
        Return either a list of indices for atoms in the ``symbollist``
        or indices of other other than those in ``symbollist``

    Returns:
      out : list
        List of indices
    '''

    if mode == 'include':
        return [atom.index for atom in atoms if atom.symbol in symbollist]
    elif mode == 'exclude':
        return [atom.index for atom in atoms if atom.symbol not in symbollist]
    else:
        raise ValueError('wrong mode: {}, allowed values we: "include" and "exclude"'.format(mode))


def remove_atom_by_symbols(atoms, symbollist):
    '''
    Given a list of atom symbols remove the corresponding atoms from the atoms
    object.
    '''

    del atoms[[atom.index for atom in atoms if atom.symbol in symbollist]]


def substitute_atom(atoms, a1, a2):
    '''
    Funtion that given an Atoms object and two symbols a1 and a2, substitutes
    a1 for a2.
    '''
    indices = get_indices_by_symbols(atoms, a1)
    for i in indices:
        atoms[i].symbol = a2
    return


def attach_atom(atoms, ind, symbol='H', theta=-45.0, r=1.5):
    '''
    Attach an atom to the existing system

    Args:
      atoms : ase.Atoms
        system to which thr atom will be attached
      ind : int
        index of the atom to which to attach the new atom
      symbol : str
        symbol of the new atom that will be attached
      theta : float
        angle at which the new will be positioned with respect to the selected
        atom
      r : float
        distance of the new atom with respect to the selected atom
    '''

    t = math.radians(theta)

    x = atoms[ind].x + r * math.cos(t)
    y = atoms[ind].y + r * math.sin(t)
    z = atoms[ind].z

    h = Atom(symbol=symbol, position=[x, y, z])

    return atoms + h


def attach_molecule(atoms, ind, molecule, theta=-45.0, r=2.5):
    '''
    Attach a molecule `molecule` to atom with index `ind` and return
    the metged system as ase.Atoms instance

    Args:
      atoms : ase.Atoms
        System to which the molecule should be attached
      ind : int
        Index of the atom to which the molecule should be attached
      molecule : ase.Atoms
        A system (*molecule*) that is to be attached/added
      theta : float
        Angle at which the center of mass of the `molecule` will be placed
      r : float
        Distance along angle `theta` at which the center of mass of the
        `molecule` will be placed

    Returns:
      res : ase.Atoms
        atoms instance with the new molecule attached

    .. note::
       It is assumed here that the `molecule` is properly rotated/aligned.
    '''
    mcm = molecule.get_center_of_mass()
    molecule.translate(-mcm)

    t = math.radians(theta)
    cmx = atoms[ind].x + r * math.cos(t)
    cmy = atoms[ind].y + r * math.sin(t)
    cmz = atoms[ind].z
    molecule.translate([cmx, cmy, cmz])
    return atoms + molecule


def get_SiAlratio(atoms):
    'returns the Si/Al ratio for an ase.Atoms object'

    c = Counter(atoms.get_chemical_symbols())
    return round(c['Si'] / float(c['Al']), 1)


def smart_cell(s, vac=5.0, h=0.2):
    '''
    Returns the Atoms object centered in a cell with a size that ensures
    minimum vac distance to the cell wall in all directions, and adapts the
    cell to yield exactly the grid spacing h (only relevant for real-space grid
    codes like gpaw). For single atoms the cell is non-cubic to break symmetry.
    '''
    s.center(vac)
    pos = s.get_positions()
    x = np.max(pos[:, 0]) - np.min(pos[:, 0])
    y = np.max(pos[:, 1]) - np.min(pos[:, 1])
    z = np.max(pos[:, 2]) - np.min(pos[:, 2])
    a = np.array([x, y, z])
    b = a + np.array([2.0 * vac, 2.0 * vac, 2.0 * vac])
    c = np.zeros(3)
    for i in range(len(c)):
        v = b[i]
        gpts = v / h
        rem = np.mod(gpts, 4)
        c[i] = v + (4 - rem) * h
    if len(s) == 1:
        c[1] += 4 * h
        c[2] += 8 * h
    s.set_cell(c)
    s.center()


def set_init_magmoms(atoms, magset):
    '''sets initial magmoms for elements specified in magset. E.g. ('Ni',1.0)
    will set the initial magnetic moment of all Ni atoms to 1.0'''

    indxs = []
    for name, magmom in magset:
        idxs = get_indices_by_symbols(atoms, name)
        magvals = [magmom] * len(idxs)
        indxs += zip(idxs, magvals)
    if indxs == [] and magset != []:
        raise ValueError('Error: no elements of specified type present. Exiting...')
    else:
        set_init_magmoms_from_indxs(atoms, indxs)


def set_init_magmoms_from_indxs(atoms, indxs):
    '''sets initial magmoms for atoms specified in indxs. E.g (1, 1.0) will set
    the initial magnetic moment of atoms[1] to 1.0'''

    magmoms = atoms.get_initial_magnetic_moments()
    new_magmoms = [0.0 for _ in magmoms]
    for (atom, magmom) in indxs:
        new_magmoms[atom] = magmom
    atoms.set_initial_magnetic_moments(new_magmoms)


def find_closest(atoms, reference, symbol=None, n=1):
    '''
    Return a list of indices of atoms closest to the reference atom

    Args:
      atoms : ase.Atoms
        ASE Atoms object
      reference : int
        Index of the reference atom
      symbol : str
        Symbol of the atom that will be taken into account when searching for
        nearest to the refence
      n : int
        Number of nearest atoms to be returned

    Returns:
      out : np.array
        A structured, sorted array with `n` records each composed of an index,
        symbol and distance to reference atoms
    '''

    pos = atoms.get_positions()
    d = np.sqrt(np.power(pos - pos[reference], 2).sum(axis=1))

    out = np.array(zip(range(len(atoms)), atoms.get_chemical_symbols(), d),
            dtype=[('idx', int), ('symbol', '|S2'), ('dist', float)])

    out = out[out['idx'] != reference]
    out = np.sort(out, order='dist')

    if symbol:
        out = out[out['symbol'] == symbol]

    return out[:n]


def get_indices_of_duplicates(lst):
    '''
    Get indices and values of repeated elements in a list

    Returns:
        an array of repeated value and a list of array with indices of
        repeated elements
    '''
    records_array = np.array(lst)
    idx_sort = np.argsort(records_array)
    sorted_records_array = records_array[idx_sort]
    vals, idx_start, count = np.unique(sorted_records_array,
                                       return_counts=True,
                                       return_index=True)

    # sets of indices
    res = np.split(idx_sort, idx_start[1:])

    # filter them with respect to their size,
    # keeping only items occurring more than once
    vals = vals[count > 1]
    res = filter(lambda x: x.size > 1, res)
    return vals, res


def nearest_neighbors_kd_tree(x, y, k):
    '''
    Find unique pairs using KDTree method

    Args:
        x : numpy.array
            points in 3D
        y : numpy.array
            points in 3D
        k : int
            number of nearest neighbors to use

    .. seealso::

       http://stackoverflow.com/questions/15363419/finding-nearest-items-across-two-lists-arrays-in-python

    '''

    from scipy.spatial import cKDTree

    x, y = map(np.asarray, (x, y))
    tree = cKDTree(y)
    ordered_neighbors = tree.query(x, k)[1]
    nearest_neighbor = np.empty((len(x),), dtype=np.intp)
    nearest_neighbor.fill(-1)
    used_y = set()
    for j, neigh_j in enumerate(ordered_neighbors):
        for k in neigh_j:
            if k not in used_y:
                nearest_neighbor[j] = k
                used_y.add(k)
                break
    return nearest_neighbor


def rmsd(a, b, relative=True):
    '''
    Calculate Root Mean Square Deviation of atomic positions between two
    structures.

    Args:
        a : ase.Atoms
            Atoms object
        b : ase.Atoms
            Atoms object
        relative : bool
            If `True` atomic positions relative to the unit cell will be
            used [0--1], otherwise standard positions will be used.

    .. math::

       RMSD(a, b) = \sqrt{\\frac{1}{n} \sum^{n}_{i=1} \left[ (a_{ix} - b_{ix})^2 + (a_{iy} - b_{iy})^2 + (a_{iz} - b_{iz})^2 \\right]}


    '''

    if len(a) != len(b):
        raise ValueError('Atoms have different sizes {0:d} != {1:d}'.format(
            len(a), len(b)))

    if relative:
        pa = a.get_scaled_positions()
        pb = b.get_scaled_positions()
    else:
        pa = a.get_positions()
        pb = b.get_positions()

    return np.sqrt(np.sum(np.sum(np.power(pa - pb, 2), axis=1), axis=0) / len(a))


def assign_magnetic_moments_by_symbols(atoms, magdict, clear=False):
    '''
    Set initial magnetic moments for elements specified in magset.

    Args:
        atoms : ase.Atoms
            Atoms object
        magdict : dict
            Dictionary of magnetic moments to be assigned with chemical
            symbols as keys and magnetic moments as values,
            e.g. ``{'Fe': 4.0}``
        clear : bool
            If ``True`` before assigning the magnetic moments are
            initialized as 0.0, if ``False`` the existing initial
            magnetic moments are used
    '''

    if clear:
        magmoms = np.zeros(len(atoms), dtype=float)
    else:
        magmoms = atoms.get_initial_magnetic_moments()

    for symbol, magm in magdict.items():
        mask = np.array([s == symbol for s in atoms.get_chemical_symbols()])
        magmoms[mask] = magm
        atoms.set_initial_magnetic_moments(magmoms)
        if sum(mask) == 0:
            print("couldn't find <{}> in atoms".format(symbol))
