
import ase.io
from ase.calculators.vasp import Vasp

import numpy as np
from scipy.constants import value, Planck

from panther.io import read_vasp_hessian
from panther.vibrations import harmonic_vibrational_analysis
from panther.thermochemistry import Thermochemistry

atoms = ase.io.read('%initial')

calc = Vasp(prec='Accurate',
            xc='PBE',
            gga='PE',
            lreal=False,
            ediff=1.0e-8,
            encut=600.0,
            nelmin=5,
            nsw=1,
            nelm=100,
            ediffg=-0.001,
            ismear=0,
            ibrion=5,
            potim=0.02,
            nfree=2,
            isym=0,
            lvdw=True,
            lcharg=False,
            lwave=False,
            istart=0,
            npar=2,
            ialgo=48,
            lplane=True,
            ispin=1,
            )

atoms.set_calculator(calc)
calc.calculate(atoms)

# calculate the frequencies and thermo

hessian, labels = read_vasp_hessian('OUTCAR', symmetrize=True,
                                    convert_to_au=True, dof_labels=True)

frequencies, normal_modes = harmonic_vibrational_analysis(hessian, atoms,
                            proj_translations=True, proj_rotations=True,
                            ascomplex=False)

# save the results
np.save('hessian', hessian)
np.save('frequencies', frequencies)
np.save('normal_modes', normal_modes)

# calculate thermodynamic functions
vibenergies = Planck * frequencies.real * value('hartree-hertz relationship')
vibenergies = vibenergies[vibenergies > 0.0]

thermo = Thermochemistry(vibenergies, atoms, phase='%phase',
                         pointgroup='%group')
thermo.summary(T=273.15, p=0.1)
