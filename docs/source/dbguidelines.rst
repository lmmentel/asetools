Best practices when adding data to the central database
=======================================================

Although there is a extensive flexibility when adding data, all users will benefit from a certain structure, in particular in nomenclature. This document is an attempt to approach a standard.

System.name
-----------
For zeotype structures:
Construct the name by fragments relating to the framework, extrametal ion(s) and adsorbate(s) respectively, e.g.

Al-AFI-Ni1-ethene-H_nonagostic

to name nonagostically bound [Ni-ethene-H]+ in SSZ-24 zeolite, charge-balanced by one Al atom.

For molecules:
- di- and tri-atomics: sum formula
- larger structures: IUPAC nomenclature or trivial names, like isobutene or phenol

System.magnetic_moment
----------------------
Use the total magnetic moment in Bohr magneton per cell. A triplet state (2S+1=3), would have total magnetic moment 2.

System.topology
---------------
- molecules: molecule
- zeolites: three-letter framework code

System.notes
------------
For molecules: define parameters employed in thermochemistry
'geometry': str
   'linear' or 'nonlinear'
'rotational_symmetry_no': int
    any integer larger than 0
'point_group': str
    Schoenflies point group

For zeolites and other crystalline structures:
'space_group': str
    the crystallographic symmetry group



Job.name
--------
Use comma-separated keywords, e.g. 
- 'relax'
- 'relax,freq'

Job.status
----------
Use any of the following
- 'not_started'
- 'finished'
- 'failed'
- other value, if the above are insufficient

Job.inpname
-----------
The name of the file that is passed to python when the job is executed

Job.outname
-----------
- 'relax' jobs: name of trajectory file
- 'freq' jobs: name of pickle file with vibrational energies
- ...

Job.hostname
------------
Of the form 'abel.uio.no'

