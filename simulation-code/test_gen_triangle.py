import random
import triangle_type
import time
import numpy as np
import scipy
import math
import utils
import argparse
import os
from scipy.stats import norm
import incr_entropy


def random_gen(test_gen_budget=100000, stop_at_failure=False, delay=False, max_len=10):
    if stop_at_failure:
        start = time.time()
    f = 0.0
    n = 0
    while n < test_gen_budget or stop_at_failure:
        a = random.randint(0, max_len)
        b = random.randint(0, max_len)
        c = random.randint(0, max_len)
        n += 1
        if triangle_type.triangle_type(a, b, c, delay) != triangle_type.triangle_type_mu1(a, b, c):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
    return f / test_gen_budget



def ART_dist(test_gen_budget=100, W_sample_size=10, stop_at_failure=False, delay=False, max_len=10):
    if stop_at_failure:
        start = time.time()
    Z = []
    a = random.randint(0, max_len)
    b = random.randint(0, max_len)
    c = random.randint(0, max_len)
    Z.append((a, b, c))
    n = 1
    f = 0.0
    if triangle_type.triangle_type(a, b, c, delay) != triangle_type.triangle_type_mu1(a, b, c):
        f += 1.0
        if stop_at_failure:
            return (n, time.time() - start)
    while n < test_gen_budget or stop_at_failure:
        W = []
        W_dist = []
        for i in range(W_sample_size):
            a = random.randint(0, max_len)
            b = random.randint(0, max_len)
            c = random.randint(0, max_len)
            min_dist = np.min([math.dist((a, b, c), z) for z in Z])
            W.append((a, b, c))
            W_dist.append(min_dist)
        t_exec = W[np.argmax(W_dist)]
        n += 1
        if triangle_type.triangle_type(t_exec[0], t_exec[1], t_exec[2], delay) != triangle_type.triangle_type_mu1(t_exec[0], t_exec[1], t_exec[2]):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        Z.append(t_exec)
    return f / test_gen_budget

def update_probs(probs, a, b, c, max_len=10):
    std = 2  # max_len/5
    if a in probs:
        probs[a] += norm.pdf(a, scale=std)  # 5 sigma ensure nice decay of probabilities between 0 and max_len
    else:
        probs[a] = norm.pdf(a, scale=std)
    if b in probs:
        probs[b] += norm.pdf(b, scale=std)
    else:
        probs[b] = norm.pdf(b, scale=std)
    if c in probs:
        probs[c] += norm.pdf(c, scale=std)
    else:
        probs[c] = norm.pdf(c, scale=std)

def ART_bigram(test_gen_budget=100, W_sample_size=10, stop_at_failure=False, delay=False, max_len=10):
    if stop_at_failure:
        start = time.time()
    std = 2  # max_len/5
    Z = []
    probs = {}
    ient = incr_entropy.IncrementalEntropy()
    a = random.randint(0, max_len)
    b = random.randint(0, max_len)
    c = random.randint(0, max_len)
    Z.append((a, b, c))
    # update_probs(probs, a, b, c, max_len)
    probs[a] = norm.pdf(a, scale=std)
    probs[b] = norm.pdf(b, scale=std)
    probs[c] = norm.pdf(c, scale=std)
    ient.inc_entropy(probs)
    n = 1
    f = 0.0
    if triangle_type.triangle_type(a, b, c, delay) != triangle_type.triangle_type_mu1(a, b, c):
        f += 1.0
        if stop_at_failure:
            return (n, time.time() - start)
    while n < test_gen_budget or stop_at_failure:
        W = []
        W_ent = []
        for i in range(W_sample_size):
            a = random.randint(0, max_len)
            b = random.randint(0, max_len)
            c = random.randint(0, max_len)
            local_probs = {}  # probs.copy()
            local_probs[a] = norm.pdf(a, scale=std)
            local_probs[b] = norm.pdf(b, scale=std)
            local_probs[c] = norm.pdf(c, scale=std)
            # update_probs(local_probs, a, b, c, max_len)
            # ent = scipy.stats.entropy(list(local_probs.values()), base=2)
            ent = ient.inc_entropy(local_probs)
            W.append((a, b, c))
            W_ent.append(ent)
        t_exec = W[np.argmax(W_ent)]
        # print(f'Bigrams choice: {t_exec[0]}, {t_exec[1]}, {t_exec[2]}')
        n += 1
        if triangle_type.triangle_type(t_exec[0], t_exec[1], t_exec[2], delay) != triangle_type.triangle_type_mu1(t_exec[0], t_exec[1], t_exec[2]):
            f += 1.0
            if stop_at_failure:
                return (n, time.time() - start)
        Z.append(t_exec)
        # update_probs(probs, t_exec[0], t_exec[1], t_exec[2], max_len)
        local_probs = {}
        local_probs[t_exec[0]] = norm.pdf(t_exec[0], scale=std)
        local_probs[t_exec[1]] = norm.pdf(t_exec[1], scale=std)
        local_probs[t_exec[2]] = norm.pdf(t_exec[2], scale=std)
        ient.store_changes(local_probs)
    return f / test_gen_budget



