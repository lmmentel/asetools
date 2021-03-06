
from ase import Atoms, Atom
import ase.io
from ase.calculators.vasp import Vasp

atoms = ase.io.read('%initial')

calc = Vasp(
        prec='Accurate',
        gga='PE',
        lreal=False,
        ediff=1.0e-8,
        encut=600.0,
        nelmin=5,
        nsw=10000,
        nelm=100,
        ediffg=-0.001,
        ismear=0,
        ibrion=2,
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

ase.io.write('%relaxed', atoms)

