"""Exact illustrative power for independent paired binary observations.

Not a power calculation for two correlated seeds: specify independent
problem units. Discordances M~Binomial(n,q); favorable discordances
W|M~Binomial(M,(q+gain)/(2q)). Sum the probability of meeting the review's
observed-gain threshold and two-sided exact significance criterion.
The hypothesized true gain and required observed gain are separate inputs.
Set minimum_observed_gain=0 to count positive significant effects alone.
"""

# pyright: strict

import argparse
import json
import math


def power(
    n: int,
    gain: float,
    discordance: float,
    minimum_observed_gain: float = 0.05,
) -> float:
    if n < 1 or not 0 < gain <= discordance <= 1:
        raise ValueError("require n>=1 and 0<gain<=discordance<=1")
    if not 0 <= minimum_observed_gain <= 1:
        raise ValueError("require 0<=minimum_observed_gain<=1")
    q = discordance
    favorable = (q + gain) / (2 * q)
    result = 0.0
    for m in range(n + 1):
        mass = math.comb(n, m) * q**m * (1 - q) ** (n - m)
        tails: list[float] = []
        count = 0
        for k in range(m + 1):
            count += math.comb(m, k)
            tails.append(min(1.0, 2 * count / 2**m))
        for wins in range(m + 1):
            if (2 * wins - m) / n >= minimum_observed_gain and tails[
                min(wins, m - wins)
            ] < 0.05:
                result += (
                    mass
                    * math.comb(m, wins)
                    * favorable**wins
                    * (1 - favorable) ** (m - wins)
                )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=88)
    parser.add_argument("--gain", type=float, default=0.05)
    parser.add_argument("--discordance", type=float, default=0.1)
    parser.add_argument("--minimum_observed_gain", type=float, default=0.05)
    args = parser.parse_args()
    print(
        json.dumps(
            dict(
                n=args.n,
                gain=args.gain,
                discordance=args.discordance,
                minimum_observed_gain=args.minimum_observed_gain,
                power=power(
                    args.n,
                    args.gain,
                    args.discordance,
                    args.minimum_observed_gain,
                ),
            ),
            indent=2,
        )
    )
