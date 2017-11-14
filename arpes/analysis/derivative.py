import functools
import warnings

import numpy as np
import xarray as xr

from arpes.provenance import provenance

__all__ = ('curvature', 'dn_along_axis', 'd2_along_axis', 'd1_along_axis',)


def curvature(arr: xr.DataArray, directions=None, alpha=1, beta=None):
    """
    Defined via
        C(x,y) = ([C_0 + (df/dx)^2]d^2f/dy^2 - 2 * df/dx df/dy d^2f/dxdy + [C_0 + (df/dy)^2]d^2f/dx^2) /
                 (C_0 (df/dx)^2 + (df/dy)^2)^(3/2)

    of in the case of inequivalent dimensions x and y

        C(x,y) = ([1 + C_x(df/dx)^2]C_y * d^2f/dy^2 -
                  2 * C_x * C_y * df/dx df/dy d^2f/dxdy +
                  [1 + C_y * (df/dy)^2] * C_x * d^2f/dx^2) /
                 (1 + C_x (df/dx)^2 + C_y (df/dy)^2)^(3/2)

        where
        C_x = C_y * (xi / eta)^2
        and where (xi / eta) = dx / dy

        The value of C_y can reasonably be taken to have the value |df/dx|_max^2 + |df/dy|_max^2
        C_y = (dy / dx) * (|df/dx|_max^2 + |df/dy|_max^2) * \alpha

        for some dimensionless parameter alpha
    :param arr:
    :param alpha: regulation parameter, chosen semi-universally, but with no particular justification
    :return:
    """
    if beta is not None:
        alpha = np.power(10., beta)

    if directions is None:
        directions = arr.dims[:2]

    axis_indices = tuple(arr.dims.index(d) for d in directions)
    dx, dy = tuple(float(arr.coords[d][1] - arr.coords[d][0]) for d in directions)
    dfx, dfy = np.gradient(arr.values, dx, dy, axis=axis_indices)
    np.nan_to_num(dfx, copy=False)
    np.nan_to_num(dfy, copy=False)

    mdfdx, mdfdy = np.max(np.abs(dfx)), np.max(np.abs(dfy))

    cy = (dy / dx) * (mdfdx ** 2 + mdfdy ** 2) * alpha
    cx = (dx / dy) * (mdfdx ** 2 + mdfdy ** 2) * alpha

    dfx_2, dfy_2 = np.power(dfx, 2), np.power(dfy, 2)
    d2fy = np.gradient(dfy, dy, axis=axis_indices[1])
    d2fx = np.gradient(dfx, dx, axis=axis_indices[0])
    d2fxy = np.gradient(dfx, dy, axis=axis_indices[1])

    denom = np.power((1 + cx * dfx_2 + cy * dfy_2), 1.5)
    numerator = (1 + cx * dfx_2) * cy * d2fy - 2 * cx * cy * dfx * dfy * d2fxy + \
                (1 + cy * dfy_2) * cx * d2fx

    curv = xr.DataArray(
        numerator / denom,
        arr.coords,
        arr.dims,
        attrs=arr.attrs
    )

    if 'id' in curv.attrs:
        del curv.attrs['id']
        provenance(curv, arr, {
            'what': 'Curvature',
            'by': 'curvature',
            'directions': directions,
            'alpha': alpha,
        })
    return curv


def dn_along_axis(arr: xr.DataArray, axis=None, smooth_fn=None, order=2):
    """
    Like curvature, performs a second derivative. You can pass a function to use for smoothing through
    the parameter smooth_fn, otherwise no smoothing will be performed.

    You can specify the axis to take the derivative along with the axis param, which expects a string.
    If no axis is provided the axis will be chosen from among the available ones according to the preference
    for axes here, the first available being taken:

    ['eV', 'kp', 'kx', 'kz', 'ky', 'phi', 'polar']
    :param arr:
    :param axis:
    :param smooth_fn:
    :param order: Specifies how many derivatives to take
    :return:
    """
    axis_order = ['eV', 'kp', 'kx', 'kz', 'ky', 'phi', 'polar']
    if axis is None:
        axes = [a for a in axis_order if a in arr.dims]
        if len(axes):
            axis = axes[0]
        else:
            # have to do something
            axis = arr.dims[0]
            warnings.warn('Choosing axis: {} for the second derivative, no preferred axis found.'.format(axis))

    if smooth_fn is None:
        smooth_fn = lambda x: x

    d_axis = float(arr.coords[axis][1] - arr.coords[axis][0])
    axis_idx = arr.dims.index(axis)

    values = arr.values
    for _ in range(order):
        values = np.gradient(smooth_fn(arr.values), d_axis, axis=axis_idx)

    dn_arr = xr.DataArray(
        values,
        arr.coords,
        arr.dims,
        attrs=arr.attrs
    )

    if 'id' in dn_arr.attrs:
        del dn_arr.attrs['id']
        provenance(dn_arr, arr, {
            'what': '{}th derivative'.format(order),
            'by': 'dn_along_axis',
            'axis': axis,
            'order': order,
        })

    return dn_arr


d2_along_axis = functools.partial(dn_along_axis, order=2)
d1_along_axis = functools.partial(dn_along_axis, order=1)