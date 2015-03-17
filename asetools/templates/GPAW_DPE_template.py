#!/usr/bin/env python
from ase.io import write,read
import numpy as np
from sys import path
from gpaw import GPAW
from ase.visualize import view
from ase.optimize import BFGS

Hzeo = read('$read') #read zeolite including  proton
zeo = Hzeo.copy()
Hindex = [atom.index for atom in zeo if atom.symbol=='H']
proton = zeo[Hindex].copy() #get isolated proton at same position as in zeolite
del zeo[Hindex] #generate anion

Hzeocalc = GPAW(h=$h,xc='$xc',kpts=$kpts,txt='AH.txt')
zeocalc = GPAW(h=$h,xc='$xc',kpts=$kpts,charge=-1,txt='A-.txt')
protoncalc = GPAW(h=$h,xc='$xc',kpts=$kpts,charge=1,txt='H+.txt')

es = []

for atoms,calc,name in zip([Hzeo,zeo,proton],[Hzeocalc,zeocalc,protoncalc],['AH','A-','H+']):
	atoms.set_calculator(calc)
	es.append(atoms.get_potential_energy())
	write(name+'.traj',atoms)

qn = BFGS(zeo, logfile='qn.log',trajectory='A-.traj')
qn.run(fmax=0.03)
