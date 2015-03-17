#!/usr/bin/env python
from ase.io import write,read
import numpy as np
from sys import path
from gpaw import GPAW
from ase.visualize import view
from ase.optimize import BFGS
from ase.constraints import FixAtoms
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin/mypython')
from mypython import smart_cell

Hzeo = read('$Hzeofile') #read zeolite including  proton
Hzeo.set_pbc(False)
zeo = read('$zeofile') #read anion
zeo.set_pbc(False)

h = 0.2
xc = 'BEEF-vdW'

Hzeocalc = GPAW(h=h,xc=xc,kpts=(1,1,1),txt='AH.txt')
zeocalc = GPAW(h=h,xc=xc,kpts=(1,1,1),charge=-1,txt='A-.txt')

for atoms,calc,name in zip([Hzeo,zeo],[Hzeocalc,zeocalc],['AH','A-']):
  indices = [atom.index for atom in atoms if atom.symbol == 'H' and not atom.index == 164]
  c = FixAtoms(indices)
  atoms.set_constraint(c)
  smart_cell(atoms,vac=4.2,h=h)
  atoms.set_calculator(calc)
  atoms.get_potential_energy()
  qn = BFGS(atoms, logfile='qn_%s.log' % name,trajectory=name+'.traj')
  qn.run(fmax=0.03)
