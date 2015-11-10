
from ase.io.cif import parse_cif, tags2atoms
import numpy as np

def read_cif(fileobj, index=-1, store_tags=False, **kwargs):
    """Read Atoms object from CIF file. *index* specifies the data
    block number or name (if string) to return.

    If *index* is None or a slice object, a list of atoms objects will
    be returned. In the case of *index* is *None* or *slice(None)*,
    only blocks with valid crystal data will be included.

    If *store_tags* is true, the *info* attribute of the returned
    Atoms object will be populated with all tags in the corresponding
    cif data block.

    Keyword arguments are passed on to the Atoms constructor."""
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
    labels = np.array([atoms.info['_atom_site_label'][i] for i in kinds], dtype='S5')
    atoms.set_tags(kinds)
    atoms.new_array('labels', labels)
    return atoms
