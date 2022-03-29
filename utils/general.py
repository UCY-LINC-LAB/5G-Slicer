import json


def to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)


class CurrentEncoder(json.JSONEncoder):
    def default(self, o):
        from networks.QoS import QoS
        from utils.location import Location
        if isinstance(o, QoS):
            return o.get_formated_qos()
        if isinstance(o, Location):
            return o.to_dict()
        if isinstance(o, Bins):
            return o.__dict__
        return super(CurrentEncoder, self).default(o)


from collections.abc import MutableMapping
from bisect import bisect_left


class Bins(MutableMapping):
    def __init__(self, intervals, init_value=None):
        empty_bins = {interval: init_value for interval in intervals}
        self._dict = empty_bins

    def __getitem__(self, key):
        interval = self._roundkey(key)
        return self._dict[interval]

    def __setitem__(self, key, value):
        interval = self._roundkey(key)
        self._dict[interval] = value

    def _roundkey(self, key):
        intervals = list(self._dict.keys())
        minkey = intervals[0]
        midkeys = intervals[1:-1]
        maxkey = intervals[-1]

        if key <= minkey:
            return minkey
        elif key >= maxkey:
            return maxkey
        elif key in midkeys:
            return key
        else:
            i = bisect_left(intervals, key)
            leftkey = intervals[i - 1]
            rightkey = intervals[i]

            if abs(leftkey - key) < abs(rightkey - key):
                return leftkey
            else:
                return rightkey

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return repr(self._dict)

    def __str__(self):
        return f"Bins({repr(self)})"
