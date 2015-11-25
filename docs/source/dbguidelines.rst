Best practices when adding data to the central database
=======================================================

Although there is a extensive flexibility when adding data, all users will benefit from a certain structure, in particular in nomenclature. This document is an attempt to approach a standard.

System
-------

System.name : str
    *Molecules*:
    construct the shortest name
     - di- and tri-atomics: sum formula.
     - larger structures: IUPAC nomenclature or trivial names, like isobutene or phenol.
    *Zeotype structures*:
    Construct the name by fragments relating to the framework, extra-framework ion(s) and adsorbate(s) respectively. E.g. '1Al-AFI-Ni1-ethene-H_nonagostic' to name nonagostically bound [Ni-ethene-H]+ charge-balanced by one Al atom in SSZ-24 zeolite.
    *Transition states*:
    Use '_2_' notation, e.g. '1Al-AFI-CH3-ethene_2_propylium'.

System.magnetic_moment : float
    Use the total magnetic moment in Bohr magneton per cell. A triplet state (2S+1=3), would have total magnetic moment 2.

System.topology : str
    - *Molecules*: 'molecule'
    - *Zeotype structures*: three-letter framework code (str)

System.notes : dict
    *Molecules*:
    parameters employed in thermochemistry
         'geometry'
            'linear' or 'nonlinear'
         'rotational_symmetry_no'
            any integer larger than 0
         'point_group'
            Schoenflies point group (str)
    *Zeotypes and other crystalline structures*:
    similar information, e.g.
         'space_group'
            the crystallographic symmetry group (str)
    *Other supplementary information*:


Vibrations
----------
To come


Job
---

Job.name : str
    Use comma-separated keywords, e.g. 'relax', 'relax,freq' or 'neb'.

Job.status : str
    - 'not_started'
    - 'finished'
    - 'failed'
    - other value, if the above are insufficient

Job.inpname : str
    The name of the file that is passed to python when the job is executed, e.g. input.py.

Job.outname : str
    - for 'relax' jobs: name of trajectory file
    - for 'freq' jobs: name of pickle file with vibrational energies
    - for 'neb' jobs: comma-separated list of trajectory files along the band

Job.hostname : str
    Of the form 'abel.uio.no'

DBTemplate
----------

DBTemplate.name : str
    Use comma-separated keywords, e.g. 'relax', 'relax,freq', 'freq,harmonic_thermo', etc.

DBTemplate.ase_version : str
    Use ase.version.version, not mandatory.

