# -*- coding: utf-8 -*-

'''A module with methods for managing jobs through a database'''

import os
import pickle

import logging

import ase.io
from ase.geometry import cell_to_cellpar
from ase.thermochemistry import HarmonicThermo, IdealGasThermo

from ..asetools import AseTemplate
from ..submit import main as sub
from .model import Job, System, VibrationSet
from .dbinterface import vibrations2db, atoms2db, get_atoms
from .utils import sanitizestr


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class JobManager(object):
    ''' database oriented job manager '''

    def __init__(self, session):

        self.session = session

    def get_thermo(self, systems, thermo='Harmonic', vibsetname='PHVA',
                   **kwargs):
        '''
        For a list of specified :py:class:`System <asetools.db.model.System>`
        intances create and return a corresponding list of thermochemistry
        instances based on the electronic energy in
        :py:class:`System <asetools.db.model.System>`, vibrations in
        :py:class:`VibrationSet <asetools.db.model.VibrationSet>` and thermo type.

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            thermo : str
                Name of the thermochemical model to use, `Harmonic` or `IdealGas`
            vibsetname : str
                Name of the vibration set to select
        '''

        out = []
        for system in systems:
            energy = system.energy
            vibset = self.session.query(VibrationSet).\
                filter(VibrationSet.name == vibsetname).\
                filter(VibrationSet.system_id == system.id).one()
            vibenergies = vibset.vibenergies

            if thermo == 'Harmonic':
                out.append(HarmonicThermo(vibenergies, energy))
            elif thermo == 'IdealGas':
                atoms = get_atoms(self.session, system.id)
                out.append(IdealGasThermo(vibenergies, kwargs.pop('geometry'),
                                          potentialenergy=energy, atoms=atoms,
                                          **kwargs))

        return out

    def insert_jobs(self, systems, jobname, workdir, temp_id=None,
                    calc_id=None, hostname='abel.uio.no', commit=True):
        '''
        Create :py:class:`Job <asetools.db.model.Job>` instances  and insert
        them into the db.

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            jobname : str
                Name of the job see docs
            workdir : str
                Path to the workdir
            temp_id : int
                Template ID
            calc_id : int
                Calculator ID
            hostname : str
                Name of the host
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        sanitized = sanitizestr(jobname)

        if jobname.find('relax') > -1:
            outname = 'relaxed.traj'
        elif jobname == 'freq':
            outname = 'vibenergies.pckl'
        elif jobname == 'thermo':
            outname = 'thermo.pckl'
        elif jobname == 'single':
            outname = 'singlepoint.traj'
        else:
            outname = sanitized + '.pkl'

        for syst in systems:
            djob = Job(
                abspath=os.path.join(workdir, sanitizestr(syst.name)),
                hostname=hostname,
                inpname=sanitized + '.py',
                outname=outname,
                name=jobname,
                status='not started',
                template_id=temp_id,
                calculator_id=calc_id,
                username=os.getenv('USER'))

            syst.jobs.append(djob)
            self.session.add(syst)
        if commit:
            self.session.commit()
        else:
            self.session.rollback()

    def insert_neb(self, ts_name, initial_name, final_name, workdir, temp_id=9,
                   calc_id=1, nimage=5, springc=0.1, climb=True, magmoms='',
                   fmax=0.2, commit=True):
        '''
        Create a new `System` entry and  neb `Job` and insert both into the
        database

        Args:
            ts_name : str
                Name of the transitions state `System` to be created
            initial_name : str
                Name of the `System` which will be the initial state for the
                neb
            final_name : str
                Name of the `System` which will be the final state of the neb
            workdir : str
                Working directory
            temp_id : int
                Template ID
            calc_id : int
                Calculator ID
            nimage : int
                Number of NEB images
            springc : float
                Spting constant see:: https://wiki.fysik.dtu.dk/ase/ase/neb.html
            climb : bool
                Use climbing image see:: https://wiki.fysik.dtu.dk/ase/ase/neb.html
            magmoms : str
                Magnetic moments
            fmax : float
                Force threshold for the optimizer
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        initial = self.session.query(System).\
            filter(System.name == initial_name).one()
        final = self.session.query(System).\
            filter(System.name == final_name).one()

        tst = System(name=ts_name, topology=initial.topology)

        self.insert_jobs([tst], jobname='neb', workdir=workdir,
                         temp_id=temp_id, calc_id=calc_id, commit=commit)

        repls = {'initial': 'initial.traj',
                 'final': 'final.traj',
                 'nimage': nimage,
                 'springc': springc,
                 'climb': climb,
                 'magmoms': magmoms,
                 'fmax': fmax}

        self.write_jobs([tst], 'neb', subs=[repls], commit=commit)

        # write initial and final structures into the working directory of the job
        nebjob = next(j for j in tst.jobs if j.name == 'neb')
        for struct, name in zip([initial, final], ['initial.traj', 'final.traj']):
            atoms = get_atoms(self.session, struct.id)
            ase.io.write(os.path.join(nebjob.abspath, name), atoms)

    def insert_vibs(self, systems, relaxname='relax', calc_id=1, temp_id=8,
                    vibname='freq,thermo', hostname='abel.uio.no',
                    commit=True):
        '''
        Create :py:class:`Job <asetools.db.model.Job>` instances for
        calculating the vibrations and/or thermochemistry and insert them into
        the db.

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            relaxname : str
                Name of the job (referencing `Job.name`) in which the geometry
                was relaxed
            vibname : str
                Name of the job (referencing `Job.name`) for the frequency
                calculation
            temp_id : int
                Template ID
            calc_id : int
                Calculator ID
            hostname : str
                Name of the host
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for system in systems:
            relaxjob = next(j for j in system.jobs if j.name == relaxname)

            sanitized = sanitizestr(vibname)

            freqjob = Job(
                abspath=os.path.join(relaxjob.abspath, sanitized),
                calculator_id=calc_id,
                hostname=hostname,
                inpname=sanitized + '.py',
                name=vibname,
                outname=u'vibenergies.pckl',
                status=u'not started',
                template_id=temp_id,
                jobscript=None,
                username=os.getenv('USER'))

            system.jobs.append(freqjob)
            self.session.add(system)

        if commit:
            self.session.commit()
        else:
            self.session.rollback()

    def submit_jobs(self, systems, jobname, subargs=None, commit=True):
        '''
        Submit/resubmit selected jobs for specified systems

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            jobname : str
                Name of the job to submit, referencing `Job.name`
            subargs : list
                List of `str` argument to be passed to `asetools.submit.main`
                and then to the scheduler
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for system in systems:
            job = next(j for j in system.jobs if j.name == jobname)

            os.chdir(job.abspath)
            if subargs is not None:
                arglist = [job.inpname] + subargs
            else:
                arglist = [job.inpname, '-t', '120:00:00', '-n', '2']
            # submit the job
            sub(arglist)

            # update job status
            job.status = 'submitted'
            self.session.add(job)

        if commit:
            self.session.commit()
        else:
            self.session.rollback()

    def update_vibs(self, systems, jobname, vibfile='vibenergies.npy',
                    vibname='PHVA', thermofile=None, T=298.15, p=100000,
                    verbose=False, jobstatus='finished', commit=True):
        '''
        Update frequencies and thermochemistry in the database for the
        `systems` from the jobs with the name `jobname`.

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            jobname : str
                Name of the job for which the data in system should be updated
            vibfile : str
                Name of the file with the `ase.Vibrations` object
            vibname : str
                Name for the vibrations
            thermofile : str
                Name of the file with the Thermochemistry
            T : float
                Temperature for thermochemistry calculation in `K`
            p : pressure
                Pressure for thermochemistry calculation in `Pa`
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for mol in systems:
            job = next(j for j in mol.jobs if j.name == jobname)
            job.jobscript = open(job.inppath, 'r').read()
            job.status = jobstatus

            if os.path.exists(os.path.join(job.abspath, vibfile)):
                vibset = vibrations2db(os.path.join(job.abspath, vibfile), name=vibname)
                mol.vibrationsets.append(vibset)

            if thermofile is not None:
                if os.path.exists(os.path.join(job.abspath, thermofile)):
                    with open(os.path.join(job.abspath, thermofile), 'rb') as fthermo:
                        thermo = pickle.load(fthermo)

                    thermoname = thermo.__class__.__name__
                    mol.thermo = thermoname + '@{:.2f}'.format(T)

                    if thermoname in ['HarmonicThermo', 'CrystalThermo']:
                        viben = thermo.vib_energies
                        if getattr(thermo, 'electronicenergy', None) is not None:
                            poten = thermo.electronicenergy
                        else:
                            poten = thermo.potentialenergy

                        thermo = HarmonicThermo(viben, poten)
                        mol.entropy = thermo.get_entropy(T, verbose=verbose)
                        mol.internal_energy = thermo.get_internal_energy(T, verbose=verbose)
                        # older version of ase have gibbs free energy instead of
                        # helmholtz
                        #try:
                        #mol.free_energy = thermo.get_gibbs_energy(T, verbose=verbose)
                        mol.free_energy = thermo.get_helmholtz_energy(T, verbose=verbose)
                    elif thermoname == 'IdealGasThermo':
                        mol.entropy = thermo.get_entropy(T, p, verbose=verbose)
                        mol.enthalpy = thermo.get_enthalpy(T, verbose=verbose)
                        mol.free_energy = thermo.get_gibbs_energy(T, p, verbose=verbose)
                    else:
                        raise ValueError('Unknown thermoname: {}'.format(thermoname))

            self.session.add(mol)
            self.session.add(job)
        if commit:
            self.session.commit()
        else:
            self.session.rollback()

    def update_geoms(self, systems, jobname, jobstatus='finished',
                     commit=True):
        '''
        Update the database for the `systems` from the jobs `jobname`

        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            jobname : str
                Name of the job for which the data in system should be updated
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for mol in systems:
            job = next(j for j in mol.jobs if j.name == jobname)
            job.jobscript = open(job.inppath, 'r').read()
            job.status = jobstatus

            atoms = ase.io.read(str(job.outpath), format='traj')

            dbatoms = atoms2db(atoms)
            mol.atoms = dbatoms
            cellpar = cell_to_cellpar(atoms.get_cell())
            pbc = atoms.get_pbc()
            mol.cell_a = cellpar[0]
            mol.cell_b = cellpar[1]
            mol.cell_c = cellpar[2]
            mol.cell_alpha = cellpar[3]
            mol.cell_beta = cellpar[4]
            mol.cell_gamma = cellpar[5]
            mol.pbc_a = bool(pbc[0])
            mol.pbc_b = bool(pbc[1])
            mol.pbc_c = bool(pbc[2])
            mol.formula = atoms.get_chemical_formula()
            mol.energy = atoms.get_potential_energy()
            mol.absolute_magnetization = atoms.get_absolute_magnetization()
            mol.total_magnetization = atoms.get_total_magnetization()
            self.session.add(mol)
            self.session.add(job)

        if commit:
            self.session.commit()
        else:
            self.session.rollback()

    def write_jobs(self, systems, jobname, subs=None, submit=False,
                   submitargs=None, overwrite=False, commit=True,
                   write_struct=False, struct_fname='initial.traj'):
        '''
        Render the template file into an input script for the job, write the
        file and submit the job (if requested).

        Args:
            systems : list
                List of `asetools.db.model.System` instances
            jobname : str
                Name of the job to be created
            subs : dict
                Dictionary with key, value pairs to be rendered into the job
                template, they will overwrite the values obtained from the
                calculator specified in the job
            submit : bool
                A flag to specify whether to submit the job or not
            submitargs : list of strings
                A list of arguments for the batch program used to submit the
                job
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for system in systems:
            job = next(j for j in system.jobs if j.name == jobname)
            atemp = AseTemplate(job.template.template)

            # create a dictionary with replacements for the template by getting
            # the matching values from the calculator attributes absed on keys
            # from the template
            subs2render = {k: job.calculator[k] for k in atemp.get_keys()['named'] \
                           if k in job.calculator.attributes.keys()}

            # update the values with the ones supplied by the user
            if subs is not None:
                subs2render.update(subs)

            # check if all the template keys have values before rendering the
            # tempate
            if len(set(atemp.get_keys()['named']) - set(subs2render.keys())) == 0:
                job.create_job(subs2render, overwrite)
            else:
                print('Not writing input for {0}, missing values for: {1}'.format(
                    system.name, str(set(atemp.get_keys()['named']) - set(subs2render.keys()))))

            if write_struct:

                path = job.abspath

                atoms = get_atoms(self.session, system.id)
                ase.io.write(os.path.join(path, struct_fname), atoms)

                log.info('wrote file {} in {}'.format(struct_fname, path))
        if submit:
            self.submit_jobs(systems, jobname, submitargs, commit)

    def write_vibs(self, systems, subs, relaxname='relax', vibname='freq',
                   submit=False, subargs=None, overwrite=False, commit=True):
        '''
        Args:
            systems : list
                List of :py:class:`System <asetools.db.model.System>` instances
            subs : dict
                Dictionary with key, value pairs to be rendered into the job
                template, they will overwrite the values obtained from the
                calculator specified in the job
            relaxname : str
                Name of the job (referencing `Job.name`) in which the geometry
                was relaxed
            vibname : str
                Name of the job (referencing `Job.name`) for the frequency calculation
            submit : bool
                A flag to specify whether to submit the job or not
            subargs : list of strings
                A list of arguments for the batch program used to submit the job
            overwrite : bool
                If True the previous the job dir will be overwritten if it exists
            commit : bool
                Flag to mark whether to commit changes or not
        '''

        for system in systems:
            relaxjob = next(j for j in system.jobs if j.name == relaxname)
            vibjob = next(j for j in system.jobs if j.name == vibname)
            atemp = AseTemplate(vibjob.template.template)

            # create a dictionary with replacements for the template by getting the
            # matching values from the calculator attributes absed on keys from the
            # template
            subs2render = {k: vibjob.calculator[k] for k in atemp.get_keys()['named'] \
                           if k in vibjob.calculator.attributes.keys()}

            # update the values with the ones supplied by the user
            subs2render.update(subs)
            # use the relaxed geometry for calculating the frequency
            subs2render['atoms'] = relaxjob.outpath

            # check if all the template keys have values before rendering the tempate
            if len(set(atemp.get_keys()['named']) - set(subs2render.keys())) == 0:
                vibjob.create_job(subs2render, overwrite)
            else:
                print('Not writing input for {0}, missing values for: {1}'.format(
                    system.name, str(set(atemp.get_keys()['named']) - set(subs2render.keys()))))

        if submit:
            self.submit_jobs(systems, vibname, subargs, commit)
