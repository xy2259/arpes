import datetime
import errno
import itertools
import os.path
import numpy as np
import matplotlib.offsetbox
import matplotlib
from matplotlib.lines import Line2D

from collections import Counter

import matplotlib.pyplot as plt

from arpes.config import CONFIG, FIGURE_PATH
from arpes.typing import DataType
from utilities import normalize_to_spectrum

__all__ = ['path_for_plot', 'path_for_holoviews', 'name_for_dim', 'label_for_colorbar', 'label_for_dim',
           'label_for_symmetry_point', 'savefig', 'AnchoredHScaleBar', 'calculate_aspect_ratio', 'unit_for_dim',]

def calculate_aspect_ratio(data: DataType):
    data = normalize_to_spectrum(data)

    assert(len(data.dims) == 2)

    x_extent = np.ptp(data.coords[data.dims[0]].values)
    y_extent = np.ptp(data.coords[data.dims[1]].values)

    return y_extent / x_extent

class AnchoredHScaleBar(matplotlib.offsetbox.AnchoredOffsetbox):
    """ size: length of bar in data units
        extent : height of bar ends in axes units """
    def __init__(self, size=1, extent = 0.03, label="", loc=2, ax=None,
                 pad=0.4, borderpad=0.5, ppad = 0, sep=2, prop=None,
                 label_color=None,
                 frameon=True, **kwargs):
        if not ax:
            ax = plt.gca()
        trans = ax.get_xaxis_transform()

        size_bar = matplotlib.offsetbox.AuxTransformBox(trans)
        line = Line2D([0,size],[0,0], **kwargs)
        vline1 = Line2D([0,0],[-extent/2.,extent/2.], **kwargs)
        vline2 = Line2D([size,size],[-extent/2.,extent/2.], **kwargs)
        size_bar.add_artist(line)
        size_bar.add_artist(vline1)
        size_bar.add_artist(vline2)
        txt = matplotlib.offsetbox.TextArea(label, minimumdescent=False, textprops={
            'color': label_color,
        })
        self.vpac = matplotlib.offsetbox.VPacker(children=[size_bar,txt],
                                 align="center", pad=ppad, sep=sep)
        matplotlib.offsetbox.AnchoredOffsetbox.__init__(self, loc, pad=pad,
                 borderpad=borderpad, child=self.vpac, prop=prop, frameon=frameon)


def savefig(desired_path, dpi=400, **kwargs):
    full_path = path_for_plot(desired_path)
    plt.savefig(full_path, dpi=dpi, **kwargs)


def path_for_plot(desired_path):
    workspace = CONFIG['WORKSPACE']
    assert(workspace is not None)

    if isinstance(workspace, dict):
        workspace = workspace['name']

    filename = os.path.join(FIGURE_PATH, workspace,
                            datetime.date.today().isoformat(), desired_path)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    return filename


def path_for_holoviews(desired_path):
    skip_paths = ['.svg', '.png', '.jpeg', '.jpg', '.gif']

    prefix, ext = os.path.splitext(desired_path)

    if ext in skip_paths:
        return prefix

    return prefix + ext


def name_for_dim(dim_name, escaped=True):
    name = {
        'polar': r'$\theta$',
        'phi': r'$\varphi$',
        'eV': r'$\textnormal{E}$',
        'kx': r'$\textnormal{k}_\textnormal{x}$',
        'ky': r'$\textnormal{k}_\textnormal{y}$',
        'kz': r'$\textnormal{k}_\textnormal{z}$',
        'kp': r'$\textnormal{k}_\textnormal{\parallel}$',
        'hv': r'$h\nu$'
    }.get(dim_name)

    if not escaped:
        name = name.replace('$', '')

    return name

def unit_for_dim(dim_name, escaped=True):
    unit = {
        'polar': r'rad',
        'phi': r'rad',
        'eV': r'eV',
        'kx': r'$\AA^{-1}$',
        'ky': r'$\AA^{-1}$',
        'kz': r'$\AA^{-1}$',
        'kp': r'$\AA^{-1}$',
        'hv': r'eV'
    }.get(dim_name)

    if not escaped:
        unit = unit.replace('$', '')

    return unit

