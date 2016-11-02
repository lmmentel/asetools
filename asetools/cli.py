
from __future__ import print_function

import argparse
import os
import ase.io
from ase.build import cut

from .io import write_biosym_car


def trajextract():
    '''
    A CLI interafce to extract atoms object from trajectory file and save it
    to another file
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('traj',
                        help='trajctory file from which atoms will be extracted')
    parser.add_argument('ind',
                        help='index of the image to extracted, defaults to last',
                        type=int,
                        default=-1)
    parser.add_argument('output',
                        help='output file to save the extracted image')

    args = parser.parse_args()

    atoms = ase.io.read(args.traj, index=args.ind)
    ase.io.write(args.output, atoms)
    print('wrote file: {}'.format(args.output))


def traj_to_car():
    '''
    CLI for converting trajectory files to car (BIOSYM archive 3)
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('traj',
                        help='trajectory file')
    parser.add_argument('-o', '--output',
                        default='output.car',
                        help='output file name')
    args = parser.parse_args()

    atoms = ase.io.read(args.traj)

    write_biosym_car(atoms,
                     title='converted from: {}'.format(args.traj),
                     filename=args.output)
    print('wrote file: ', args.output)


def aseconvert():
    'Convert between different formats supported by ASE'

    parser = argparse.ArgumentParser()
    parser.add_argument('inp')
    parser.add_argument('out')
    args = parser.parse_args()

    atoms = ase.io.read(args.inp)
    ase.io.write(args.out, atoms)


def coords(s):
    'return a tuple from a string with three numbers'
    try:
        x, y, z = map(float, s.split(','))
        return x, y, z
    except:
        raise argparse.ArgumentTypeError("Coordinates must be x,y,z")


def modify_cell():
    'Mdify the cell using cut and repeat'

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-x", default=1,
                        help="the scaling factor for the a-vector (from origo)")
    parser.add_argument("-y", default=1,
                        help="the scaling factor for the b-vector (from origo)")
    parser.add_argument("-z", default=1,
                        help="the scaling factor for the c-vector (from origo)")
    parser.add_argument("--origo", default=(0.5, 0.5, 0.5), type=coords,
                        help="Position of origo of the new cell in scaled coordinates")
    parser.add_argument("-t", "--tolerance", default=0.01, type=float,
                        help="Determines what is defined as a plane. All atoms within tolerance "
                        "Angstroms from a given plane will be considered to belong to that plane.")
    args = parser.parse_args()

    base, ext = os.path.splitext(args.input)

    if not args.output:
        args.output = base + "_translated" + ext

    mol = ase.io.read(args.input)
    new_mol = cut(mol, a=(args.x, 0, 0), b=(0, args.y, 0), c=(0, 0, args.z),
                  origo=args.origo, tolerance=args.tolerance)
    ase.io.write(args.output, new_mol)
