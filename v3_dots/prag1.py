from dots import *
import pickle
import random

def eval_prog(x):
    if type(x) == type(''):
        return eval(x)
    else:
        return x

def eval_spec(x):
    if type(x[0][0]) == type(''):
        return (eval(x[0][0]), eval(x[0][1])), (eval(x[1][0]), eval(x[1][1]))
    else:
        return x

def load_S0_L0_from_cache():
    stuff = pickle.load(open('cache.p', 'rb'))
    loc_to_prog, prog_to_loc, rel_to_prog, prog_to_rel = stuff
    
    def cross(stuffs):
        if stuffs == []:
            return [[]]
        else:
            ret = []
            rest = cross(stuffs[1:])
            for f in stuffs[0]:
                for r in rest:
                    ret.append([f] + r)
            return ret

    def cross(a,b,c,d):
        ret = []
        for i, aa in enumerate(a):
            for j, bb in enumerate(b):
                for k, cc in enumerate(c):
                    for l, dd in enumerate(d):
                        if i <= j and k <= l:
                            ret.append((aa,bb,cc,dd))
        return ret

    # give the set of all consistent utterances from prog
    def PS0(prog, sample_limit=3600, force_add=None):
        prog = repr(prog)
        pred_loc = prog_to_loc[prog]
        pred_rel = prog_to_rel[prog]

        everything = []
        # create everything if suficiently small
        if len(pred_loc)**2 * len(pred_rel)**2 < sample_limit:
            everything = cross(pred_loc, pred_loc, pred_rel, pred_rel)
        # otherwise we sample
        else:
            for _ in range(sample_limit):
                pred_loc = list(pred_loc)
                pred_rel = list(pred_rel)
                a0 = random.choice(pred_loc)
                a1 = random.choice(pred_loc)
                a0,a1 = list(sorted([a0,a1]))
                a2 = random.choice(pred_rel)
                a3 = random.choice(pred_rel)
                a2,a3 = list(sorted([a2,a3]))
                everything.append([a0, a1, a2, a3])

        ret = [((a[0],a[1]) , (a[2],a[3])) for a in everything]

        if force_add is not None and force_add not in ret:
            ret.append(force_add)
        return ret


    def PL0(spec):
        loc_specs, rel_specs = spec
        loc_sats = [loc_to_prog[repr(loc)] for loc in loc_specs]
        rel_sats = [rel_to_prog[repr(rel)] for rel in rel_specs]
        all_sats = loc_sats + rel_sats
        everything = all_sats[0].intersection(all_sats[1]).intersection(all_sats[2]).intersection(all_sats[3])
        return [e for e in everything]

    return PS0, PL0

def get_cache():
    loc_to_prog = dict()
    prog_to_loc = dict()
    rel_to_prog = dict()
    prog_to_rel = dict()

    stuff = pickle.load(open('cache.p', 'rb'))
    loc_to_prog, prog_to_loc, rel_to_prog, prog_to_rel = stuff

    for i in range(10000000000):
        prog = gen_prog()
        prog_repr = repr(prog)
        
        # add in location description and program mapping
        loc_desc = repr(gen_description_loc(prog))
        if loc_desc not in loc_to_prog:
            loc_to_prog[loc_desc] = set()
        loc_to_prog[loc_desc].add(prog_repr)

        if prog_repr not in prog_to_loc:
            prog_to_loc[prog_repr] = set()
        prog_to_loc[prog_repr].add(loc_desc)

        # add in relational description and program mapping
        rel_desc = repr(gen_description_rel(prog))
        if rel_desc not in rel_to_prog:
            rel_to_prog[rel_desc] = set()
        rel_to_prog[rel_desc].add(prog_repr)

        if prog_repr not in prog_to_rel:
            prog_to_rel[prog_repr] = set()
        prog_to_rel[prog_repr].add(rel_desc)

        if i % 100000 == 0:
            def sizee(dd):
                return sum([len(x) for x in dd.values()])
            print (sizee(loc_to_prog), sizee(prog_to_loc), sizee(rel_to_prog), sizee(prog_to_rel))
            pickle.dump((loc_to_prog, prog_to_loc, rel_to_prog, prog_to_rel), 
                        open('cache.p','wb'))
            print ("finished dumping")

# build PS1 from PS0 and PL0
def PS1(prog, PS0, PL0, force_add = None, sample_limit=3600):
    legal_specs = [eval_spec(x) for x in PS0(prog, sample_limit, force_add = force_add)]
    weights = []
    
    for spec in legal_specs:
        weights.append(1/len(PL0(spec)))
        #print (len(weights)/len(legal_specs),len(legal_specs))

    weights = np.array(weights)
    weights = weights / np.sum(weights)
    return legal_specs, weights

def PL1(spec, PS0, PL0):
    legal_progs = [eval_prog(x) for x in PL0(spec)]
    print ("legal programs ",len(legal_progs))
    weights = []

    for jj, prog in enumerate(legal_progs):
        render_dots(prog, f"l1_{jj}")

        s1_u, s1_w = PS1(prog, PS0, PL0, force_add = spec)
        if spec not in s1_u:
            weights.append(0)
        else:
            spec_weight = s1_w[s1_u.index(spec)]
            weights.append(spec_weight)
        print (len(weights))
        print (weights)
        print (len(legal_progs))

    weights = np.array(weights)
    weights = weights / np.sum(weights)
    return legal_progs, weights

if __name__ == '__main__':
    # get_cache()

    PS0, PL0 = load_S0_L0_from_cache()
    prog = gen_prog()

    # prog = [('B', (0, 1)), ('B', (2, 0)), ('R', (3, 3))]

    render_dots(prog, "orig_prog")

    rand_spec = eval_spec(random.choice(PS0(prog)))
    print ("random spec ", rand_spec)
    s0l0_prog = eval_prog(random.choice(PL0(rand_spec)))
    render_dots(s0l0_prog, "S0L0_prog")

    specs, weights = PS1(prog, PS0, PL0)
    best_spec = eval_spec(specs[np.argmax(weights)])
    print ("best PS1 spec ", best_spec)

    recovered_progs, prog_weights = PL1(best_spec, PS0, PL0)
    best_prog = eval_prog(recovered_progs[np.argmax(prog_weights)])
    print (best_prog)

    render_dots(best_prog, "S1L1_prog")

    from matplotlib import pyplot as plt
    plt.plot(prog_weights)
    plt.savefig('drawings/prog_weights.png')
