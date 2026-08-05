#!/usr/bin/env python3
"""Password Stretcher: A tool to generate large password lists from small input wordlists or website names."""
# by TheTechromancer

import argparse
import os
import sys

from password_stretcher.lib.errors import PasswordStretcherError
from password_stretcher.lib.mangler import Mangler
from password_stretcher.lib.policy import PasswordPolicy
from password_stretcher.lib.utils import ReadFiles, ReadSTDIN, human_to_int


def stretcher(options):
    """Main function to handle password stretching based on provided options."""
    if options.minlength is not None and options.maxlength is not None and options.minlength > options.maxlength:
        print('U WOT M8')
        sys.exit(1)


    policy = PasswordPolicy(
        minlength=options.minlength,
        maxlength=options.maxlength,
    )

    sys.stderr.write('[+] Reading input wordlist...')
    mangler = Mangler(
        _input=options.input,
        output_size=options.limit,
        double=options.double,
        deconstruct=options.deconstruct,
        perm=options.permutations,
        leet=options.leet,
        cap=options.cap,
        capswap=options.capswap,
        pend=options.pend,
    )
    sys.stderr.write(f' read {len(mangler.input):,} words {"(after basic cap mutations)" if (options.cap and not options.capswap) else ""}\n')
    if options.permutations > 1:
        sys.stderr.write(f'[*] Input wordlist after permutations: {len(mangler.mutators[0]):,}\n')
    else:
        sys.stderr.write(f'[*] Output capped at {mangler.output_size:,} words\n')
    if any([mangler.leet, mangler.cap, mangler.pend]):
        sys.stderr.write('[+] Mutations allowed per word:\n')
        for mutator in mangler.mutators[1:]:
            sys.stderr.write(f'       {mutator!s:<16}{mutator.limit:,}\n')
    if policy:
        sys.stderr.write('[+] Filtering based on policy, output size may be reduced\n')

    #sys.stderr.write(f'[+] Estimated output: {len(mangler):,} words\n')

    bytes_written = 0
    wordcounter = 0
    max_size = mangler.output_size if mangler.output_size else 7
    output_buffer = []
    output_buffer_bytes = 0
    flush_threshold = 1_000_000

    for wordcounter, mangled_word in enumerate(mangler, start=1):
        if policy.meets_policy(mangled_word):
            if isinstance(mangled_word, bytes):
                output_word = mangled_word
            elif isinstance(mangled_word, str):
                output_word = mangled_word.encode('utf-8', errors='replace')
            else:
                output_word = str(mangled_word).encode('utf-8', errors='replace')

            line = output_word + b'\n'
            output_buffer.append(line)
            output_buffer_bytes += len(line)
            bytes_written += len(line)

            if output_buffer_bytes >= flush_threshold:
                sys.stdout.buffer.write(b''.join(output_buffer))
                output_buffer = []
                output_buffer_bytes = 0

        else:
            # if the word didn't meet length requirements, increase the limit by 1
            mangler.mutators[-1].cur_limit += 1        
        if wordcounter >= max_size:
            if output_buffer:
                sys.stdout.buffer.write(b''.join(output_buffer))
            sys.stderr.write('\r[!] Reached the end. Quiting.\n')
            sys.exit(0)  # exit if no new words were written in the last second

    if output_buffer:
        sys.stdout.buffer.write(b''.join(output_buffer))
    sys.stdout.buffer.flush()


def main():

    parser = argparse.ArgumentParser(description='FETCH THE PASSWORD STRETCHER')
    parser.add_argument('-i', '--input', nargs='+', default=ReadSTDIN(), help='input website or wordlist(s) (default: STDIN)', metavar='')
    parser.add_argument('--limit', type=human_to_int, help='limit length of output (default: max(100M, 1000x input))')
    mangling = argparse.ArgumentParser.add_argument_group(parser, 'mangling options')
    mangling.add_argument('-L', '--leet', action='store_true', help='"leetspeak" mutations')
    mangling.add_argument('-c', '--cap', action='store_true', help='common upper/lowercase variations')
    mangling.add_argument('-C', '--capswap', action='store_true', help='all possible case combinations')
    mangling.add_argument('-p', '--pend', action='store_true', help='append/prepend common digits & special characters')
    mangling.add_argument('-d', '--deconstruct', action='store_true', help='extract smaller words from input list')
    mangling.add_argument('-dd', '--double', action='store_true', help='double each word (e.g. "Pass" --> "PassPass")')
    mangling.add_argument('-P', '--permutations',type=int, default=1, help='max permutation depth (careful! massive output)', metavar='INT')
    filters = argparse.ArgumentParser.add_argument_group(parser, 'password complexity filters')
    filters.add_argument('--minlength', type=int, metavar='8', help='minimum password length')
    filters.add_argument('--maxlength', type=int, metavar='16', help='maximum password length')

    try:

        options = parser.parse_args()
        if not isinstance(options.input, ReadSTDIN):
            options.input = ReadFiles(*options.input)

        # print help if there's nothing to stretch
        if isinstance(options.input, ReadSTDIN) and sys.stdin.isatty():
            parser.print_help()
            sys.stderr.write('\n\n[!] Please specify wordlist(s) or pipe to STDIN\n')
            sys.exit(2)
        # If input is not ReadSTDIN, process as needed (removed read_uris call)
        # You may need to implement your own URI reading logic here if required.


        stretcher(options)


    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
    except (PasswordStretcherError, AssertionError) as e:
        sys.stderr.write(f'\n[!] {e}\n')
        sys.exit(1)
    except argparse.ArgumentError:
        sys.stderr.write('\n[!] Check your syntax. Use -h for help.\n')
        sys.exit(2)
    except KeyboardInterrupt:
        sys.stderr.write('\n[!] Interrupted.\n')
        sys.exit(2)


if __name__ == '__main__':
    main()
