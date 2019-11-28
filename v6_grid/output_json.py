import json
import pickle
from functools import singledispatch

@singledispatch
def keys_to_strings(ob):
    return ob

@keys_to_strings.register(dict)
def _handle_dict(ob):
    return {str(k): keys_to_strings(v) for k, v in ob.items()}

@keys_to_strings.register(list)
def _handle_list(ob):
    return [keys_to_strings(v) for v in ob]

@keys_to_strings.register(set)
def _handle_set(ob):
    return [keys_to_strings(v) for v in ob]


ALL_SHAPE_REPRS, L0VS = pickle.load(open("L0VS.p" ,"rb"))

to_dump = keys_to_strings(L0VS)
jstr = json.dumps(to_dump)
jstr = 'var l0vs = ' + jstr

to_dump_allrepr = ALL_SHAPE_REPRS
reprjstr = json.dumps(to_dump_allrepr)
reprjstr = 'var all_shapes = ' + reprjstr

print (jstr[:40])
print (reprjstr[:40])

with open("l0vs.js", "w") as fp:
    fp.write(jstr)
with open("all_shapes.js", "w") as fp:
    fp.write(reprjstr)



