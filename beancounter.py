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

import rrdtool
import re
import os
import logging as log

log.basicConfig(level=log.DEBUG)

BEAN_FILE = "/proc/user_beancounters"
BEAN_VERSION = "2.5"

NUMERIC_LINE = re.compile("^\d+:$")
DB_PATH = "tmp"

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

      if name == "dummy":
        continue

      yield name, parts[1:]

def create_rrd_if_necessarry(db_path, name, fields):
  fields_string = "_".join(fields.keys())
  filename = "%s/%s/%s.rrd" % (db_path, fields_string, name)

  dirname = os.path.dirname(filename)
  if not os.path.exists(dirname):
    os.makedirs(dirname)

  if os.path.exists(filename):
    return filename

  log.info("creating rrd %s", filename)
  dss = []

  for name, type in fields.iteritems():
    ds = "DS:%s:%s:120:0:U" % (name, type)
    dss.append(ds)

  cfs = ["MIN", "MAX", "AVERAGE"]

  # this values make an archive which can be used for at least four
  # graphs. For 24h, 1-2w, 2-5months, 8-24months.
  # the chosen values guarantee that for each graph the RRA provides
  # data for at least 800px width.
  times = [
      "1:1800",   # resolution 1min,  timespan 30h
      "10:2016",  # resolution 10min, timespan 14d
      "210:1025", # resolution 3.5h,  timespan 5months
      "720:1500", # resolution 12h,   timespan 2y
  ]

  rras = []
  for cf in cfs:
    for time in times:
      rras.append("RRA:%s:0.5:%s" % (cf, time))

  rrdtool.create(filename, *(dss + rras))

  return filename

def main():
  ressources = []

  for record in read_bean_file(BEAN_VERSION):
    ressource, (held, maxheld, barrier, limit, failcnt) = record

    filename = create_rrd_if_necessarry(DB_PATH, name=ressource,
        fields={
          "held": "GAUGE",
          "barrier": "GAUGE",
          "limit": "GAUGE"
        })

    data = (held, barrier, limit)
    rrdtool.update(filename, "N:%s" % ":".join(data))

    filename = create_rrd_if_necessarry(DB_PATH, name=ressource,
        fields={"failcnt": "COUNTER" })

    rrdtool.update(filename, "N:%s" % failcnt)

if __name__ == "__main__":
  main()