def f_t_measure(runs_rand=1000, runs_dist=10, runs_bigrams=100, delay=False, max_len=10):
    res_rand = []
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(stop_at_failure=True, delay=delay, max_len=max_len))
        print(f'{i+1}/{runs_rand}')
    # res_rand = [random_gen(stop_at_failure=True) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(stop_at_failure=True, delay=delay, max_len=max_len))
        print(f'{i+1}/{runs_dist}')
    # res_dist = [ART_dist(stop_at_failure=True) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(ART_bigram(stop_at_failure=True, delay=delay, max_len=max_len))
        print(f'{i+1}/{runs_bigrams}')
    # res_bigrams = [ART_bigram(stop_at_failure=True) for i in range(runs_bigrams)]
    f_rand = 0 if runs_rand == 0 else np.mean([n for n, t in res_rand])
    f_dist = 0 if runs_dist == 0 else np.mean([n for n, t in res_dist])
    f_bigrams = 0 if runs_bigrams == 0 else np.mean([n for n, t in res_bigrams])
    t_rand = 0 if runs_rand == 0 else np.mean([t for n, t in res_rand])
    t_dist = 0 if runs_dist == 0 else np.mean([t for n, t in res_dist])
    t_bigrams = 0 if runs_bigrams == 0 else np.mean([t for n, t in res_bigrams])
    if runs_rand != 0:
        utils.write_f_t_results(res_rand, 'rand', max_len, is_triangle=True)
    if runs_dist != 0:
        utils.write_f_t_results(res_dist, 'dist', max_len, is_triangle=True)
    if runs_bigrams != 0:
        utils.write_f_t_results(res_bigrams, 'bigrams', max_len, is_triangle=True)
    return ((f_rand, f_dist, f_bigrams), (t_rand, t_dist, t_bigrams))


def p_measure(runs_rand=1000, runs_dist=10, runs_bigrams=100, tgen_budget=50, max_len=10):
    res_rand = []
    print(f'**** Running Rand ({runs_rand}) ****')
    for i in range(runs_rand):
        res_rand.append(random_gen(test_gen_budget=tgen_budget, max_len=max_len))
        print(f'{i+1}/{runs_rand}')
    # res_rand = [random_gen(test_gen_budget=tgen_budget) for i in range(runs_rand)]
    res_dist = []
    print(f'**** Running Dist ({runs_dist}) ****')
    for i in range(runs_dist):
        res_dist.append(ART_dist(test_gen_budget=tgen_budget, max_len=max_len))
        print(f'{i+1}/{runs_dist}')
    # res_dist = [ART_dist(test_gen_budget=tgen_budget) for i in range(runs_dist)]
    res_bigrams = []
    print(f'**** Running Bigram ({runs_bigrams}) ****')
    for i in range(runs_bigrams):
        res_bigrams.append(ART_bigram(test_gen_budget=tgen_budget, max_len=max_len))
        print(f'{i+1}/{runs_bigrams}')
    # res_bigrams = [ART_bigram(test_gen_budget=tgen_budget) for i in range(runs_bigrams)]
    p_rand = 0 if runs_rand == 0 else np.mean(res_rand)
    p_dist = 0 if runs_dist == 0 else np.mean(res_dist)
    p_bigrams = 0 if runs_bigrams == 0 else np.mean(res_bigrams)
    if runs_rand != 0:
        utils.write_p_results(res_rand, 'rand', max_len, is_triangle=True)
    if runs_dist != 0:
        utils.write_p_results(res_dist, 'dist', max_len, is_triangle=True)
    if runs_bigrams != 0:
        utils.write_p_results(res_bigrams, 'bigrams', max_len, is_triangle=True)
    return (p_rand, p_dist, p_bigrams)


