from ase.io import read
from ase.optimize import BFGS
from espresso import iEspresso
from asetools import set_init_magmoms,smart_cell

calc = iEspresso(pw=%pw,dw=%dw,
                xc=%xc,
		london=%grimme, #DFT-D2 dispersion correction
                kpts = %kpts,
                sigma = %sigma, #Fermi smearing	
		isolated=%screening, #assuming the system to be isolated (a molecule or a cluster in a 3D supercell)
                convergence={'energy':1e-10}, #default
                spinpol=%spinpol,
		charge=%charge,
                )

atoms = read(%input)
set_init_magmoms(atoms,%magmoms)
atoms.set_calculator(calc)
smart_cell(atoms,vac=7.5,h=0.01) #create cell with equal vacuum spacing of vac Aa in all directions. NB! grid spacing parameter h only matters for a real-space code!'

qn = BFGS(atoms, logfile='qn.log',trajectory=%output)
qn.run(fmax=%fmax,steps=%steps)
