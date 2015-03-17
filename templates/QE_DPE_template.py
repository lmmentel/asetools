#!/usr/bin/env python
from ase.io import write,read
import numpy as np
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin')
from espresso import espresso
from ase.visualize import view

encut = $pw
dcut = $dw
xc = '$xc'

Hzeo = read('$read') #read zeolite including  proton
zeo = Hzeo.copy()
Hindex = [atom.index for atom in zeo if atom.symbol=='H']
proton = zeo[Hindex].copy() #get isolated proton at same position as in zeolite
del zeo[Hindex] #generate anion

Hzeocalc = espresso(pw=encut,dw=dcut,xc=xc,kpts=$kpts,outdir='AH')
zeocalc = espresso(pw=encut,dw=dcut,xc=xc,kpts=$kpts,tot_charge=-1,outdir='A-')
protoncalc = espresso(pw=encut,dw=dcut,xc=xc,kpts=$kpts,tot_charge=+1,outdir='H+')

es = []

for atoms,calc,name in zip([Hzeo,zeo,proton],[Hzeocalc,zeocalc,protoncalc],['AH','A-','H+']):
	atoms.set_calculator(calc)
	es.append(atoms.get_potential_energy())
	calc.stop()
	write(name+'.traj',atoms)

print 'DPE: %.4f eV (electronic energy)' % (es[1]-es[0]-es[2])
