from bisect import bisect_left
from typing import List, Tuple
from scipy.stats import wilcoxon, mannwhitneyu, rankdata, ranksums


def wilcoxon_pvalue(a: List, b: List) -> float:
    # paired test
    assert len(a) == len(b), "Lists should have the same length"
    return wilcoxon(a=a, b=b).pvalue


def wilcoxon_unpaired_pvalue(a: List, b: List) -> float:
    # unpaired test
    return ranksums(x=a, y=b).pvalue


def mannwhitneyu_pvalue(a: List, b: List) -> float:
    # unpaired test
    return mannwhitneyu(x=a, y=b).pvalue


def vargha_delaney(a: List[float], b: List[float]) -> Tuple[float, str]:
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000
    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/
    :param a: a numeric list
    :param b: another numeric list
    :returns the value estimate and the magnitude
    """
    m = len(a)
    n = len(b)

    assert m == n, "The two list must be of the same length: {}, {}".format(m, n)

    r = rankdata(a + b)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (
        2 * n * m
    )  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude
