#!/usr/bin/env python
#Template input for a structure and cell relaxation with Quantum Espresso
from ase.io import read, write
from espresso import Espresso
from asetools import set_init_magmoms

calc = Espresso(pw=$pw,dw=$dw,
                xc='$xc',
                london=$grimme, #DFT-D2 dispersion correction
                kpts = $kpts,
                sigma = $sigma, #Fermi smearing 
                convergence={'energy':1e-6}, #default
                spinpol=$spinpol,
                charge=$charge,
                )

atoms = read('$input')
set_init_magmoms(atoms,[$magmoms])

atoms.set_calculator(calc)

calc.relax_cell_and_atoms(fmax=$fmax)

final = calc.get_final_structure()
final.set_calculator(calc)
final.get_potential_energy()

write('$output',final)
