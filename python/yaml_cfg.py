import yaml
from argparse import ArgumentParser
from string import Formatter

class formatdict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def replace_available(string : str, **namespace):
    namespace = formatdict(**namespace)
    return Formatter().vformat(string, (), namespace)

def fill_replace(variable, **namespace):
    if isinstance(variable, str):
        variable = replace_available(variable, **namespace)

    elif isinstance(variable, dict):
        new_namespace = dict(namespace, **variable)
        variable = { key: fill_replace(value, **new_namespace) for key, value in variable.items() }

    elif isinstance(variable, list):
        variable = [ fill_replace(value, **namespace) for value in variable]
        
    return variable

class Config:
    """
    General configuration class reading from a yaml formatted file
    """

    @classmethod
    def from_str(cls, cfgstr : str):
        cfg = yaml.safe_load(cfgstr)
        return cls(**cfg)

    @classmethod
    def from_file(cls, cfgfile : str):
        with open(cfgfile, 'r') as cfg:
            cfg = yaml.safe_load(cfg.read())
        return cls(**cfg, cfgfile=cfgfile)

    def __init__(self, **cfg):
        keys = list()

        parser_kwargs = cfg.pop('argparse', None)
        keys += list(cfg.keys())

        self._parser = ArgumentParser()
        self._parser.add_argument('--yaml', action='store_true', default=False, help='Print out initialized yaml', dest='_print_yaml')
        if parser_kwargs:

            for key, value in parser_kwargs.items():
                keys.append(key)

                opt = key.replace('_', '-')

                opt_kwargs = dict(
                    default=value,
                    type=type(value),
                    help=f'Default = {value}'
                )

                if opt_kwargs['type'] is dict:
                    opt_kwargs.update(value, type=type(value['default']))

                if opt_kwargs['type'] is list:
                    opt_kwargs.update(
                        type=type(opt_kwargs['default']),
                        nargs='+'
                    )

                self._parser.add_argument(f'--{opt}', **opt_kwargs)


            cfg.update(
                **parser_kwargs
            )

        self.__dict__.update(**cfg, _keys=keys)

    @property
    def namespace(self):
        return { key:getattr(self, key) for key in self._keys }

    @property
    def yaml(self):
        args = self.namespace
        return yaml.dump(args, sort_keys=False)

    def init(self, *args, **kwargs):
        self.parse_args(*args, **kwargs)
        self.replace()

        if self._print_yaml:
            print(self.yaml)

        return self


    def parse_args(self, *args, **kwargs):
        if not hasattr(self, '_parser'):
            print(f'No arguments to parse in {self.cfgpath}')
            return self

        args, unk = self._parser.parse_known_args(*args, **kwargs)
        self.__dict__.update(**vars(args))
        return self

    def replace(self):
        namespace = self.namespace
        namespace = fill_replace(namespace, **namespace)

        self.__dict__.update(**namespace)
        return self
        