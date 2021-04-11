PREFIX_I = 'INFO'
PREFIX_W = 'WARNING'
PREFIX_E = 'ERROR'
PREFIX_D = 'DEBUG'
PREFIXES = [PREFIX_I, PREFIX_W, PREFIX_E, PREFIX_D]


def debug_print(module, prefix, text):
    if module is not None and prefix in PREFIXES:
        print('[{}]\t***\t{}\t***\t{}'.format(module, prefix, text))
    else:
        raise TypeError("Wrong usage of debug_print")
