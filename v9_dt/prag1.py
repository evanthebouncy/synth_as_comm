from decisiontree import *
import tqdm
import pickle
import numpy as np

ALL_SHAPE_REPRS, L0VS = pickle.load(open("L0VS.p" ,"rb"))

# the literal listener upon hearing utterances
def L0(us):
    ret = set.intersection(*[L0VS[u] for u in us])
    pr = np.ones(len(ret))
    return ret, pr / np.sum(pr) 

# the literal speaker that utters all it can sans whats already being said
def S0(shape_repr_id, us=[]):
    shapes = ALL_SHAPE_REPRS[shape_repr_id]
    utters = []
    for i in range(L):
        for j in range(L):
            to_append = (i, j, shapes[i][j])
            if to_append not in us:
                utters.append(to_append)
    return utters

# get 1step S1 probability, PS1_1(u | w us)
# return a list of further uttrances and PS1_1(u | w us) normalised
def PS1_1(shape_repr_id, us):
    u_news = S0(shape_repr_id, us)
    vs_us = L0(us)[0] if len(us) > 0 else set()

    u_weights = []
    for u_new in u_news:
        vs_us_new = set.intersection(vs_us, L0([u_new])[0]) if len(vs_us) > 0 else L0([u_new])[0]
        u_weights.append(1 / len(vs_us_new))
    u_weights = np.array(u_weights)
    return u_news, u_weights / np.sum(u_weights)

# get a logPS1 score for a particular us upon shape_repr_id
def logPS1(shape_repr_id, us):
    logpr = 0.0
    for i in range(len(us)):
        to_utter = us[i]
        utters, utter_prob = PS1_1(shape_repr_id, us[:i]) 
        prob_idx = utters.index(to_utter)
        logpr += np.log(utter_prob[prob_idx])
    return logpr

# get the top1 utterance by S1
def get_top1_S1(shape_repr_id, n_utter):
    utters = []
    for i in range(n_utter):
        best_nxt = None
        best_score = -99999
        for nxt_utter in S0(shape_repr_id, utters):
            full_utter = utters + [nxt_utter]
            score = logPS1(shape_repr_id, full_utter)
            if score > best_score:
                best_score = score
                best_nxt = nxt_utter
        utters = utters + [best_nxt]
    return utters

# get PL1 from utterances us
def PL1(us, limit=500):
    shape_repr_ids = list(L0(us)[0])[:limit]
    shape_repr_id_weights = []
    for i, p in tqdm.tqdm(enumerate(shape_repr_ids)):
        shape_repr_id_weights.append(logPS1(p, us))
    return shape_repr_ids, shape_repr_id_weights

def interactive(listener, goal_shape_id):
    goal_shape = ALL_SHAPE_REPRS[goal_shape_id]
    #best_utter = get_top1_S1(goal_shape_id, 5)
    #print (best_utter)
    draw(goal_shape, 'target')

    us = []
    while True:
        raw = input("i[0-7] j[0-7] 1 or 0 \n>>>").split(' ')
        # UNDO UNDO LMAO
        if raw[0] == 'UNDO':
            us = us[:-1]
            if len(us) == 0:
                continue
        else:
            coords = int(raw[0]), int(raw[1])
            shape = int(raw[2])
            us.append(coords+(shape,))

        shape_repr_ids, idd_weights = listener(us)
        print (f"{len(shape_repr_ids)} candidates remain")
        shape_reprs = list(shape_repr_ids)
        idx_weights = list(reversed(sorted(list(zip(idd_weights, range(len(idd_weights)))))))
        print (f"top3 {idx_weights[:3]}")
        top3 = [x[1] for x in idx_weights[:3]]
        for j, i in enumerate(top3):
            draw(ALL_SHAPE_REPRS[shape_reprs[i]], f"candidate_{j}")


if __name__ == '__main__':
    #_, shapes = gen_legal_prog_shape()
    #print (shapes)
    rand_id = random.choice([_ for _ in range(len(ALL_SHAPE_REPRS))])
    interactive(PL1, rand_id)
    # interactive(L0, shaperepr)
    