def label_for_colorbar(data):
    if not data.S.is_differentiated:
        return r'Spectrum Intensity (arb).'

    # determine which axis was differentiated
    hist = data.S.history
    records = [h['record'] for h in hist if isinstance(h, dict)]
    if 'curvature' in [r['by'] for r in records]:
        curvature_record = [r for r in records if r['by'] == 'curvature'][0]
        directions = curvature_record['directions']
        return r'Curvature along {} and {}'.format(
            name_for_dim(directions[0]),
            name_for_dim(directions[1])
        )

    derivative_records = [r for r in records if r['by'] == 'dn_along_axis']
    c = Counter(itertools.chain(*[[d['axis']] * d['order'] for d in derivative_records]))

    partial_frag = r''
    if sum(c.values()) > 1:
        partial_frag = r'^' + str(sum(c.values()))

    return r'$\frac{\partial' + partial_frag + r' \textnormal{Int.}}{' + \
           r''.join([r'\partial {}^{}'.format(name_for_dim(item, escaped=False), n)
                     for item, n in c.items()])+ '}$ (arb.)'


def label_for_dim(data, dim_name, escaped=True):
    raw_dim_names = {
        'polar': r'$\theta$',
        'phi': r'$\varphi$',
        'eV': r'\textbf{eV}',
        'angle': r'Interp. \textbf{Angle}'
    }

    if data.S.spectrometer.get('type') == 'hemisphere':
        raw_dim_names['phi'] = r'$\varphi$ (Hemisphere Acceptance)'

    if dim_name in raw_dim_names:
        return raw_dim_names.get(dim_name)

    # Next we will look at the listed symmetry_points to try to infer the appropriate way to display the axis
    return r'$\boldsymbol{\Gamma}\rightarrow \textbf{X}$'


def label_for_symmetry_point(point_name):
    proper_names = {
        'G': r'$\Gamma$',
        'X': r'X',
        'Y': r'Y',
    }
    return proper_names.get(point_name, point_name)


class CoincidentLinesPlot():
    """
    Helper to allow drawing lines at the same location. Will draw n lines offset so that their
    center appears at the data center, and the lines will end up nonoverlapping.

    Only works for straight lines

    Technique from https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit.
    """

    linewidth=3

    def __init__(self, **kwargs):
        self.ax = kwargs.pop('ax', plt.gca())
        self.fig = kwargs.pop('fig', plt.gcf())
        self.extra_kwargs = kwargs
        self.ppd = 72. / self.fig.dpi
        self.has_drawn = False

        self.events = {
            'resize_event': self.ax.figure.canvas.mpl_connect('resize_event', self._resize),
            'motion_notify_event': self.ax.figure.canvas.mpl_connect('motion_notify_event', self._resize),
            'button_release_event': self.ax.figure.canvas.mpl_connect('button_release_event', self._resize),
        }
        self.handles = []
        self.lines = [] # saved args and kwargs for plotting, does not verify coincidence

    def add_line(self, *args, **kwargs):
        assert(not self.has_drawn)
        self.lines.append((args, kwargs,))

    def draw(self):
        self.has_drawn = True

        offset_in_data_units = self.data_units_per_pixel * self.linewidth
        self.offsets = [offset_in_data_units * (o - (len(self.lines) - 1) / 2) for o in range(len(self.lines))]

        for offset, (line_args, line_kwargs) in zip(self.offsets, self.lines):
            line_args = self.normalize_line_args(line_args)
            line_args[1] = np.array(line_args[1]) + offset
            handle = self.ax.plot(*line_args, **line_kwargs)
            self.handles.append(handle)

    @property
    def data_units_per_pixel(self):
        trans = self.ax.transData.transform
        inverse = ((trans((1, 1)) - trans((0, 0))) * self.ppd)
        return (1/inverse[0], 1/inverse[1])

    def normalize_line_args(self, args):
        def is_data_type(value):
            return isinstance(value, (
                np.array, np.ndarray, list, tuple
            ))

        assert(is_data_type(args[0]))

        if len(args) > 1 and is_data_type(args[1]) and len(args[0]) == len(args[1]):
            # looks like we have x and y data
            return args

        # otherwise we should pad the args with the x data
        return [range(len(args[0]))] + args


    def _resize(self, event=None):
        # Keep the trace in here until we can test appropriately.
        import pdb
        pdb.set_trace()
        """
        self.line.set_linewidth(lw)
        self.ax.figure.canvas.draw_idle()
        self.lw = lw
        """
