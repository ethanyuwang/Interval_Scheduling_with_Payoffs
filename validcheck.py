#!/usr/bin/env python3
"""Checks the formatting of output for interval scheduling with payoff problem.

This program executes another program with input from specified file, then
checks whether the output is valid.

"""
import argparse
import itertools
import os
import re
import subprocess
import sys
import tempfile
import time


def main():
    # Obtain program arguments.
    program_args = get_program_args()
    executable = os.path.abspath(program_args.program)
    input_file = os.path.abspath(program_args.test_input)
    output_file = os.path.abspath(program_args.dest_output)
    expected_payoff = program_args.expected_payoff

    # Execute the program and redirecting stdin/stdout through files.
    execute_program(executable, input_file, output_file)

    # Read test input file and program output file.
    # read_program_output may cause error and this program terminates
    input_intervals = read_test_input(input_file)
    written_payoff, selected_intervals = read_program_output(output_file)

    # Check if the output is valid.
    # These functions may terminate this program if error occurs
    check_exists(input_intervals, selected_intervals)
    check_sorted(selected_intervals)
    check_payoff(expected_payoff, written_payoff, selected_intervals)

    # At this point, everything is fine.
    if expected_payoff is None:
        print('Output validation done. No expected payoff sum checking.')
    else:
        print('Output validation done. Payoff is correct.')


def get_program_args():
    """
    Construct and parse the command line arguments to the program.
    """
    parser = argparse.ArgumentParser(
        description='Check the formatting and validity of output of '
        'interval scheduling with payoff.'
        )
    parser.add_argument('program', help='Path to executable file')
    parser.add_argument('test_input', help='Path to test input file')
    parser.add_argument('dest_output', help='Path to destination output file')
    parser.add_argument('expected_payoff', nargs='?', type=int,
                        help='Expected optimal payoff of the test input '
                        '(optional; not used if omitted)')
    program_args = parser.parse_args()
    return program_args


def error_and_exit(message, exit_status=127):
    """
    Print the error message and immediately exit this program.
    """
    print(message, file=sys.stderr)
    print('Terminating...', file=sys.stderr)
    sys.exit(exit_status)


def execute_program(executable, input_file, output_file):
    """
    Use subprocess to execute the file with given input and output paths.
    """
    with open(input_file) as infile, open(output_file, 'w') as outfile:
        start_time = time.time()  # save start time
        try:
            subprocess.check_call(
                [executable], stdin=infile, stdout=outfile, timeout=60
                )
        except subprocess.TimeoutExpired:
            error_and_exit('Your program is exceeding 60 seconds')
        except subprocess.CalledProcessError as e:
            error_and_exit('Your program does not exit normally: '
                           'status {} was returned'.format(e.returncode))
        duration = time.time() - start_time  # duration of execution
        print('Your program terminates normally in {:.3f} seconds'
              .format(duration))


def read_test_input(input_file):
    """
    Return the list of intervals from the test input.
    """
    with open(input_file) as infile:
        return [tuple(int(value) for value in line.split()) for line in infile]


def read_program_output(output_file):
    """
    Return the total payoff and the list of intervals from the program output.
    """
    with open(output_file) as outfile:
        # Extract the payoff
        first_line = next(outfile).strip('\n')
        match = re.fullmatch(r'Max(imum)? Payoff: (?P<payoff>[0-9]+)',
                             first_line)
        try:
            payoff = int(match.group('payoff'))
        except AttributeError:
            error_and_exit('Line {} has incorrect format: "{}"'
                           .format(1, first_line))

        # Extract intervals
        interval_re = re.compile(r'([0-9]+) ([0-9]+) ([0-9]+)')
        intervals = []
        for number, line in enumerate(outfile, start=2):
            line = line.strip('\n')
            match = interval_re.fullmatch(line)
            try:
                interval = tuple(int(v) for v in match.group(1, 2, 3))
            except AttributeError:
                error_and_exit('Line {} has incorrect format: "{}"'
                               .format(number, line))
            intervals.append(interval)
        return payoff, intervals


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def check_exists(input_intervals, selected_intervals):
    """
    Check that each interval in the output is also in the input.
    """
    input_intervals = frozenset(input_intervals)
    for number, interval in enumerate(selected_intervals, start=2):
        if interval not in input_intervals:
            error_and_exit('Line {} has interval not belong to input: {}'
                           .format(number, interval))


def check_sorted(intervals):
    """
    Check that consecutive pair of intervals are ordered and not overlapped.
    """
    for number, (first, second) in enumerate(pairwise(intervals), start=2):
        if first[1] > second[0]:
            error_and_exit('Line {} and {} have conflicting times: {} vs {}'
                           .format(number, number+1, first, second))


def check_payoff(expected_payoff, written_payoff, selected_intervals):
    """
    Check that the total payoff is consistent with the output intervals.
    """
    actual_payoff = sum(interval[2] for interval in selected_intervals)
    if actual_payoff != written_payoff:
        error_and_exit('Output has inconsistent payoff: '
                       'reported {} but the actual payoff is {}'
                       .format(written_payoff, actual_payoff))
    if expected_payoff is not None and written_payoff != expected_payoff:
        error_and_exit('Output payoff does not match expected payoff: '
                       'expected {} but the actual payoff is {}'
                       .format(written_payoff, expected_payoff))


if __name__ == '__main__':
    main()
