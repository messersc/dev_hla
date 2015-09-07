#!/usr/bin/env python3

import argparse
import datetime
import getpass
import json
import os.path
import random
import sys

DONOR_PREFIX = 'D'
SAMPLE_PREFIX = 'S'

PROJECT_TABLE = 'project.tsv'
DONOR_TABLE = 'donor.tsv'
SAMPLE_TABLE = 'sample.tsv'

PROJECT_KEYS = ['institution', 'organization', 'pi', 'project_pk']
DONOR_KEYS = ['donor_pk', 'customer_id', 'project_pk', 'added_by',
              'added_at', 'info_json']
SAMPLE_KEYS = ['sample_pk', 'customer_id', 'donor_pk', 'project_pk',
               'added_by', 'added_at', 'info_json']


def table_path(fname):
    """Return path to file with table of the given name"""
    return os.path.join(os.path.dirname(__file__), fname)


class Project:
    """Record from the projects.tsv"""

    def __init__(self, institution, organization, pi, project_pk,
                 *other_entries):
        self.institution = institution
        self.organization = organization
        self.pi = pi
        self.project_pk = project_pk
        self.other_entries = other_entries

    def to_tsv(self):
        return '\t'.join([self.institution, self.organization, self.pi,
                          self.project_pk])


class Donor:
    """Record from the donors.tsv"""

    def __init__(self, donor_pk, customer_id, project_pk, added_by,
                 added_at, info):
        self.donor_pk = donor_pk
        self.customer_id = customer_id
        self.project_pk = project_pk
        self.added_by = added_by
        self.added_at = added_at
        self.info = info

    def to_tsv(self):
        return '\t'.join([self.donor_pk, self.customer_id, self.project_pk,
                          self.added_by, self.added_at,
                          json.dumps(self.info, sort_keys=True)])


class Sample:
    """Record from the samples.tsv"""

    def __init__(self, sample_pk, customer_id, donor_pk, project_pk, added_by,
                 added_at, info):
        self.sample_pk = sample_pk
        self.customer_id = customer_id
        self.donor_pk = donor_pk
        self.project_pk = project_pk
        self.added_by = added_by
        self.added_at = added_at
        self.info = info

    def to_tsv(self):
        return '\t'.join([self.sample_pk, self.customer_id, self.donor_pk,
                          self.project_pk, self.added_by, self.added_at,
                          json.dumps(self.info, sort_keys=True)])


def all_projects():
    """Returns iterable of all known projects"""
    path = table_path(PROJECT_TABLE)
    # check that the project_pk is no duplicate
    with open(path, 'rt') as f:
        header = None
        for i, line in enumerate(f):
            if not header:
                header = line
                continue  # read header, no processing
            line = line.strip()
            arr = line.split('\t')
            yield Project(*arr)


def all_donors():
    """Returns iterable of all known donors"""
    path = table_path(DONOR_TABLE)
    # check that the donor_pk is no duplicate
    with open(path, 'rt') as f:
        header = None
        for i, line in enumerate(f):
            if not header:
                header = line
                continue  # read header, no processing
            line = line.strip()
            arr = line.split('\t')
            arr[-1] = json.loads(arr[-1])
            yield Donor(*arr)


def all_samples():
    """Returns iterable of all known samples"""
    path = table_path(SAMPLE_TABLE)
    # check that the sample_pk is no duplicate
    with open(path, 'rt') as f:
        header = None
        for i, line in enumerate(f):
            if not header:
                header = line
                continue  # read header, no processing
            line = line.strip()
            arr = line.split('\t')
            arr[-1] = json.loads(arr[-1])
            yield Sample(*arr)


def generate_pk(prefix, known_pks):
    known_pks = set(known_pks)
    alph = [chr(ord('0') + i) for i in range(10)] + \
        [chr(ord('a') + i) for i in range(26)]
    LEN = 5
    while True:
        key = prefix + ''.join([alph[random.randint(0, len(alph) - 1)]
                               for i in range(LEN)])
        if key not in known_pks:
            return key


