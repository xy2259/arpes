"""
Store experiment level configuration here, this module also provides functions
for loading configuration in via external files, to allow better modularity
between different projects.
"""

import json
import os.path

import arpes.constants as consts

DATA_PATH = '/Users/chstansbury/Research/lanzara/data/'
SOURCE_PATH = '/Users/chstansbury/PycharmProjects/python-arpes/'
DATASET_CACHE_PATH = '/Users/chstansbury/Research/lanzara/data/cache/'

FIGURE_PATH = os.path.join(SOURCE_PATH, 'figures/')

DATASET_CACHE_RECORD = os.path.join(SOURCE_PATH, 'datasets/cache.json')
CLEAVE_RECORD = os.path.join(SOURCE_PATH, 'datasets/cleaves.json')
CALIBRATION_RECORD = os.path.join(SOURCE_PATH, 'datasets/calibrations.json')

# TODO use a real database here
PIPELINE_SHELF = os.path.join(SOURCE_PATH, 'datasets/pipeline.shelf')
PIPELINE_JSON_SHELF = os.path.join(SOURCE_PATH, 'datasets/pipeline.shelf.json')

CONFIG = {
    'VERSION': '1.0.0',
    'MODE': consts.MODE_ARPES,
    'LATTICE_CONSTANT': consts.LATTICE_CONSTANTS['Bi-2212'],
    'WORK_FUNCTION': 46,
    'LASER_ENERGY': 5.93,
    'WORKSPACE': None, # set me in your notebook before saving anything
}

def load_json_configuration(filename):
    """
    Flat updates the configuration. Beware that this doesn't update nested data.
    I will adjust if it turns out that there is a use case for nested configuration
    """
    with open(filename) as config_file:
        CONFIG.update(json.load(config_file))
