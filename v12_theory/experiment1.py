import numpy as np
import matplotlib.pyplot as plt


def normalise(mat, axis):
    if axis == 0:
        row_sums = mat.sum(axis=1)
        new_matrix = mat / row_sums[:, np.newaxis]
        return new_matrix
    if axis == 1:
        col_sums = mat.sum(axis=0)
        new_matrix = mat / col_sums[np.newaxis, :]
        return new_matrix

# permute the rows and colums of a matrix to a canonical representation cuz order dont matter
def canonicalise(xx):
    xx = ((sum(x), tuple(x)) for x in xx)
    xx = tuple(sorted(xx))

    xx = np.array([x[1] for x in xx]).T

    xx = ((sum(x), tuple(x)) for x in xx)
    xx = tuple(sorted(xx))

    xx = np.array([x[1] for x in xx]).T

    return xx

def gen_sat(m,n, check=True):
    mat = np.random.randint(0, 2, (m,n)) + 1e-3
    # row_sums = mat.sum(axis=0)
    # col_sums = mat.sum(axis=1)
    # # make sure ever utterance and every world are 'useful'
    # if check and (0 in row_sums or 0 in col_sums):
    #     return gen_sat(m,n)
    # order the row and columns to be set invariant
    return canonicalise(mat)

# compute P(w'= w) = integrate_u Pspeak(u | w) Plisten(w' | u)
def comm_acc(S,L):
    w_to_w = (S*L).sum(axis=0)
    return w_to_w.mean()

def draw(x, name):
    plt.imshow(x, cmap='gray')
    plt.savefig(f"drawings/{name}.png")
    plt.close()

def exp1():
    work, almost_work, not_work = dict(), dict(), dict()
    for i in range(1000):
        sat = gen_sat(3, 3, check=False)

        rank = np.linalg.matrix_rank(sat)

        S0 = normalise(sat, 1)
        L0 = normalise(sat, 0)
        start_acc = comm_acc(S0, L0)

        S, L = S0, L0
        for i in range(100):
            S = normalise(L, 1)
            L = normalise(S, 0)
            end_acc = comm_acc(S, L)
            assert end_acc >= start_acc, f"{i}, {end_acc} {start_acc}, {sat}, {L0}"

        if end_acc > 0.99:
            work[str(sat)] = sat
        if end_acc < 0.99 and rank == 3:
            almost_work[str(sat)] = sat

        if end_acc < 0.99:
            not_work[str(sat)] = sat

    print ("ratio ", len(work) / 1000)

    # for i, x in enumerate(work.values()):
    #     plt.imshow(x)
    #     plt.savefig(f"drawings/work_{i}.png")
    #     plt.close()

    # for i, x in enumerate(almost_work.values()):
    #     plt.imshow(x)
    #     plt.savefig(f"drawings/almost_work_{i}.png")
    #     plt.close()

if __name__ == '__main__':
    # exp1()
    L   = np.array([ [0.01,0.01,0.98],
                     [0.02,0.01,0.97],
                     [1/3 ,1/3 ,1/3 ],
                  ])
    L   = np.array([ [0.6,0.01,0.39],
                     [0.02,0.01,0.97],
                     [1/3 ,1/3 ,1/3 ],
                  ])
    L   = np.array([ [1, 1, 0],
                     [1, 0, 1],
                     [0, 1, 0],
                  ])
    print(np.linalg.eig(L))
    print ("LOOK HERE")
    # L   = np.array([ [0, 0, 1],
    #                  [0, 0, 1],
    #                  [1, 1, 1],
    #               ])

    draw(L, "fail_0")
    rank = np.linalg.matrix_rank(L)

    S = normalise(L, 1)
    draw(L, f"0_L")
    draw(S, f"0_S")
    start_acc = comm_acc(S,L)
    print (start_acc)

    for i in range(20):
        S = normalise(L, 1)
        L = normalise(S, 0)
        draw(L, f"{i+1}_L")
        draw(S, f"{i+1}_S")
        end_acc = comm_acc(S, L)
        print (end_acc)

    print (S,"\n", L)