def main_add_sample(args):
    print('adding sample to file sample.tsv...', file=sys.stderr)
    # check that the project and donor are known and fit together
    projects = dict([(p.project_pk, p) for p in all_projects()])
    if args.project_pk not in projects.keys():
        raise Exception('Project {} not known!'.format(args.project_pk))
    donors = dict([(p.donor_pk, p) for p in all_donors()])
    if args.donor_pk not in donors.keys():
        raise Exception('Donor {} not known!'.format(args.donor_pk))
    if donors[args.donor_pk].project_pk != args.project_pk:
        raise Exception('Donor {} not in project {}'.format(
            args.donor_pk, args.project_pk))

    path = table_path(SAMPLE_TABLE)
    # create table if necessary
    if not os.path.exists(path):
        print('sample table {} does not exist, writing header'.format(path),
              file=sys.stderr)
        with open(path, 'wt') as f:
            print('#' + '\t'.join(SAMPLE_KEYS), file=f)

    # warn about duplicate customer ids
    for sample in all_samples():
        if sample.customer_id == args.customer_id:
            if args.force:
                print('WARNING: duplicate sample with customer id '
                      '{}, overridden with --force'.format(args.customer_id))
            else:
                tpl = ('ERROR: duplicate sample with customer id '
                       '{}, override with --force')
                raise Exception(tpl.format(args.customer_id))

    # generate primary sample, without duplicates
    known_pks = [d.sample_pk for d in all_samples()]
    sample_pk = generate_pk(SAMPLE_PREFIX, known_pks)

    # convert --info=key=value args into key/value pairs in dict
    infos = {}
    for info in args.infos:
        key, value = info.split('=', 1)
        infos[key] = value

    # append sample record
    with open(path, 'at') as f:
        sample = Sample(sample_pk, args.customer_id, args.donor_pk,
                        args.project_pk, args.added_by, args.added_at,
                        infos)
        print(sample.to_tsv(), file=f)
        # print sample_pk for easy shell usage
        print(sample.sample_pk, file=sys.stdout)


def main_add_donor(args):
    print('adding donor to file donor.tsv...', file=sys.stderr)
    # check that the project is known
    projects = dict([(p.project_pk, p) for p in all_projects()])
    if args.project_pk not in projects.keys():
        raise Exception('Project {} not known!'.format(args.project_pk))

    path = table_path(DONOR_TABLE)
    # create table if necessary
    if not os.path.exists(path):
        print('donor table {} does not exist, writing header'.format(path),
              file=sys.stderr)
        with open(path, 'wt') as f:
            print('#' + '\t'.join(DONOR_KEYS), file=f)

    # warn about duplicate donor ids
    for donor in all_donors():
        if donor.customer_id == args.customer_id:
            if args.force:
                print('WARNING: duplicate donor with customer id '
                      '{}, overridden with --force'.format(args.customer_id))
            else:
                tpl = ('ERROR: duplicate donor with customer id '
                       '{}, override with --force')
                raise Exception(tpl.format(args.customer_id))

    # generate primary donor, without duplicates
    known_pks = [d.donor_pk for d in all_donors()]
    donor_pk = generate_pk(DONOR_PREFIX, known_pks)

    # convert --info=key=value args into key/value pairs in dict
    infos = {}
    for info in args.infos:
        key, value = info.split('=', 1)
        infos[key] = value

    # append donor record
    with open(path, 'at') as f:
        donor = Donor(donor_pk, args.customer_id, args.project_pk,
                      args.added_by, args.added_at, infos)
        print(donor.to_tsv(), file=f)
        # print donor_pk for easy shell usage
        print(donor.donor_pk, file=sys.stdout)


def main_add_project(args):
    print('adding project to file project.tsv...', file=sys.stderr)
    path = table_path(PROJECT_TABLE)
    # create table if necessary
    if not os.path.exists(path):
        print('project table {} does not exist, writing header'.format(path),
              file=sys.stderr)
        with open(path, 'wt') as f:
            print('#' + '\t'.join(PROJECT_KEYS), file=f)

    # check that the project_pk is no duplicate
    for i, project in enumerate(all_projects()):
        if project.project_pk == args.project_pk:
            tpl = 'Duplicate project PK {} in line {}'
            raise Exception(tpl.format(args.project_pk, i + 2))

    # append project record
    with open(path, 'at') as f:
        project = Project(args.institution, args.organization, args.pi,
                          args.project_pk)
        print(project.to_tsv(), file=f)
        # print project_pk for consistency
        print(project.project_pk, file=sys.stdout)


