"""
Store experiment level configuration here, this module also provides functions
for loading configuration in via external files, to allow better modularity
between different projects.
"""

DATA_PATH = "/Users/chstansbury/Research/lanzara/data/"
SOURCE_PATH = "/Users/chstansbury/PycharmProjects/python-arpes/"

import json

import arpes.constants as consts

CONFIG = {
    'VERSION': '1.0.0',
    'MODE': consts.MODE_ARPES,
    'LATTICE_CONSTANT': consts.LATTICE_CONSTANTS['Bi-2212'],
    'WORK_FUNCTION': 46,
    'LASER_ENERGY': 5.93,
}

def load_json_configuration(filename):
    """
    Flat updates the configuration. Beware that this doesn't update nested data.
    I will adjust if it turns out that there is a use case for nested configuration
    """
    with open(filename) as config_file:
        CONFIG.update(json.load(config_file))