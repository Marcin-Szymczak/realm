_hooks = {}

def register(name, *classes):
    _hooks[name] = {
            "hooks":[],
            "arg_classes":classes,
    }

class HookException(Exception):
    pass

class HookBadArgException(Exception):
    pass

def call(name, *args, **kvargs):
    if name in _hooks:
        hook = _hooks[name]
        for i, arg in enumerate(args):
            if arg.__class__ != hook["arg_classes"][i]:
                raise HookBadArgException 
        # print(f"Calling all attached hooks of {name}")
        for hook in _hooks[name]["hooks"]:
            # print(hook["function"])
            hook["function"](*args,**kvargs)
    else:
        raise HookException

def hook(name, fun):
    hook = {
            "function":fun,
            }
    _hooks[name]["hooks"].append(hook)


