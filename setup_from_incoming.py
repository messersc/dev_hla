#!/usr/bin/env python3

from __future__ import print_function # python 2

import argparse
import csv
import glob
import os
import os.path
import sys

def enumerate_samples(f):
    """Enumerate (sample_name, our_name) pairs from TSV file"""
    reader = csv.reader(f, delimiter='\t')
    header = None
    for row in reader:
        # handle reading of the header, transform into index/key mapping
        if header is None:
            header = row
            header[0] = header[0][1:]
            header = dict(enumerate(header))
            continue
        # handle each row
        donor = row[0]
        for i, sample_name in enumerate(row[1:], 1):
            sample_type = header[i]
            our_name = '{}_{}'.format(donor, sample_type)
            yield(sample_name, our_name)

def run_setup(args):
    """Perform the setup from the incoming triplets file."""
    # Enumerate pairs of known incoming sample names to our identifier in the samples
    # folder (will consist of the donor identifier and a semantic sample identifier)
    for sample_name, our_name in enumerate_samples(args.incoming_triplets):
        # Compute source path for the given sample
        glob_pattern = os.path.join(args.base_dir, 'incoming', '*', sample_name)
        source_candidates = glob.glob(glob_pattern)
        if len(source_candidates) != 1:
            print('Found {} candidates from pattern {}, must have exactly 1'.format(
                len(source_candidates), glob_pattern, file=sys.stderr))
            return 1

        # Compute destination path
        dest = os.path.join(args.base_dir, 'samples', our_name, 'fastq', 'original')
        source = source_candidates[0]
        print('creating {}'.format(dest), file=sys.stderr)
        print('    from {}/*.f*q.gz'.format(source), file=sys.stderr)
        print('', file=sys.stderr)

        # Create output directory
        if not os.path.exists(dest):
            os.makedirs(dest)

        # Compute source files to link.
        source_files = glob.glob(os.path.join(source, '*.f*q.gz'))
        for f in source_files:
            relative_path = os.path.relpath(f, dest)
            name = os.path.basename(f)
            dest_name = os.path.join(dest, name)
            print('    linking {}'.format(dest_name), file=sys.stderr)
            print('         => {}'.format(relative_path), file=sys.stderr)
            if os.path.exists(dest_name):
                print('    *NOTICE* already exists, ignoring', file=sys.stderr)
            else:
                os.symlink(relative_path, dest_name)
        print('', file=sys.stderr)

def main():
    """Script's entry point."""

    # Get default base dir
    default_base_dir = os.path.dirname(os.path.realpath(__file__))
    default_base_dir = os.path.realpath(os.path.join(default_base_dir, '..'))

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Setup Hummel project from incoming subdir.')
    parser.add_argument('--base-dir', help='path to directory', default=default_base_dir)
    parser.add_argument('--incoming-triplets', help='path to incoming_triplets.tsv',
                        required=True, type=argparse.FileType('r'))
    args = parser.parse_args()

    # Print options
    print('Hummel project setup...\n', file=sys.stderr)
    print('base dir\t{}'.format(args.base_dir), file=sys.stderr)
    print('triplets file\t{}'.format(args.incoming_triplets.name), file=sys.stderr)
    print('', file=sys.stderr)

    run_setup(args)

if __name__ == '__main__':
    sys.exit(main())
