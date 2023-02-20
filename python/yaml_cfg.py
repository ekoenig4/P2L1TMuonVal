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
        parser_kwargs = cfg.pop('argparse', None)
        if parser_kwargs:
            self._parser = ArgumentParser()

            for key, value in parser_kwargs.items():
                opt = key.replace('_', '-')
                value_type = type(value)
                nargs = None 

                if isinstance(value, list):
                    nargs = '+'
                    value_type = type(value[0])

                self._parser.add_argument(f'--{opt}', default=value, nargs=nargs,
                                         type=value_type, help=f'Default = {value}')
            cfg.update(
                **parser_kwargs
            )

        self.__dict__.update(**cfg)

    @property
    def namespace(self):
        return { key:value for key, value in self.__dict__.items() if not key.startswith('_') }

    @property
    def yaml(self):
        args = self.namespace
        return yaml.dump(args)

    def parse_args(self, *args, **kwargs):
        if not hasattr(self, '_parser'):
            print(f'No arguments to parse in {self.cfgpath}')
            return self

        args = self._parser.parse_args(*args, **kwargs)
        self.__dict__.update(**vars(args))
        return self

    def replace(self):
        namespace = self.namespace
        namespace = fill_replace(namespace, **namespace)

        self.__dict__.update(**namespace)
        return self
        