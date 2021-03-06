#!/usr/bin/python
# Copyright (c) TurnKey GNU/Linux - http://www.turnkeylinux.org
#
# This file is part of Pool
#
# Pool is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

"""Get packages from pool

  If a package is specified without a version, get the newest package.
  If no packages are specified as arguments, get all the newest packages.

Options:
  -i --input <file>	file from which we read package list (- for stdin)
    
  -s --strict		fatal error on missing packages
  -q --quiet		suppress warnings about missing packages

  -t --tree		output dir is in a package tree format (like a repository)

"""
import sys
import help
import getopt

from os.path import *
import re

from pool import Pool

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] <output-dir> [ package[=version] ... ]" % sys.argv[0]


exitcode = 0
def warn(s):
    global exitcode
    exitcode = 1
    
    print >> sys.stderr, "warning: " + str(s)
    
def fatal(s):
    print >> sys.stderr, "error: " + str(s)
    sys.exit(1)

def read_packages(fh):
    packages = []
    for line in fh.readlines():
        line = re.sub(r'#.*', '', line)
        line = line.strip()
        if not line:
            continue
        packages.append(line)
    return packages
    
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'i:sqt',
                                       ['input=', 'strict', 'quiet', 'tree'])
    except getopt.GetoptError, e:
        usage(e)

    if not args:
        usage()

    outputdir = args[0]
    packages = args[1:]

    input = None
    opt_strict = False
    opt_quiet = False
    opt_tree = False
    
    for opt, val in opts:
        if opt in ('-i', '--input'):
            if val == '-':
                input = sys.stdin
            else:
                input = file(val, "r")
        elif opt in ('-s', '--strict'):
            opt_strict = True
        elif opt in ('-q', '--quiet'):
            opt_quiet = True
        elif opt in ('-t', '--tree'):
            opt_tree = True

    pool = Pool()
    
    if input:
        packages += read_packages(input)

    if not args[1:] and not input:
        # if no packages specified, get all the newest versions
        packages = pool.list()

    try:
        packages = pool.get(outputdir, packages, tree_fmt=opt_tree, strict=opt_strict)
    except pool.Error, e:
        fatal(e)

    if not opt_quiet:
        for package in packages.missing:
            warn("no such package (%s)" % package)
            
    sys.exit(exitcode)
        
if __name__=="__main__":
    main()
