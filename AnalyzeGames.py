from dataclasses import dataclass
from typing import Tuple
from math import isfinite
from scipy.stats import beta, binomtest

@dataclass
class Results:
    n: int
    k: int
    phat: float
    # Bayesian
    prior_alpha: float
    prior_beta: float
    post_alpha: float
    post_beta: float
    prob_p_gt_0_5: float
    bayes_ci_95: Tuple[float, float]
    bayes_mean: float
    # Frequentist
    pvalue_one_sided: float
    cp_ci_95: Tuple[float, float]

def analyze(k: int, n: int, prior_alpha: float = 1.0, prior_beta: float = 1.0) -> Results:
    """
    k: wins for Player 1
    n: total games
    prior_alpha, prior_beta: Beta prior parameters (1,1) = uniform prior
    """
    if not (0 <= k <= n):
        raise ValueError("Require 0 <= k <= n.")
    if prior_alpha <= 0 or prior_beta <= 0:
        raise ValueError("Beta prior parameters must be > 0.")

    phat = k / n if n > 0 else float("nan")

    # Bayesian posterior
    a_post = prior_alpha + k
    b_post = prior_beta + (n - k)

    # P(p > 0.5 | data) = survival function at 0.5
    prob_gt_half = beta.sf(0.5, a_post, b_post)

    # 95% Bayesian credible interval (equal-tailed)
    bayes_lo, bayes_hi = beta.ppf([0.025, 0.975], a_post, b_post)
    bayes_mean = a_post / (a_post + b_post)

    # Frequentist one-sided binomial test under H0: p=0.5, H1: p>0.5
    pval = binomtest(k, n, p=0.5, alternative="greater").pvalue

    # Exact (Clopper–Pearson) 95% CI
    cp_lo = beta.ppf(0.025, k, n - k + 1)
    cp_hi = beta.ppf(0.975, k + 1, n - k)

    return Results(
        n=n, k=k, phat=phat,
        prior_alpha=prior_alpha, prior_beta=prior_beta,
        post_alpha=a_post, post_beta=b_post,
        prob_p_gt_0_5=prob_gt_half,
        bayes_ci_95=(bayes_lo, bayes_hi),
        bayes_mean=bayes_mean,
        pvalue_one_sided=pval,
        cp_ci_95=(cp_lo, cp_hi)
    )

def pretty_print(res: Results) -> None:
    print(f"Data: k={res.k} wins out of n={res.n} games (p̂ = {res.phat:.3f})\n")
    print("Bayesian (Beta prior):")
    print(f"  Prior: Beta({res.prior_alpha:.3g}, {res.prior_beta:.3g})")
    print(f"  Posterior: Beta({res.post_alpha:.3g}, {res.post_beta:.3g})")
    print(f"  P(p > 0.5 | data) = {res.prob_p_gt_0_5:.6f}")
    print(f"  95% credible interval = [{res.bayes_ci_95[0]:.3f}, {res.bayes_ci_95[1]:.3f}]")
    print(f"  Posterior mean = {res.bayes_mean:.3f}\n")

    print("Frequentist:")
    print(f"  One-sided binomial test (H0: p=0.5, H1: p>0.5): p-value = {res.pvalue_one_sided:.6g}")
    print(f"  Exact Clopper–Pearson 95% CI = [{res.cp_ci_95[0]:.3f}, {res.cp_ci_95[1]:.3f}]")

res = analyze(15, 22)
pretty_print(res)