args = argparse.ArgumentParser()
args.add_argument(
    "--delay",
    help="Add 10 ms delay to the execution of the palindrome function",
    action="store_true",
    default=False,
)
args.add_argument(
    "--max-side-length",
    help="Maximum input triangle side, controlling the failure rate",
    type=int,
    choices=[10, 100, 300],
    default=10,
)
args.add_argument(
    "--runs-rand",
    help="Number of runs for random generation",
    type=int,
    default=1000,
)
args.add_argument(
    "--runs-dist",
    help="Number of runs for ART_dist",
    type=int,
    default=10,
)
args.add_argument(
    "--runs-bigrams",
    help="Number of runs for ART_bigrams",
    type=int,
    default=100,
)
#args, _ = args.parse_args()
args = args.parse_args()


# python test_gen_triangle.py --max-side-length 100 --runs-rand 100 --runs-dist 100 --runs-bigrams 100
if __name__ == '__main__':
    MAX_SIDE_LENGTH = args.max_side_length
    ADD_DELAY = args.delay
    runs_rand = args.runs_rand
    runs_dist = args.runs_dist
    runs_bigrams = args.runs_bigrams
    if not os.path.exists('results_tr'):
        os.makedirs('results_tr')

    assert runs_rand >= 0, "Number of runs for random generation must be non-negative"
    assert runs_dist >= 0, "Number of runs for ART_dist must be non-negative"
    assert runs_bigrams >= 0, "Number of runs for ART_bigrams must be non-negative"
    DELAY_SUFFIX = ""
    if ADD_DELAY:
        DELAY_SUFFIX = "_del"  # '_del' when delay is true; '' otherwise
    print("===== Computing p-measure =====")
    p_measure(
        runs_rand=runs_rand,
        runs_dist=runs_dist,
        runs_bigrams=runs_bigrams,
        max_len=MAX_SIDE_LENGTH,
    )
    print("===== Computing f-measure and t-measure =====")
    f_t_measure(
        runs_rand=runs_rand,
        runs_dist=runs_dist,
        runs_bigrams=runs_bigrams,
        delay=ADD_DELAY,
        max_len=MAX_SIDE_LENGTH,
    )
    utils.write_summary_statistics(delay=ADD_DELAY, is_triangle=True)
    p_val = utils.compare_P_meas(
        f"results_tr/P_measure_bigrams_{MAX_SIDE_LENGTH}.csv",
        f"results_tr/P_measure_rand_{MAX_SIDE_LENGTH}.csv",
    )
    p_val1, p_val2 = utils.compare_F_T_meas(
        f"results_tr/F_T_measure_bigrams_{MAX_SIDE_LENGTH}.csv",
        f"results_tr/F_T_measure_rand_{MAX_SIDE_LENGTH}.csv",
    )
    print(f'Bigrams vs Rand (P-meas): p-val = {p_val}')
    print(f'Bigrams vs Rand (F-meas): p-val = {p_val1}')
    print(f'Bigrams vs Rand (T-meas): p-val = {p_val2}')
