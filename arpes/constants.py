"""
Useful constants for experiments and some useful science facts
Much of this is collected from past students, especially Jeff's 'Cstes.ipf'
"""

import math

MODE_ARPES = 'arpes'
MODE_TRARPES = 'trarpes'
MODE_SARPES = 'sarpes'
MODE_STARPES = 'starpes'

EXPERIMENT_MODES = [
    MODE_ARPES,
    MODE_TRARPES,
    MODE_SARPES,
    MODE_STARPES,
]

TIME_RESOLVED_MODES = [
    MODE_TRARPES,
    MODE_STARPES,
]

SPIN_RESOLVED_MODES = [
    MODE_SARPES,
    MODE_STARPES,
]

def mode_has_spin_resolution(mode):
    return mode in SPIN_RESOLVED_MODES

def mode_has_time_resolution(mode):
    return mode in TIME_RESOLVED_MODES

LATTICE_CONSTANTS = {
    'Bi-2212': 3.83,
    'NCCO': 3.942,
    'Hg-2201': 3.8797,
    'BaFe2As2': 3.9625,
}

# eV, A reasonablish value if you aren't sure for the particular sample
WORK_FUNCTION = 4.38

HBAR = 1.05 * 10**(-34)
HBAR_EV = 6.52 * 10**(-16)

HC = 1239.84172 # in units of eV * nm

HEX_ALPHABET = "ABCDEF0123456789"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHANUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

DEG_PER_RAD = 180 / math.pi
RAD_PER_DEG = math.pi / 180

STRAIGHT_TOF_LENGTH = 0.937206
SPIN_TOF_LENGTH = 1.1456
DLD_LENGTH = 1.1456 # This isn't correct but it should be a reasonable guess


K_INV_ANGSTROM = 0.5123

SPECTROMETER_STRAIGHT_TOF = {
    'length': STRAIGHT_TOF_LENGTH,
}
SPECTROMETER_SPIN_TOF = {
    'length': SPIN_TOF_LENGTH,
}

SPECTROMETER_DLD = {
    'length': DLD_LENGTH,
}