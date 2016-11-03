
import datetime

from ase import Atoms
from ase.io.cif import parse_cif, tags2atoms
from ase.geometry import cell_to_cellpar
import numpy as np


def read_cif(fileobj, index=-1, store_tags=False, **kwargs):
    '''
    Read Atoms object from CIF file. *index* specifies the data
    block number or name (if string) to return.

    If `index` is `None` or a slice object, a list of atoms objects will
    be returned. In the case of *index* is `None` or `slice(None)`,
    only blocks with valid crystal data will be included.

    If `store_tags` is true, the `info` attribute of the returned
    Atoms object will be populated with all tags in the corresponding
    cif data block.

    Keyword arguments are passed on to the Atoms constructor.
    '''

    blocks = parse_cif(fileobj)
    if isinstance(index, str):
        tags = dict(blocks)[index]
        return tags2atoms(tags, store_tags=store_tags, **kwargs)
    elif isinstance(index, int):
        name, tags = blocks[index]
        return tags2atoms(tags, store_tags=store_tags, **kwargs)
    elif index is None or index == slice(None):
        # Return all CIF blocks with valid crystal data
        images = []
        for name, tags in blocks:
            try:
                atoms = tags2atoms(tags, store_tags=store_tags)
                images.append(atoms)
            except KeyError:
                pass
        if not images:
            # No block contained a a valid atoms object
            # Provide an useful error by try converting the first
            # block to atoms
            name, tags = blocks[0]
            tags2atoms(tags, store_tags=store_tags)
        return images
    else:
        return [tags2atoms(tags, store_tags=store_tags) for name, tags in blocks[index]]


def read_cif_with_tags(fname):
    '''
    Read a cif file and return ase.Atoms object with an additional numpy.array
    instantiated called `labels` containing the labels for different T and O
    atoms. Tags are initialized to different symmetry uniqe atom kinds

    Args:
      fname : str
        Name of the cif file
    '''

    atoms = read_cif(fname, store_tags=True)
    scaled_positions = np.array([atoms.info['_atom_site_fract_x'],
                                 atoms.info['_atom_site_fract_y'],
                                 atoms.info['_atom_site_fract_z']]).T
    sg = atoms.info['spacegroup']
    spos, kinds = sg.equivalent_sites(scaled_positions)
    labels = np.array([atoms.info['_atom_site_label'][i] for i in kinds],
                      dtype='S5')
    atoms.set_tags(kinds)
    atoms.new_array('labels', labels)
    return atoms


def atoms2df(atoms):
    '''
    Convert `ase.Atoms` object into `pandas.DataFrame`

    atoms : ase.Atoms
        Atoms object
    '''

    import pandas as pd

    data = {k: v for k, v in atoms.arrays.items() if v.ndim == 1}
    data['symbol'] = atoms.get_chemical_symbols()
    data['mass'] = atoms.get_masses()
    data['x'] = atoms.positions[:, 0]
    data['y'] = atoms.positions[:, 1]
    data['z'] = atoms.positions[:, 2]
    return pd.DataFrame(data=data)


def df2atoms(df):
    '''
    Convert a `pandas.DataFrame` to `ase.Atoms`
    '''

    symbols = df['symbol'].values
    positions = df[['x', 'y', 'z']].values

    return Atoms(symbols=symbols, positions=positions)


def write_biosym_car(atoms, title='', filename='output.car'):
    '''
    Write a *car* file in the biosym archive 3 format

    .. seealso::

       http://www.upch.edu.pe/facien/fc/dbmbqf/zimic/cursos/modelamiento%202005/Manuales/Insight%20documentation/doc/formats980/File_Formats_1998.html#781840

    '''

    pars = cell_to_cellpar(atoms.get_cell())
    energy = atoms.get_potential_energy()

    if any([b for b in atoms.get_pbc()]):
        pbc = 'ON'
    else:
        pbc = 'OFF'

    if 'spacegroup' in atoms.info.keys():
        sgname = atoms.info['spacegroup'].symbol
    else:
        sgname = '(P1)'

    date = datetime.datetime.now()

    with open(filename, 'w') as fcar:

        fcar.write('!BIOSYM archive 3\n')
        fcar.write('PBC={0:s}\n'.format(pbc))
        fcar.write(title.ljust(65) + '{0:>15.7f}\n'.format(energy))
        fcar.write('!DATE ' + date.strftime('%a %b %d %H:%M:%S %Y') + '\n')
        fcar.write('PBC' + ''.join(['{0:10.5f}'.format(p) for p in pars]) +
                   ' ' + sgname.ljust(7) + '\n')

        for atom in atoms:
            line = ' '.join([atom.symbol.ljust(5),
                             ' '.join(['{0:14.9f}'.format(c) for c in atom.position]),
                             'XXXX', '1'.ljust(7) + atom.symbol.ljust(7),
                             atom.symbol.ljust(2), '{0:6.3f}\n'.format(atom.number)])
            fcar.write(line)
        fcar.write('end\nend')
