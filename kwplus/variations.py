from itertools import product


class kwvariations(list):
    pass


def separate_variations(kw):
    return ({k: v for k, v in kw.items()
             if isinstance(v, kwvariations)},
            {k: v for k, v in kw.items()
             if not isinstance(v, kwvariations)})


def config_vars_to_configs(config_vars):
    if not config_vars:
        return [{}]
    config_keys, config_vals = zip(*config_vars.items())
    return [dict(zip(config_keys, vlist)) for vlist in product(*config_vals)]


def expand_variations(kwargs):
    variations, common_kwargs = separate_variations(kwargs)
    expanded = config_vars_to_configs(variations)
    kw_expanded = list()
    for kw in expanded:
        kw_expanded.append(kw.copy())
        kw_expanded[-1].update(common_kwargs)
    return kw_expanded

