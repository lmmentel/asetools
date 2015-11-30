Working with the database
=========================

Accessing the database
----------------------

The database is called `smn_kvantekjemi_test`. It is hosted at `dbpg-hotel-utv.uio.no`
and currently is only accessible from `abel.uio.no`.

Direct access
^^^^^^^^^^^^^

.. warning::

   This access method is discuraged unless you know **exactly** what you are
   doing since it can corrupt the database schema or data.


To connect to the PostgreSQL_ prompt, type

.. code-block:: bash

   $ psql -h dbpg-hotel-utv.uio.no -U smn_kvantekjemi_test_user smn_kvantekjemi_test

you will then be asked for a password, and after prividing the prompt will show
up.

Python API
^^^^^^^^^^

The preferred method of accessing the database is through a Python_ interface
layer based on SQLAlchemy_. To get the ``session`` object use the
:py:func:`get_pgsession <asetools.db.get_pgsession>` function from the
:py:mod:`asetools.db` module. The function requires the password as an argument
and returns the ``session`` object::

    >>> from asetools.db import get_pgesession
    >>> session = get_pgsession('password')

You can also get the database ``engine`` with :py:func:`get_pgengine`::

    >>> from asetools.db import get_pgengine
    >>> engine = get_pgengine('password')

where ``password`` is the actual password for the databse.


Best practices when adding data to the database
-----------------------------------------------

Although there is a extensive flexibility when adding data, all users will
benefit from a certain structure, in particular in nomenclature. The following
is an attempt to approach a standard.

System
^^^^^^

System.name : :class:`str`
    *Molecules*:
        construct the shortest name

        - di- and tri-atomics: sum formula.
        - larger structures: IUPAC nomenclature or trivial names, like isobutene or phenol.

    *Zeotype structures*:
        Construct the name by fragments relating to the framework-substituted atom, the framework, extra-framework ion(s) and adsorbate(s) respectively. E.g. '1Al-AFI-Ni1-ethene-H_nonagostic' to name nonagostically bound [Ni-ethene-H]+ charge-balanced by one Al atom in SSZ-24 zeolite.

    *Transition states*:
        Use '_2_' notation, e.g. '1Al-AFI-CH3-ethene_2_propylium'.

System.magnetic_moment : :class:`float`
    Use the total magnetic moment in Bohr magneton per cell. A triplet state
    (2S+1=3), would have total magnetic moment 2.

System.topology : :class:`str`
    Toplology of the system

    - *Molecules*: 'molecule'
    - *Zeotype structures*: three-letter framework code approved by IZA-SC_.

System.notes : :class:`dict`
    *Molecules*:
        parameters employed in thermochemistry (see: ase.thermochemistry_)
         'geometry' : :class:`str`
            'linear' or 'nonlinear'
         'symmetrynumber' : :class:`int`
            rotational symmetry number.
         'point_group' : :class:`str`
            Schoenflies point group
    *Zeotypes and other crystalline structures*:
        similar information, e.g.
         'space_group' : :class:`str`
            the crystallographic symmetry group
    *Other supplementary information*
        key-value pairs where values can be: :class:`int`, :class:`float`,
        :class:`str`, :class:`bool`


VibrationSet
^^^^^^^^^^^^

VibrationSet.name : :class:`str`
    - 'FHVA', full harmonic vibrational analysis including all atoms in the molecular or crystalline structure.
    - 'PHVA', partial harmonic vibrational analysis including atoms defined by VibrationSet.atom_ids.
    - 'FAVA', anharmonic vibrational analysis.

VibrationSet.atom_ids : :class:`str`
    Comma-separated indices of the atoms (in the associated Atoms object) included in the vibrations.


Job
^^^

Job.name : :class:`str`, as comma-separated keywords
    - 'relax', structure relaxation.
    - 'freq', frequency calculation.
    - 'relax,freq', both of the above in the same job.
    - 'neb', nudged elastic band calculation.
    - other string, if the above are insufficient.

Job.status : :class:`str`
    - 'not_started'
    - 'failed'
    - 'finished'
    - 'TSfinished': if a TS was converged, but the entire band of the 'neb' job did not. 
    - other string, if the above are insufficient.

Job.inpname : :class:`str`
    The name of the file that is passed to python when the job is executed, e.g. input.py.

Job.outname : :class:`str`
    - for 'relax' jobs: name of trajectory file.
    - for 'freq' jobs: name of pickle file with vibrational energies.
    - for 'neb' jobs: comma-separated list of trajectory files along the band.

Job.hostname : :class:`str`
    Of the form 'abel.uio.no'.

DBTemplate
^^^^^^^^^^

DBTemplate.name : :class:`str`
    Use comma-separated keywords, e.g. 'relax', 'relax,freq', 'freq,harmonic-thermo', etc.

DBTemplate.ase_version : :class:`str`
    Use ase.version.version, not mandatory.


.. _PostgreSQL: http://www.postgresql.org/
.. _Python: https://www.python.org/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _ase.thermochemistry: https://wiki.fysik.dtu.dk/ase/ase/thermochemistry/thermochemistry.html#module-ase.thermochemistry
.. _IZA-SC: http://www.iza-structure.org/databases/
