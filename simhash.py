# Created by 1e0n in 2013
from __future__ import division, unicode_literals

import sys
import re
import hashlib
import logging
import functools
import collections

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str
    long = int
else:
    range = xrange


def _hashfunc(x):
    return int(hashlib.md5(x).hexdigest(), 16)


def gen_features(content, pattern, width):
    content = ''.join(re.findall(pattern, content.lower()))
    length = len(content)
    ns = range((length if length > width else width) + 1)
    return [content[b:e] for b, e in zip(ns, ns[width:])]


def build_value_by_features(features, fg_len, hashfunc):
    """
    `features` might be a list of unweighted tokens (a weight of 1
               will be assumed), a list of (token, weight) tuples or
               a token -> weight dict.
    """
    v = [0] * fg_len
    masks = [1 << i for i in range(fg_len)]
    for feature, weight in features.items():
        h = hashfunc(feature.encode('utf-8'))
        for i in range(fg_len):
            v[i] += weight if h & masks[i] else -weight
    ans = 0
    for i in range(fg_len):
        if v[i] >= 0:
            ans |= masks[i]
    return ans


class Simhash(object):
    def __init__(self, value, fg_len=64, reg=r'[\w\u4e00-\u9fcc]+', hashfunc=None):
        """
        `fg_len` is the dimensions of fingerprints

        `reg` is meaningful only when `value` is basestring and describes
        what is considered to be a letter inside parsed string. Regexp
        object can also be specified (some attempt to handle any letters
        is to specify reg=re.compile(r'\w', re.UNICODE))

        `hashfunc` accepts a utf-8 encoded string and returns a unsigned
        integer in at least `fg_len` bits.
        """

        self.fg_len = fg_len
        self.reg = reg
        self.value = None

        if hashfunc is None:
            self.hashfunc = _hashfunc
        else:
            self.hashfunc = hashfunc

        build_value = functools.partial(
            build_value_by_features,
            fg_len=self.fg_len,
            hashfunc=self.hashfunc,
        )

        if isinstance(value, Simhash):
            self.value = value.value
        elif isinstance(value, basestring):
            self.value = build_value(collections.Counter(gen_features(value, self.reg, 4)))
        elif isinstance(value, collections.Iterable):
            self.value = build_value(collections.Counter(value))
        elif isinstance(value, long):
            self.value = value
        else:
            raise Exception('Bad parameter with type {}'.format(type(value)))

    def build_value_by_features(self, features, fg_len, hashfunc):
        """
        `features`: a dict <token -> weight>
        """
        values = [0] * fg_len
        masks = [1 << i for i in range(fg_len)]
        for feature, weight in features.items():
            h = hashfunc(feature.encode('utf-8'))
            for i in range(fg_len):
                values[i] += weight if h & masks[i] else -weight
        ans = 0
        for i in range(fg_len):
            if values[i] >= 0:
                ans |= masks[i]
        return ans

    def distance(self, another):
        assert self.fg_len == another.fg_len
        x = (self.value ^ another.value) & ((1 << self.fg_len) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans


class SimhashIndex(object):

    def __init__(self, objs, fg_len=64, k=2):
        """
        `objs` is a list of (obj_id, simhash)
        obj_id is a string, simhash is an instance of Simhash
        `fg_len` is the same with the one for Simhash
        `k` is the tolerance
        """
        self.k = k
        self.fg_len = fg_len
        count = len(objs)
        logging.info('Initializing %s data.', count)

        self.bucket = collections.defaultdict(set)

        for i, q in enumerate(objs):
            if i % 10000 == 0 or i == count - 1:
                logging.info('%s/%s', i + 1, count)

            self.add(*q)

    def get_near_dups(self, simhash):
        """
        `simhash` is an instance of Simhash
        return a list of obj_id, which is in type of str
        """
        assert simhash.fg_len == self.fg_len

        ans = set()

        for key in self.get_keys(simhash):
            dups = self.bucket[key]
            logging.debug('key:%s', key)
            if len(dups) > 200:
                logging.warning('Big bucket found. key:%s, len:%s', key, len(dups))

            for dup in dups:
                sim2, obj_id = dup.split(',', 1)
                sim2 = Simhash(long(sim2, 16), self.fg_len)

                d = simhash.distance(sim2)
                if d <= self.k:
                    ans.add(obj_id)
        return list(ans)

    def add(self, obj_id, simhash):
        """
        `obj_id` is a string
        `simhash` is an instance of Simhash
        """
        assert simhash.fg_len == self.fg_len

        for key in self.get_keys(simhash):
            v = '%x,%s' % (simhash.value, obj_id)
            self.bucket[key].add(v)

    def delete(self, obj_id, simhash):
        """
        `obj_id` is a string
        `simhash` is an instance of Simhash
        """
        assert simhash.fg_len == self.fg_len

        for key in self.get_keys(simhash):
            v = '%x,%s' % (simhash.value, obj_id)
            if v in self.bucket[key]:
                self.bucket[key].remove(v)

    @property
    def offsets(self):
        """
        You may optimize this method according to <http://www.wwwconference.org/www2007/papers/paper215.pdf>
        """
        return [self.fg_len // (self.k + 1) * i for i in range(self.k + 1)] + [self.fg_len]

    def get_keys(self, simhash):
        offsets = self.offsets
        for i, (offset, _offset) in enumerate(zip(offsets, offsets[1:])):
            mask = 2 ** (_offset - offset) - 1
            c = simhash.value >> offset & mask
            yield '%x:%x' % (c, i)

    def bucket_size(self):
        return len(self.bucket)
