import yaml
from argparse import ArgumentParser


class Config:
    """
    General configuration class reading from a yaml formatted file
    """

    def __init__(self, cfgpath: str):
        with open(cfgpath, 'r') as cfg:
            cfg = yaml.safe_load(cfg.read())

        parser_kwargs = cfg.pop('argparse', None)
        if parser_kwargs:
            self._parser = ArgumentParser()

            for key, value in parser_kwargs.items():
                opt = key.replace('_', '-')
                self._parser.add_argument(f'--{opt}', default=value,
                                         type=type(value), help=f'Default = {value}')
            cfg.update(
                **parser_kwargs
            )

        self.__dict__.update(**cfg)
        self.cfgpath = cfgpath

    @property
    def yaml(self):
        args = { key:value for key, value in self.__dict__.items() if not key.startswith('_') }
        return yaml.dump(args)

    def parse_args(self, *args, **kwargs):
        if not hasattr(self, '_parser'):
            print(f'No arguments to parse in {self.cfgpath}')
            return self

        args = self._parser.parse_args(*args, **kwargs)
        self.__dict__.update(**vars(args))
        return self
        