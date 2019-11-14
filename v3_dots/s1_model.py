import pickle
import torch
import numpy as np
import random

from gen_s1_data import prog_spec_to_np, np_to_description_loc, np_to_description_rel
from utilities import Module

import torch.nn as nn
import torch.nn.functional as F

DUMMY_SPEC = ((('2', 'B', 'Edge', 'any', 'Right'), ('all', 'B', 'Edge', 'any', 'Right')), (('Far', ('some', 'B'), ('1', 'B')), ('Far', ('some', 'B'), ('1', 'B'))))

# sample prog batch : (10, 2, 4, 4) 
# sample spec batch : (10, 4, 5, 6)
class NNS1(Module):

    def __init__(self):
        super(NNS1, self).__init__()
        print ("I am live")
        hidden_size = 128
        self.enc = nn.Sequential(
            nn.Linear(32, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU())

        self.fc_mu = nn.Linear(hidden_size, hidden_size)
        self.fc_logvar = nn.Linear(hidden_size, hidden_size)

        self.dec = nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 4*5*6),
            )

        self.finalize()
        self.opt = torch.optim.Adam(self.parameters(), lr=0.001)


    def prog_specs_to_tensor(self, prog_specs):
        ww, uu = [], []
        for prog_spec in prog_specs:
            w, u = prog_spec_to_np(*prog_spec)
            ww.append(w)
            uu.append(u)
        ww, uu = np.array(ww), np.array(uu)
        return self.tensor(ww), self.tensor(uu)

    def vae(self, w_enc):
        return self.fc_mu(w_enc), self.fc_logvar(w_enc)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return eps.mul(std).add_(mu)


    def forward(self, prog_specs):
        ww, uu = self.prog_specs_to_tensor(prog_specs)
        w_enc = self.enc(ww.view(-1, 2*4*4))
        mu, logvar = self.vae(w_enc)
        z = self.reparameterize(mu, logvar)

        #return self.dec(z), mu, logvar
        logit_specs = self.dec(z).view(-1, 4*5, 6)
        logprob_specs = F.log_softmax(logit_specs, dim=-1)

        return logprob_specs, mu, logvar

    def loss(self, prog_specs):
        _, spec_target = self.prog_specs_to_tensor(prog_specs)
        spec_target = spec_target.view(-1, 4*5, 6)

        logprob_specs, mu, logvar = self(prog_specs)
        # TODO : mess with this ! 
        KLD = -0.01 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        XEN = - torch.sum(logprob_specs * spec_target)
        return KLD + XEN

    def get_prog_spec_logpr(self, prog_specs):
        _, spec_target = self.prog_specs_to_tensor(prog_specs)
        spec_target = spec_target.view(-1, 4*5, 6)

        logprob_specs, mu, logvar = self(prog_specs)
        return torch.sum(logprob_specs * spec_target)

    def get_samples(self, prog, n_sample):
        prog_specs = [(prog, DUMMY_SPEC) for _ in range(n_sample)]
        logprob_specs, _, _ = self(prog_specs)
        specc = self.to_numpy(torch.argmax(logprob_specs,-1))
        ret = []
        for spec in specc:
            loc1, loc2 = spec[:5], spec[5:10]
            rel1, rel2 = spec[10:15], spec[15:20]
            try:
                to_add = ((np_to_description_loc(loc1),
                  np_to_description_loc(loc2)),
                 (np_to_description_rel(rel1),
                    np_to_description_rel(rel2)))
                ret.append(to_add)
            except:
                pass
        return ret

    def save(self, loc):
        torch.save(self.state_dict(), loc)

    def load(self, loc):
        self.load_state_dict(torch.load(loc))


def train(train_path):
    training_data = pickle.load(open(train_path, "rb"))
    batch_size = 10
    data_len = len(training_data) - batch_size - 2
    nns1 = NNS1()

    for i in range(100000000):
        random_idx = random.randint(0, data_len)
        train_batch = training_data[random_idx:random_idx + batch_size]

        # print (nns1.get_prog_spec_logpr([training_data[0] for _ in range(100)]) / 100 / 20)

        nns1.opt.zero_grad()
        loss = nns1.loss(train_batch)
        loss.backward()
        nns1.opt.step()

        if i % 1000 == 0:
            print (i)
            print (loss)
            print ('program ', train_batch[0][0])
            sample = nns1.get_samples(train_batch[0][0], 20)
            sample = list(set(sample))
            for s in sample:
                print (s)
            nns1.save('saved_models/s1.mdl')
            print ("model saved")

if __name__ == '__main__':
    train("s1_training.p")


