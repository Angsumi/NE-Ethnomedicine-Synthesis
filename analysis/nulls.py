"""Shared randomisation helpers for the revision (margin-preserving nulls).

curveball_chain: Strona et al. (2014) curveball algorithm on a binary matrix stored as a list of row sets.
Each swap picks two rows and re-deals the items that only one of them holds. Row totals and column totals
are both preserved exactly, so a survey keeps its plants, each plant keeps its number of conditions, and each
condition keeps its number of plants.
"""
import numpy as np


def curveball_step(rows, rng, n_swaps):
    n = len(rows)
    if n < 2:
        return
    for _ in range(n_swaps):
        i, j = rng.choice(n, 2, replace=False)
        a, b = rows[i], rows[j]
        a_only, b_only = a - b, b - a
        if not a_only or not b_only:
            continue
        pool = list(a_only | b_only)
        rng.shuffle(pool)
        k = len(a_only)
        shared = a & b
        rows[i] = shared | set(pool[:k]); rows[j] = shared | set(pool[k:])


class BlockCurveball:
    """Independent curveball chains for many blocks (e.g. one per survey report).

    blocks: dict block_id -> dict row_id -> set(items). Rows are plants, items are conditions.
    sample(): advance every chain by `thin` sweeps and return a flat list of (block, row, item) triples.
    """

    def __init__(self, blocks, rng, burn=50, thin=5):
        self.keys = list(blocks)
        self.rows = {k: [set(s) for s in blocks[k].values()] for k in self.keys}
        self.ids = {k: list(blocks[k].keys()) for k in self.keys}
        self.rng, self.thin = rng, thin
        for k in self.keys:
            curveball_step(self.rows[k], rng, burn * max(len(self.rows[k]), 1))

    def sample(self):
        out = []
        for k in self.keys:
            curveball_step(self.rows[k], self.rng, self.thin * max(len(self.rows[k]), 1))
            for rid, s in zip(self.ids[k], self.rows[k]):
                out.extend((k, rid, c) for c in s)
        return out


def perm_p(null, obs):
    null = np.asarray(null)
    return float((np.sum(null >= obs) + 1) / (len(null) + 1))
