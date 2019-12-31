import random
from fake_fill import P, sample_E_params, sample_input
import pickle

def make_vs_cache():
    func_seen = dict()
    input_seen = set()
    # stop genreating the func and inputs
    stops = []

    # go ahead and genrate all the funcions and inputs there is
    for i in range(10000000):
        # generate a function with 2 Es (this way all program length same)
        E_params = [sample_E_params() for _ in range(2)]
        func = P.generate(E_params)

        func_repr = str(func)
        func_seen[func_repr] = E_params

        inp = sample_input()
        input_seen.add(inp)
        
        if i % 1000 == 0:
            print (f"func size {len(func_seen)}, input size {len(input_seen)}")
            stops.append((len(input_seen), len(func_seen)))

            if len(stops) > 100 and stops[-1] == stops[-100]:
                break

    # to cache these crazy f00ls
    prog_params = []
    all_inputs = list(input_seen)
    vs = dict()

    # for the crazy cross product, cache in the results O_O
    for func_i, func_repr in enumerate(func_seen):
        E_params = func_seen[func_repr]
        prog_params.append(E_params)
        func = P.generate(E_params)
        for inp in input_seen:
            out = func(inp)
            if (inp,out) not in vs:
                vs[(inp,out)] = set()
            vs[(inp,out)].add(len(prog_params)-1)

        if func_i % 1000 == 0:
            print (f"handling program number {func_i} {len(func_seen)}")
            print ("vs size ", sum([len(v) for v in vs.values()]))
            pickle.dump((prog_params, vs), open("L0VS.p", "wb"))
            print ("dumpked pickle")

    pickle.dump((prog_params, all_inputs, vs), open("L0VS.p", "wb"))
    print ("dumpked pickle")

if __name__ == '__main__':
    make_vs_cache()
