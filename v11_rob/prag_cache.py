import random
from fake_fill import P, sample_P_params, sample_input
import pickle

# we want to identify functions up-to I-O equivalence
def make_func_io_hash(func, all_inps):
    io_list = []
    for inp in all_inps:
        io_list.append((inp, func(inp)))
    return hash(str(io_list))

def make_vs_cache():

    # step 1 : generate all the different inputs !
    input_seen = set()
    # stop genreating the inputs
    input_stops = []
    for i in range(10000000):
        inp = sample_input()
        input_seen.add(inp)
        
        if i % 10000 == 0:
            input_stops.append(len(input_seen))
            print ("input generated ", len(input_seen))
            if len(input_stops) > 100 and input_stops[-1] == input_stops[-100]:
                break

    # store all the inputs as an ordered list
    all_inputs = list(input_seen)

    # step 2 : generate all the different functions !
    func_seen = set()
    func_io_seen = dict()
    # stop generating functiosn
    func_stops = []
    for i in range(10000000):
        # generate a function , get its string representation
        P_params = sample_P_params()
        func = P.generate(P_params)
        func_repr = str(func)
        # if the string representation is new
        if func_repr not in func_seen:
            func_seen.add(func_repr)
            # get the io specification
            func_io_repr = make_func_io_hash(func, all_inputs)
            func_io_seen[func_io_repr] = P_params
        
        if i % 1000 == 0:
            print ("function generated ", len(func_io_seen))
            func_stops.append(len(func_io_seen))

            if len(func_stops) > 100 and func_stops[-1] == func_stops[-100]:
                break

    # to cache these crazy f00ls
    prog_params = []
    vs = dict()

    # for the crazy cross product, cache in the results O_O
    for func_i, func_io_repr in enumerate(func_io_seen):
        P_params = func_io_seen[func_io_repr]
        prog_params.append(P_params)
        func = P.generate(P_params)
        for inp in input_seen:
            out = func(inp)
            if (inp,out) not in vs:
                vs[(inp,out)] = set()
            vs[(inp,out)].add(len(prog_params)-1)

        if func_i % 1000 == 0:
            print (f"handling program number {func_i} {len(func_io_seen)}")
            print ("vs size ", sum([len(v) for v in vs.values()]))
            pickle.dump((prog_params, vs), open("L0VS.p", "wb"))
            print ("dumpked pickle")

    pickle.dump((prog_params, all_inputs, vs), open("L0VS.p", "wb"))
    print ("dumpked pickle")

if __name__ == '__main__':
    make_vs_cache()