def main_check(args):
    project_pks = set()
    donor_pks = set()
    sample_pks = set()
    all_good = False

    print('Checking project table...', file=sys.stderr)
    for p in all_projects():
        if p.project_pk in project_pks:
            print('ERROR: duplicate projekt PK {}'.format(p.project_pk),
                  file=sys.stderr)
            all_good = False
        project_pks.add(p.project_pk)

    print('Checking donor table...', file=sys.stderr)
    for p in all_donors():
        if p.project_pk not in project_pks:
            print('ERROR: unknown project PK {}'.format(p.project_pk))
            all_good = False
        if p.donor_pk in donor_pks:
            print('ERROR: duplicate donor PK {}'.format(p.donor_pk),
                  file=sys.stderr)
            all_good = False
        donor_pks.add(p.donor_pk)

    print('Checking sample table...', file=sys.stderr)
    for p in all_samples():
        if p.project_pk not in project_pks:
            print('ERROR: unknown project PK {}'.format(p.project_pk))
            all_good = False
        if p.sample_pk in sample_pks:
            print('ERROR: duplicate sample PK {}'.format(p.sample_pk),
                  file=sys.stderr)
            all_good = False
        sample_pks.add(p.sample_pk)

    return 0 if all_good else 1


def main():
    parser = argparse.ArgumentParser(prog='manage_table')
    parser.add_argument('--verbose', action='store_true',
                        help='verbose output')
    subparsers = parser.add_subparsers(
        dest='command', help='sub-command help')

    # command line interface for table checking
    p_project = subparsers.add_parser(
        'check', help='check all tables')

    # command line interface for 'project' table
    p_project = subparsers.add_parser(
        'add_project', help='add an entry to the project table')
    p_project.add_argument('--institution', type=str, required=True,
                           help='Institution, e.g., "BIH"')
    p_project.add_argument('--organization', type=str, required=True,
                           help='Organization , e.g., "T-cell immunotherapy"')
    p_project.add_argument('--pi', type=str, required=True,
                           help='PI, e.g., "Hummel, Michael"')
    p_project.add_argument('--project-pk', type=str, required=True,
                           help='project primary key, e.g., "TCELL2015"')

    # command line interface for donor table
    p_donor = subparsers.add_parser(
        'add_donor', help='add an entry to the donor table')
    p_donor.add_argument('--force', default=False, action='store_true',
                         help='add even in the case of duplicate customer ids')
    p_donor.add_argument('--customer-id', required=True, type=str,
                         help='id given by customer')
    p_donor.add_argument('--project-pk', required=True, type=str,
                         help='project primary key, e.g., "TCELL2015"')
    p_donor.add_argument('--added-by', type=str, default=getpass.getuser(),
                         help='name of the one adding the record')
    p_donor.add_argument('--added-at', type=str,
                         default=datetime.datetime.now().isoformat(),
                         help='name of the one adding the record')
    p_donor.add_argument('--info', action='append', type=str, default=[],
                         dest='infos',
                         help='key=value pair with additional information')

    # command line interface for sample table
    p_donor = subparsers.add_parser(
        'add_sample', help='add an entry to the sample table')
    p_donor.add_argument('--force', default=False, action='store_true',
                         help='add even in the case of duplicate customer ids')
    p_donor.add_argument('--customer-id', required=True, type=str,
                         help='id given by customer')
    p_donor.add_argument('--donor-pk', required=True, type=str,
                         help='PK of the donor')
    p_donor.add_argument('--project-pk', required=True, type=str,
                         help='project primary key, e.g., "TCELL2015"')
    p_donor.add_argument('--added-by', type=str, default=getpass.getuser(),
                         help='name of the one adding the record')
    p_donor.add_argument('--added-at', type=str,
                         default=datetime.datetime.now().isoformat(),
                         help='name of the one adding the record')
    p_donor.add_argument('--info', action='append', type=str, default=[],
                         dest='infos',
                         help='key=value pair with additional information')

    try:
        args = parser.parse_args()
        if args.command == 'add_project':
            return main_add_project(args)
        elif args.command == 'add_donor':
            return main_add_donor(args)
        elif args.command == 'add_sample':
            return main_add_sample(args)
        elif args.command == 'check':
            return main_check(args)
        else:
            parser.print_help()
    except Exception as e:
        print('An error occured!', file=sys.stderr)
        print(e, file=sys.stderr)
        raise

if __name__ == '__main__':
    sys.exit(main())
