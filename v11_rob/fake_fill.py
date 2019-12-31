import random
import re

# ------------- the alphabet and the input string ---------------
L = 7
# SIG = 'Aa10-'
SIG = 'a0-'

# --- delimiters ---
SIG_LET = r'a'
# SIG_LET = r'A|a'
SIG_NUM = r'0'
SIG_LIM = r'-'

def sample_input():
    l = random.choice([_ for _ in range(0,L+1)])
    return ''.join([random.choice(SIG) for _ in range(l)])

# ------------- the program sampler ---------------

# generation is controlled by config_params which is a dictionary of values
# different config_params correspond to different programs by counting how many
# combination a config_params can have, we estimate the size of the space of
# programs

# the top level program is a concat of two E expressions
class P:
    @staticmethod
    def generate(E_params_list):
        return P([E.generate(E_params) for E_params in E_params_list])
    
    def __init__(self, Es):
        self.Es = Es
    
    def __call__(self, s):
        return ''.join([e(s) for e in self.Es])
    
    def __str__(self):
        return f"P({self.Es})"
    
    def __repr__(self):
        return str(self)

class E(P):
    @staticmethod
    def generate(E_params):
        # F
        if E_params['E'] == 0:
            return E(F.generate(E_params))
        # N
        if E_params['E'] == 1:
            return E(N.generate(E_params))
        # C
        if E_params['E'] == 2:
            return E(C.generate(E_params))
        # TODO : do those later . . . 
        assert 0, "we are not handling these yet!"
        # N(N)
        if E_params['E'] == 3:
            return E((N.generate(E_params), N.generate(E_params)))
        # N(F)
        if E_params['E'] == 4:
            return E((N.generate(E_params), F.generate(E_params)))

    def __init__(self, inner_func):
        self.inner_func = inner_func
    
    def __call__(self, s):
        # singular function
        if type(self.inner_func) != type(()):
            return self.inner_func(s)
        # function composition
        if len(self.inner_func) == 2:
            return self.inner_func[0](self.inner_func[1](s))
    
    def __str__(self):
        return f"E({self.inner_func})"

# substr(i,j) = return s[i:j]
#     get sub-string from position i to position j
# span(tk1,i,tk2,j) = return s[locs(tk1)[i] : locs(tk2)[j]]
#     get sub-string from ith tk1 location to jth tk2 location
#     span('-', 0, 'num', 2)('1-2-3') = '-2-3' // from 0th - to 2nd number
class F(E):
    @staticmethod
    def generate(E_params):
        # substr
        if E_params['F'] == 0:
            return F('substr', E_params['F_substr'])
        # span
        if E_params['F'] == 1:
            return F('span', E_params['F_span'])

    def __init__(self, f_type, f_params):
        assert f_type in ['substr', 'span']
        if f_type == 'substr':
            assert f_params[0] <= f_params[1]
            self.f_type, self.f_params = f_type, f_params
        if f_type == 'span':
            lim1_type, lim1_num, lim2_type, lim2_num = f_params
            lim1_type = [SIG_LET, SIG_NUM, SIG_LIM][lim1_type]
            lim2_type = [SIG_LET, SIG_NUM, SIG_LIM][lim2_type]
            self.f_type = f_type
            self.f_params = lim1_type, lim1_num, lim2_type, lim2_num

    def __call__(self, s):
        if self.f_type == 'substr':
            return s[self.f_params[0] : 1+self.f_params[1]]

        if self.f_type == 'span':
            lim1_type, lim1_num, lim2_type, lim2_num = self.f_params
            start_idxs = [mo.end() for mo in re.finditer(lim1_type, s) ]
            end_idxs = [mo.start() for mo in re.finditer(lim2_type, s) ]
            if len(start_idxs) <= lim1_num or len(end_idxs) <= lim2_num:
                return ""
            else:
                return s[start_idxs[lim1_num] : end_idxs[lim2_num]]
    
    def __str__(self):
        return f"F({self.f_type, self.f_params})"

class N(E):
    @staticmethod
    def generate(E_params):
        # getfirst
        if E_params['N'] == 0:
            return N('getfirst', E_params['N_getfirst'])
        # getall
        if E_params['N'] == 1:
            return N('getall', E_params['N_getall'])

    def __init__(self, f_type, f_params):
        assert f_type in ['getfirst', 'getall']
        if f_type == 'getfirst':
            # get the idx copy of the type group
            get_type, idx = f_params
            get_type = [SIG_LET, SIG_NUM, SIG_LIM][get_type]
            self.f_type, self.f_params = f_type, (get_type, idx)
        if f_type == 'getall':
            get_type = [SIG_LET, SIG_NUM, SIG_LIM][f_params]
            self.f_type, self.f_params = f_type, get_type

    def __call__(self, s):
        if self.f_type == 'getfirst':
            get_type, idx = self.f_params
            # use this to handle contiguous stuff
            get_type = f"[{get_type}]+"
            igotgot = [mo.group() for mo in re.finditer(get_type, s) ]
            if idx > len(igotgot) - 1:
                return ''
            else:
                return igotgot[idx]

        if self.f_type == 'getall':
            igotgot = [mo.group() for mo in re.finditer(self.f_params, s) ]
            return ''.join(igotgot)
    
    def __str__(self):
        return f"N({self.f_type, self.f_params})"

# put down a constant
class C(E):
    @staticmethod
    def generate(E_params):
        return C('const', E_params['C_const'])

    def __init__(self, f_type, f_params):
        assert f_type in ['const']
        self.f_type, self.f_params = f_type, SIG[f_params]

    def __call__(self, s):
        return self.f_params
    
    def __str__(self):
        return f"C({self.f_type, self.f_params})"

def sample_E_params():
    
    def get_random_substr():
        start = random.randint(0,L-1)
        end = random.randint(0,L-1)
        if start <= end:
            return start, end
        else:
            return get_random_substr()
    
    def get_random_span():
        lim1_type = random.randint(0,2)
        lim1_num  = random.randint(0,1)
        lim2_type = random.randint(0,2)
        lim2_num  = random.randint(0,1)
        
        # get rid of this bad program
        if lim1_type == lim2_type and lim1_num >= lim2_num:
            return get_random_span()

        return lim1_type, lim1_num, lim2_type, lim2_num

    def get_random_getfirst():
        get_type = random.randint(0,2)
        get_idx = random.randint(0,1)
        return get_type, get_idx

    E_params = {
        'E' : random.choice([0,1,2]),

        'F' : random.choice([0,1]),
        'F_substr' : get_random_substr(),
        'F_span' : get_random_span(),

        'N' : random.choice([0,1]),
        'N_getfirst' : get_random_getfirst(),
        'N_getall' : random.choice([0,1,2]),

        'C_const' : random.choice([ix for ix in range(len(SIG))]),
        }
    return E_params

def count_functions():
    func_seen = set()
    input_seen = set()
    for i in range(10000000):
        # generate a function with either 1 or 2 Es
        num_es = random.randint(1,2)
        func = P.generate([sample_E_params() for _ in range(num_es)])

        func_repr = str(func)
        func_seen.add(func_repr)

        inp = sample_input()
        input_seen.add(inp)
        
        if i % 1000 == 0:
            print (f"func size {len(func_seen)}, input size {len(input_seen)}")


if __name__ == '__main__':
    # print (repr(sample_input()))
    num_es = random.randint(1,2)
    prog = P.generate([sample_E_params() for _ in range(num_es)])
    print (prog)

    for i in range(5):
        print ("--------------------")
        x = sample_input()
        print (repr(x))
        print (repr(prog(x)))
    # import pdb; pdb.set_trace()
    # count_functions()
