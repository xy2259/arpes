import json
import os.path
import xarray as xr
from arpes.config import DATASET_CACHE_PATH, DATASET_CACHE_RECORD


def _filename_for(data):
    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
        data = data.attrs['id']

    return os.path.join(DATASET_CACHE_PATH, data + '.nc')


_wrappable = {'note', 'data_preparation', 'provenance'}
_ignore_keys = {'Number of slices', 'Time', 'Detector last x-channel', 'Detector first x-channel',
                'Detector first y-channel', 'Detector last y-channel', 'User', 'Step Time', 'ENDSTATION',
                'userPhiOffset', 'MCP', 'provenance', 'Date', 'Version', 'Beam Current', 'userPolarOffset',
                'userNormalIncidenceOffset', 'Energy Step', 'Center Energy'}
_whitelist_keys = {'Region Name', 'Sample', 'id'}


def wrap_attrs(arr: xr.DataArray):
    for key in _wrappable:
        if key not in arr.attrs:
            continue

        arr.attrs[key] = json.dumps(arr.attrs[key])


def unwrap_attrs(arr: xr.DataArray):
    for key in _wrappable:
        if key not in arr.attrs:
            continue

        try:
            arr.attrs[key] = json.loads(arr.attrs[key])
        except Exception as e:
            pass


def save_dataset(arr: xr.DataArray):
    # TODO human readable caching in addition to FS caching
    with open(DATASET_CACHE_RECORD, 'r') as cache_record:
        records = json.load(cache_record)

    if arr.attrs['id'] in records:
        return

    wrap_attrs(arr)
    filename = _filename_for(arr)
    print(filename)
    arr.to_netcdf(filename, engine='netcdf4')

    records[arr.attrs['id']] = {
        'file': filename,
        **{k: v for k, v in arr.attrs.items() if k in _whitelist_keys}
    }

    with open(DATASET_CACHE_RECORD, 'w') as cache_record:
        json.dump(records, cache_record, sort_keys=True, indent=2)

    unwrap_attrs(arr)


def load_dataset(dataset_uuid):
    filename = _filename_for(dataset_uuid)
    if not os.path.exists(filename):
        raise ValueError('%s is not cached on the FS')

    arr = xr.open_dataarray(filename)
    unwrap_attrs(arr)


def available_datasets(**filters):
    with open(DATASET_CACHE_RECORD, 'r') as cache_record:
        records = json.load(cache_record)

    for filt, value in filters.items():
        records = {k: v for k, v in records.items() if filt in v and v[filt] == value}

    return records