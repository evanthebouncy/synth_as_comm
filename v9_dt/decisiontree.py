import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree
import pickle
import random

L = 10

def visualise_surface(clf):
    xx = np.linspace(0, 1, L)
    yy = np.linspace(0, 1, L)
    mat = tuple(tuple(int(clf.predict([[x,y]])[0]) for x in xx) for y in yy)
    return mat

def gen_legal_shape():
    n_pts = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
    X = np.random.random(size=(n_pts,2))
    Y = np.random.randint(0,2,n_pts)
    max_depth = random.choice([1,2])
    clf = tree.DecisionTreeClassifier(splitter='random', max_depth=max_depth)
    clf.fit(X,Y)
    return visualise_surface(clf)

def sample_legal_shape(us):
    X = [(u[1]/L,u[0]/L) for u in us]
    Y = [u[2] for u in us]
    clf = tree.DecisionTreeClassifier(splitter='random')
    clf.fit(X,Y)
    return visualise_surface(clf)

def draw(mat, name):
    plt.imshow(mat)
    plt.savefig(f"drawings/{name}.png")
    plt.close()

def test():
    for i in range(10):
        mat = gen_legal_shape()
        plt.imshow(mat)
        plt.savefig(f"drawings/dt{i}.png")
        plt.close()

def get_version_space():
    # version space
    vs = dict()
    seen_shapes = set()
    cached_shapes = []
    len_shapes = []
    for i in range(100000000):
        shapes = gen_legal_shape()
        if shapes not in seen_shapes:
            seen_shapes.add(shapes)
            cached_shapes.append(shapes)
            for i in range(L):
                for j in range(L):
                    key = (i, j, shapes[i][j])
                    if key not in vs:
                        vs[key] = set()
                    vs[key].add(len(cached_shapes)-1)
        if i % 1000 == 0:
            print (len(cached_shapes), sum([len(v) for v in vs.values()]))
            pickle.dump((cached_shapes, vs), open('L0VS.p', 'wb'))
            print ('dumped pickle')
            len_shapes.append(len(seen_shapes))

            if len(len_shapes) > 200 and len_shapes[-1] == len_shapes[-100]:
                print ('were done here')
                return

if __name__ == '__main__':
    test()
    get_version_space()
