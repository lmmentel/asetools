#Template input for adding a molecule to a zeolite channel
from ase.io import read,write
from ase.optimize import BFGS
from gpaw import GPAW
from asetools import smart_cell
import numpy as np
from ase.visualize import view

zeolite = read('$readpath')
cell = zeolite.get_cell()
xyzvec = 0.45 * (cell[0]+cell[1]) +  $zdisplace*cell[2]
molecule = read('$moleculepath'+'/dyn.traj')
angle = -np.pi*0.40
#molecule.rotate(v='y',a=angle) #all the branched alkanes have to be rotated

pos = molecule.get_positions()
x = (np.max(pos[:,0]) + np.min(pos[:,0])) 
y = (np.max(pos[:,1]) + np.min(pos[:,1])) 
z = (np.max(pos[:,2]) + np.min(pos[:,2]))
molcenter = 0.5 * np.array([x,y,z])
molecule.translate(-1*molcenter)
molecule.translate(xyzvec)

zeolite = zeolite + molecule
write('startguess.traj',zeolite)
