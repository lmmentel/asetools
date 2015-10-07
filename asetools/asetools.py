
'''asetools package'''

import os
import sys
import numpy as np
import math
from ase import Atom
import ase.io
from asetools import submit
from scipy.constants import value
from collections import Counter
from string import Template

N_A = value('Avogadro constant')
eV2J = value('electron volt-joule relationship')
Ry_to_eV = value('Rydberg constant times hc in eV')
# inverse cm to eV relationship is m1_to_eV*100.0
m1_to_eV = value('inverse meter-electron volt relationship')

class AseTemplate(Template):
    'A subclass of the string.Template with altered delimiter and extra methods'

    delimiter = '%'
    idpattern = r'[a-z][_a-z0-9]*'

    def get_keys(self):
        '''Parse the string and return a dict with possible keys to substitute.
        For most use case only the `named` fields are interesting'''

        keys = {}
        match = self.pattern.findall(self.template)
        for k, v in self.pattern.groupindex.items():
            keys[k] = [x[v-1] for x in match if x[v-1] != '']
        return keys

    def render_and_write(self, subs, output='input.py'):
        '''
        Write a file rendered template to a file.

        Args:
          subs : dict
            Subsitution to be made in the template string
          output : str
            Name of the file to be written
        '''

        rendered = self.substitute(subs)
        with open(output, 'w') as fout:
            fout.write(rendered)

def eV_to_kJmol(energy):
    '''
    Convert the energy from eV to kJ/mol

    Args:
      energy : float
        Energy in eV
    '''

    return energy*eV2J*N_A/1000.0

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
    execfile(fpath, siteinfo)
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

def list_templates():
    '''Return a list of all the available template file names'''

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")
    return os.listdir(path)

def get_template(tname=None):
    '''
    Return the contents of the template file *tname* if it can be found in the
    templates path, otherwise raise an error.

    Args:
      tname : str
        Name of the template file

    Returns:
      contents : str
        Contents of the file *tname* as `str`

    Raises:
      ValueError:
        when `tname` is `None`
      IOerror:
        when template file cannot be found
    '''

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")
    tempfilepath = os.path.join(path, tname)

    if tname is None:
        raise ValueError("File name not specified")

    if os.path.exists(tempfilepath):
        with open(tempfilepath) as tfile:
            contents = tfile.read()
        return contents
    else:
        raise IOError("File: '{f:s}' not found in {p:s}".format(f=tname, p=path))

def interp_positions(image1, image2, no=1):
    images = []
    ipos = image1.get_positions()
    dpos = (image2.get_positions() - ipos)/(no+1.0)
    for i in range(no):
        image = image1.copy()
        image.set_positions(ipos+dpos*(i+1))
        images.append(image)
    return images

def get_maxforce(atoms):
    try:
        return np.sqrt(np.sum(atoms.get_forces()**2., axis=1)).max()
    except:
        raise

def swap(a, i, j):
    '''Swap items i and j in the list a'''

    a[i], a[j] = a[j], a[i]
    return a

def swap_atompositions(atoms, i, j):
    '''Swap the positions of atom no i and j in an atoms object'''

    atoms.set_positions(swap(atoms.get_positions(), i, j))

def swap_atoms(atoms, i, j):
    '''Swap the atoms no i and j in an atoms object'''

    swap_atompositions(atoms, i, j)
    symbol_i = atoms[i].symbol
    index_i = atoms[i].index
    atoms[i].symbol = atoms[j].symbol
    atoms[i].index = atoms[j].index
    atoms[j].symbol = symbol_i
    atoms[j].index = index_i

def move_atom(atoms, i, j):
    '''function that moves atom i to position j'''

    newsymbols = atoms.get_chemical_symbols()
    pos = atoms.get_positions()
    if j < i:
       newsymbols = np.delete(np.insert(newsymbols,j,atoms[i].symbol),i+1)
       newpos = np.concatenate((pos[:j],[pos[i]],pos[j:i],pos[i+1:]))
    else:
       newsymbols = np.insert(np.delete(newsymbols,i),j,atoms[i].symbol)
       newpos = np.concatenate((pos[:i],pos[i+1:j+1],[pos[i]],pos[j+1:]))
    atoms.set_chemical_symbols(newsymbols)
    atoms.set_positions(newpos)
    return

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
  '''returns the Si/Al ratio for an ase.Atoms object'''
  c = Counter(atoms.get_chemical_symbols())
  return round(c['Si']/float(c['Al']),1)

def smart_cell(s, vac=5.0, h=0.2):
    '''
    Returns the Atoms object centered in a cell with a size that ensures
    minimum vac distance to the cell wall in all directions, and adapts the
    cell to yield exactly the grid spacing h (only relevant for real-space grid
    codes like gpaw). For single atoms the cell is non-cubic to break symmetry.
    '''
    s.center(vac)
    pos = s.get_positions()
    x = np.max(pos[:,0]) - np.min(pos[:,0])
    y = np.max(pos[:,1]) - np.min(pos[:,1])
    z = np.max(pos[:,2]) - np.min(pos[:,2])
    a = np.array([x,y,z])
    b = a + np.array([2.*vac,2.*vac,2.*vac])
    c = np.zeros(3)
    for i in range(len(c)):
        v = b[i]
        gpts = v / h
        rem = np.mod(gpts, 4)
        c[i] = v+(4-rem)*h
    if len(s) == 1:
        c[1] += 4*h
        c[2] += 8*h
    s.set_cell(c)
    s.center()

def set_init_magmoms(atoms, magset):
    '''sets initial magmoms for elements specified in magset. E.g. ('Ni',1.0)
    will set the initial magnetic moment of all Ni atoms to 1.0'''

    indxs = []
    for name,magmom in magset:
        idxs = get_indices_by_symbols(atoms,name)
        magvals = [magmom]*len(idxs)
        indxs += zip(idxs,magvals)
    if indxs == [] and magset != []:
        print 'Error: no elements of specified type present. Exiting...'
    else:
        set_init_magmoms_from_indxs(atoms,indxs)

def set_init_magmoms_from_indxs(atoms, indxs):
    '''sets initial magmoms for atoms specified in indxs. E.g (1, 1.0) will set
    the initial magnetic moment of atoms[1] to 1.0'''

    magmoms = atoms.get_initial_magnetic_moments()
    new_magmoms = [0.0 for _ in magmoms]
    for (atom, magmom) in indxs:
        new_magmoms[atom] = magmom
    atoms.set_initial_magnetic_moments(new_magmoms)


def create_single_job(workdir, atoms, template, subs, jobname='input.py',
        submitargs=None):
    '''
    Create a directory for a job and write the initial structure and job script
    to it.

    Args:
      workdir : str
        Name of the directory for the job
      atoms : ase.Atoms
        Atoms object with the initial geometry
      template : str
        ASE template string with the job description
      subs : dict
        Dictionary of items to be substituted into the template
      jobname : str
        Name of the ase job script
      submitargs : list
        List of string attributes to pass to the submitter (submitQE) in order
        to send the job to the queue

    '''

    os.mkdir(workdir)
    os.chdir(workdir)
    ase.io.write(subs['atoms'], atoms)
    t = AseTemplate(template)
    t.render_and_write(subs, output=jobname)
    if submitargs:
        submitargs.insert(0, jobname)
        submit.main(submitargs)
    os.chdir('..')
