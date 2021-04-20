"""
mkinit ~/code/pypogo/pypogo/utils/__init__.py --lazy -w
"""




def lazy_import(module_name, submodules, submod_attrs):
    import sys
    import importlib
    import importlib.util
    all_funcs = []
    for mod, funcs in submod_attrs.items():
        all_funcs.extend(funcs)
    name_to_submod = {
        func: mod for mod, funcs in submod_attrs.items()
        for func in funcs
    }

    def __getattr__(name):
        if name in submodules:
            attr = importlib.import_module(
                '{module_name}.{modname}'.format(
                    module_name=module_name, modname=modname)
            )
        elif name in name_to_submod:
            modname = name_to_submod[name]
            module = importlib.import_module(
                '{module_name}.{modname}'.format(
                    module_name=module_name, modname=modname)
            )
            attr = getattr(module, name)
        else:
            raise AttributeError(
                'No {module_name} attribute {name}'.format(
                    module_name=module_name, name=name))
        globals()[name] = attr
        return attr
    return __getattr__


__getattr__ = lazy_import(
    __name__,
    submodules=[
        'priority_queue',
    ],
    submod_attrs={
        'priority_queue': [
            'PriorityData',
            'PriorityQueue',
        ],
    },
)


def __dir__():
    return __all__

__all__ = ['PriorityData', 'PriorityQueue', 'priority_queue']
