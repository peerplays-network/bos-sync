def dList2Dict(l):
    return {v[0]: v[1] for v in l}


def dict2dList(l):
    return [[k, v] for k, v in l.items()]
