import re
import matplotlib.pyplot as plt
import pandas as pd
from simhash import Simhash as Sh
import time

s = '5 All ants have amazing design features. They have two sets of jaws—the outer pair is us     ed for carrying objects and for digging, while the inner pair is used for chewing. Some ants can lift food items (be they leaves, grains or other insects     ) that are up to seven times as heavy as themselves.<br />\\n&nbsp;</div><div style=\\\"text-align:justify\\\">All ants play an important role in the eco     nomy of a fallen world. They control the population numbers of many other species. Ants can eat animals (vertebrates as well as other invertebrates like      themselves), plants, and even the seeds of many plants, as well as eating and thus recycling dead organic material. Most ant species live in soil, but so     me, like carpenter ants, live in wood (although they don\'t actually eat the timber).<br />\\n&nbsp;</div><div style=\\\"text-align:justify\\\">6 Ants ar     e proficient hunters and are relentless in their search for a nest, food, or even slaves. They are able to mount a coordinated raid on an enemy colony, a     nd are quick to defend their nests against intruders.'

s = re.sub('\s{2,}', '', s)

def get_distances(s, hm):
    h = hm(s)
    return list(map(lambda i: h.distance(hm(s[:i])), range(len(s)-3, len(s)//2,-1)))

words = (['material', 'meterial'], ('food', 'feed'), ('slaves', 'slafs'), ('species', 'spacie'), ('some', 'any'), ('like', 'look'))

def get_distances1(s, hm):
    h = hm(s)
    return list(map(lambda s_: h.distance(hm(s_)), map(lambda w: s.replace(w[0], w[1]), words)))

def get_distances2(s, hm):
    h = hm(s)
    return list(map(lambda s_: h.distance(hm(s_)), map(lambda w: s.replace(w[0][0], w[0][1]).replace(w[1][0], w[1][1]), zip(words, words[1:]))))

def get_distances3(s, hm):
    h = hm(s)
    return list(map(lambda s_: h.distance(hm(s_)), map(lambda w: s.replace(w[0][0], w[0][1]).replace(w[1][0], w[1][1]).replace(w[2][0], w[2][1]), zip(words, words[1:], words[2:]))))

def get_distances4(s, hm):
    h = hm(s)
    return list(map(lambda s_: h.distance(hm(s_)), map(lambda w: s.replace(w[0][0], w[0][1]).replace(w[1][0], w[1][1]).replace(w[2][0], w[2][1]).replace(w[3][0], w[3][1]), zip(words, words[1:], words[2:], words[3:]))))
norm = lambda diss: list(map(lambda x: sum(x)/3, zip(diss, diss[1:], diss[2:], diss[3:])))

def get_nS(gdm):
    return gdm(s, Sh)

def get_n(gdm):
    return get_nS(gdm)

def show_n(gdm):
    sh_diss1 = gdm(s, Sh)

    df = pd.DataFrame({"old": sh_diss1})
    df.plot()
    plt.show()

ss = [
    "A",
    "I love U",
    "Hahaha",
    "A Python Implementation of Simhash Algorithm",
    "This is a segment tree (interval tree) implemented in Python",
    "The advantage of this version of reduce compared to the normal ufunc.reduce is that it makes use of the Broadcasting Rules in order to avoid creating an argument array the size of the output times the number of vectors."
    "Broadcasting allows universal functions to deal in a meaningful way with inputs that do not have exactly the same shape.",
    "The first rule of broadcasting is that if all input arrays do not have the same number of dimensions, a “1” will be repeatedly prepended to the shapes of the smaller arrays until all the arrays have the same number of dimensions.",
    "The second rule of broadcasting ensures that arrays with a size of 1 along a particular dimension act as if they had the size of the array with the largest shape along that dimension. The value of the array element is assumed to be the same along that dimension for the “broadcast” array."
]
def get_norm_distances(s, hm):
    h = hm(s)
    return list(map(lambda i: h.distance(hm(ss[i])), range(len(ss))))
from functools import reduce

def timeme(func, times=10):
    begin = time.time()
    num = sum(map(lambda _: func(), range(times)))
    print((time.time() - begin) / num)

print('My:')
timeme(lambda :len(reduce(lambda a, x: a + x, [get_n(m) for m in [get_distances1, get_distances2, get_distances3, get_distances4]])))

print('Origin:')
timeme(lambda :len(reduce(lambda a, x: a + x, [get_nS(m) for m in [get_distances1, get_distances2, get_distances3, get_distances4]])))


sh_diss = reduce(lambda a, x: a + x, [get_n(m) for m in [get_distances1, get_distances2, get_distances3, get_distances4]], [])

#[show_n(m) for m in [get_distances1, get_distances2, get_distances3, get_distances4]]
# plt.savefig('old_VS_new.png')

# sh_diss += norm(get_distances(s, Sh))[:200]

sh_diss += get_distances(s, Sh)

# df = pd.DataFrame({"old": sh_diss})
# df.plot()
# plt.show()
# plt.savefig('old_VS_new.png')

# sh_diss = sh_diss[-10:]
sh_diss += get_norm_distances(s, Sh)

# df = pd.DataFrame({"old": sh_diss})
# # df.plot(kind='bar')
# df.plot()
# plt.show()
# # plt.savefig('old_VS_new2.png')
