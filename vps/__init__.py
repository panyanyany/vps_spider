# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import logging
import logging.config
import yaml
import os
import sys

from beeprint import pp

THIS_DIR = os.path.dirname(__file__)

# to import utils
sys.path.insert(0, THIS_DIR)

# to import workstation
sys.path.insert(0, os.path.join(THIS_DIR, '../../../..'))

# print(sys.path)
# to import workstation.vendors.scrapy
# sys.path.insert(0, os.path.join(THIS_DIR, '../../../../vendors'))
# from workstation.vendors import scrapy

from utils.src import log_util

log_util.setup()

### setup import directory
# sys.path.insert(0, os.path.join(THIS_DIR, '../../../..'))
# sys.path.insert(0, os.path.join(THIS_DIR, '..'))
