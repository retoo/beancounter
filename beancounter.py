#!/usr/bin/python
# -*- coding: utf8 -*-

# Copyright (c) 2009 Reto Schüttel <reto -(a)- schuettel (o) ch>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Reads the servers4you / VZ Virtual Server bean statistics and creates nice RRD graphs

from __future__ import with_statement

import sys
sys.path.append('/usr/local/rrdtool-1.3.7/lib/python2.5/site-packages/')
import rrdtool

import re

BEAN_FILE = "example_input"
BEAN_VERSION = "2.5"

NUMERIC_LINE = re.compile("^\d+:$")

def read_bean_file(filename):
  with open(BEAN_FILE) as fh:
    for line in fh:
      parts = line.split()

      if parts[0] == "Version:":
        # Version: 2.5
        version = parts[1]

        if version != BEAN_VERSION:
          log.critical("Unexpected bean version %s, script verified for %s, please " +
                       "check for updates" % version, BEAN_VERSION)
          sys.exit(1)

        continue
      if parts[0] == "uid":
        #  uid  resource                     held              maxheld              barrier                limit              failcnt
        # skip column line
        continue
      if NUMERIC_LINE.match(parts[0]):
        # 187099: kmemsize                 10191833             13450533             16934908             18628398                    0
        # scrap first item in uid line
        parts.pop(0)

      name = parts[0]
      values = map(int, parts[1:])
      yield name, values

def main():
  for record in read_bean_file(BEAN_VERSION):
    print record
    resource, (held, maxheld, barrier, limit, failcnt) = record



if __name__ == "__main__":
  main()
