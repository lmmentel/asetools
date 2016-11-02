
from collections import OrderedDict

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import ase.io
from ase.data.colors import jmol_colors


def legendplot(cd, size=1, output=None):
    '''
    Plot the values in a color palette as a horizontal array.

    Args:
        cd : dict
            dictionary with labels as keys and lists/tuples or RGB
            values (range 0.0-1.0) as values
        size : float
            scaling factor for size of plot
        output : str
            Name of the output file
    '''

    # sort the dict wrt keys
    cdict = OrderedDict(sorted(cd.items(), key=lambda t: t[0]))

    n = len(cdict)
    f, ax = plt.subplots(1, 1, figsize=(n * size, size))
    ax.imshow(np.arange(n).reshape(1, n),
              cmap=mpl.colors.ListedColormap(list(cdict.values())),
              interpolation="nearest", aspect="auto")
    ax.set_xticks(np.arange(n) - .5)
    ax.set_yticks([-.5, .5])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    for x, label in enumerate(cdict.keys()):
        ax.annotate(label, (x, 0.0), family='sans-serif', fontsize=18 * size,
                    horizontalalignment='center', verticalalignment='center')

    if output is not None:
        plt.savefig(output)


def hex_to_rgb(value):
    'Convert HEX to RGB tuple with values 0-1'

    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):
    'Convert RGB (0-255) to HEX'

    return '#%02x%02x%02x' % rgb


def colordict_to_rgb(atoms, arrayname, colordict):
    'Convert srt values from colordict to RGB tuples'

    cd = dict()
    for label, color in colordict.items():
        if color == 'jmol':
            idx = np.where(atoms.arrays[arrayname] == label)[0][0]
            cd[label] = tuple(jmol_colors[atoms[idx].number])
        else:
            cd[label] = color
    return cd


def get_color_array(atoms, arrayname, colordict):
    '''
    Return the n x 3 array with RGB values per atom mapped from the colordict

    Args:
        atoms : ase.Atoms
        colordict : dict
    '''

    # default color for missing labels
    def_color = (0.800, 0.800, 0.800)

    cd = colordict_to_rgb(atoms, arrayname, colordict)

    labels = atoms.arrays[arrayname].copy()
    colors = np.zeros((len(atoms), 3))

    for label, row in zip(labels, colors):
        row[:] = cd.get(label, def_color)
    return colors


def generate_image(atoms, arrayname, colordict, output,
                   texture='jmol', rotx=0.0, roty=0.0, rotz=0.0,
                   width=None, height=600):
    '''
    Generate an image with custom coloring of the atoms

    Args:
        atoms : ase.Atoms
        arrayname : str
            Name of the array which will be used to map the colors
        colordict : dict
            Dictionary with labels from `arrayname` as keys and
            RGB tuple as values
        output : str
            Name of the output file
        texture : str
            Texture to use for rendering
        rotx : float
            Rotation angle around x axis
        roty : float
            Rotation angle around y axis
        rotz : float
            Rotation angle around z axis
        width : int
            Width of the image
        height : int
            Height of the image
    '''

    assert texture in ['jmol', 'glass', 'ase3', 'vmd']

    if height is not None and width is not None:
        raise ValueError('only one of: "height", "width" can be specified')

    output = output + '.pov'

    # found using ase-gui menu 'view -> rotate'
    rotation = '{x}x, {y}y, {z}z'.format(x=rotx, y=roty, z=rotz)

    natoms = len(atoms)

    colors = get_color_array(atoms, 'labels', colordict)

    # Textures
    tex = [texture, ] * natoms

    # keyword options for eps, pngand pov files
    kwargs = {
        'rotation': rotation,
        'show_unit_cell': 0,
        'colors': colors,
        'radii': None,
    }

    # keyword options for povray files only
    extra_kwargs = {
        'display'      : False,   # Display while rendering
        'pause'        : False,   # Pause when done rendering (only if display)
        'transparent'  : False,   # Transparent background
        'canvas_width' : width,   # Width of canvas in pixels
        'canvas_height': height,  # Height of canvas in pixels
        'camera_dist'  : 50.,     # Distance from camera to front atom
        'image_plane'  : None,    # Distance from front atom to image plane
                                  # (focal depth for perspective)
        'camera_type'  : 'perspective',   # perspective, ultra_wide_angle
        'point_lights' : [],              # [[loc1, color1], [loc2, color2],...]
        'area_light'   : [(2., 3., 40.),  # location
                    '     White',         # color
                          .7, .7, 3, 3],  # width, height, Nlamps_x, Nlamps_y
        'background'   : 'White',         # color
        'textures'     : tex,     # Length of atoms list of texture names
        'celllinewidth': 0.05,    # Radius of the cylinders representing the cell
    }

    # Make the color of the glass beads semi-transparent
    # colors2 = np.zeros((natoms, 4))
    # colors2[:, :3] = colors
    # colors2[:, 3] = 0.95
    kwargs['colors'] = colors
    kwargs.update(extra_kwargs)

    # Make the raytraced image
    ase.io.write(output, atoms, run_povray=True, **kwargs)
