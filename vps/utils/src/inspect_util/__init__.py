import inspect


def is_class_instance(o):
    # print('%s: class instance: %s' % (inspect.isclass(o), o))
    if o is None:
        return False
    try:
        # to detect:
        # old-style class & new-style class
        # instance of old-style class and of new-style class
        # method of instance of both class
        # function

        # o.__module__ in python 3.5 some instance has no this attribute

        if (inspect.isclass(o)
            or inspect.isfunction(o)
            or inspect.ismethod(o)):
            return False
        if isinstance(o, (int, float, list, tuple, dict, str, _unicode)):
            return False
        return True
    except:
        pass
    return False


def is_class(o):
    # print('%s: class: %s' % (inspect.isclass(o), o))
    return inspect.isclass(o)

    if is_class_instance(o) or inspect.isfunction(o) or inspect.isbuiltin(o) or inspect.ismethod(o):
        return False

    return True
