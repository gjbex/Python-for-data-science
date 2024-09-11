#!/usr/bin/env python
#
# This script generates CSV files with random data. It allows to
# specify the number of rows and columns through their types. The 
# format can be tweaked to generate different types of data to test
# various CSV readers.
#
# Usage:
# python generate_csv_files.py --columns <column1_type> <column2_type> ... \
#                              [ --nr-rows <nr_rows> ] \
#                              [ --no-header ] \
#                              [ --separator <separator> ] \
#                              [ --quote <quote> ] \
#                              [ --add-trailing-separator ] \
#                              [ --add-random-spaces-around-values ] \
#                              [ --file-type <file_type> ] \
#                              [ --strings-have-spaces ] \
#                              [ --headers-have-spaces ] \
#                              [ --float-format <float_format> ] \
#                              [ --help ]
#
# The column types can be:
# - int: generates random integers between -1_000 and 1_000
# - float: generates random floating point numbers between -1.e3 and 1.e3
# - string: generates random strings with length between 1 and 10
#
# The file types can be:
# - Windows: uses '\r\n' as end-of-line character
# - Unix: uses '\n' as end-of-line character
# - Mac: uses '\r' as end-of-line character
#
# The default values are:
# - nr-rows = 100
# - separator = ','
# - quote = '"'
# - end-of-line = '\n'
# - float-format = '.6f'

import argparse
import random
import string
import sys


def generate_csv_file(args):
    # Set end-of-line character
    if args.file_type == 'Windows':
        args.end_of_line = '\r\n'
    elif args.file_type == 'Mac':
        args.end_of_line = '\r'
    else:
        args.end_of_line = '\n'

    # Generate header
    if not args.no_header:
        if args.headers_have_spaces:
            header = [f'{args.quote}column {i}{args.quote}' for i in range(1, len(args.columns) + 1)]
        else:
            header = [f'column{i}' for i in range(1, len(args.columns) + 1)]
        print(args.separator.join(header), end=args.end_of_line)

    # Generate rows
    character_set = string.ascii_letters + string.digits
    float_format_str = f'{{value:{args.float_format}}}'
    if args.strings_have_spaces:
        character_set += ' '
    for _ in range(args.nr_rows):
        row = []
        for column in args.columns:
            if column == 'int':
                value = str(random.randint(-1_000, 1_000))
            elif column == 'float':
                value = float_format_str.format(value=random.uniform(-1.e3, 1.e3))
            else:
                s = ''.join(random.choices(character_set, k=random.randint(1, 10)))
                value = f'{args.quote}{s}{args.quote}'
            if args.add_random_spaces_around_values:
                if random.choice([True, False]):
                    value = f' {value}'
                if random.choice([True, False]):
                    value = f'{value} '
            row.append(value)
        if args.add_trailing_separator:
            row.append(args.separator)
        print(args.separator.join(row), end=args.end_of_line)


def main():
    parser = argparse.ArgumentParser(description='Generate CSV files with random data.')
    parser.add_argument('--columns', nargs='+', required=True,
            choices=['int', 'float', 'string'], help='List of column types')
    parser.add_argument('--nr-rows', type=int, default=100,
            help='Number of rows')
    parser.add_argument('--no-header', action='store_true',
            help='Do not include header in the CSV file')
    parser.add_argument('--separator', default=',',
            help='Separator character')
    parser.add_argument('--quote', default='"',
            help='Quote character')
    parser.add_argument('--add-trailing-separator', action='store_true',
            help='Add trailing separator to rows')
    parser.add_argument('--add-random-spaces-around-values', action='store_true',
            help='Add random spaces around values')
    parser.add_argument('--file-type', default='Unix',
            choices=['Windows', 'Unix', 'Mac'], help='Type of file')
    parser.add_argument('--strings-have-spaces', action='store_true',
            help='Add spaces to strings')
    parser.add_argument('--headers-have-spaces', action='store_true',
            help='Add spaces in header names')
    parser.add_argument('--float-format', default='.6f',
            help='Format for floating point values')
    args = parser.parse_args()

    # Generate CSV file
    generate_csv_file(args)


if __name__ == '__main__':
    main()
    sys.exit(0)
