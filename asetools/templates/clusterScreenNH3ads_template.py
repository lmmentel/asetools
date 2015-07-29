#!/usr/bin/env python
from ase.io import write,read
import numpy as np
from sys import path
from gpaw import GPAW
from ase.visualize import view
from ase.optimize import BFGS
from ase.constraints import FixAtoms
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin/asetools')
from asetools import smart_cell

atoms = read('$NH4zeofile') #start guess for NH4ads complex
atoms.set_pbc(False)

h = 0.2
xc = 'BEEF-vdW'

calc = GPAW(h=h,xc=xc,kpts=(1,1,1),txt='gpaw.txt')
NH4indices = [165,166,167,168]

indices = [atom.index for atom in atoms if atom.symbol == 'H' and not atom.index in NH4indices]
c = FixAtoms(indices)
atoms.set_constraint(c)
smart_cell(atoms,vac=4.2,h=h)
atoms.set_calculator(calc)
qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.03)
