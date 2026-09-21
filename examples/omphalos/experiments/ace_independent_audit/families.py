"""Conservative proof-method clustering, reviewed from the 80 allowed statements.

These are broader than literal duplicate theorems. Report this sensitivity
alongside theorem clusters; do not call every member a duplicate problem.
No result, cost or solver outcome enters the assignments.
"""

from .common import CAMPAIGN, allowed, save

GROUPS = {
    "functional_recurrences": "aime_1984_p1 aime_1984_p7 aime_1988_p8 amc12a_2013_p7 amc12a_2017_p7 imo_1977_p6 imo_1981_p6 mathd_numbertheory_405",
    "product_induction": "algebra_amgm_sum1toneqn_prod1tonleq1 induction_pord1p1on2powklt5on2 induction_prod1p1onk3le3m1onn",
    "finite_sums_and_products": "amc12a_2003_p1 amc12a_2008_p4 mathd_numbertheory_221 mathd_numbertheory_403 mathd_numbertheory_461 mathd_numbertheory_303",
    "gcd_lcm": "amc12a_2020_p21 mathd_numbertheory_37 mathd_numbertheory_530 mathd_numbertheory_629",
    "modular_arithmetic": "mathd_numbertheory_301 mathd_numbertheory_33 mathd_numbertheory_42 mathd_numbertheory_458 mathd_numbertheory_64",
    "natural_exponents": "amc12a_2016_p2 amc12b_2004_p3 imo_1984_p6 mathd_numbertheory_43",
    "natural_polynomials": "amc12_2000_p1 amc12_2000_p12 amc12_2001_p21 amc12a_2002_p6 amc12b_2020_p5 mathd_numbertheory_284 mathd_numbertheory_326 mathd_numbertheory_48",
    "prime_divisibility": "amc12_2000_p6 amc12b_2002_p11 amc12b_2002_p3 imo_1967_p3",
    "triangle_polynomial_inequalities": "imo_1964_p2 imo_1983_p6",
    "polynomial_lower_bounds": "mathd_algebra_28 mathd_algebra_410",
    "real_polynomial_equations": "aime_1989_p8 mathd_algebra_206 mathd_algebra_214 mathd_algebra_234 mathd_algebra_247 mathd_algebra_37 mathd_algebra_421 mathd_algebra_43",
    "reciprocal_equations": "aime_1990_p4 amc12a_2013_p8 mathd_algebra_251",
    "roots_and_absolute_values": "amc12a_2002_p13 amc12b_2003_p6 imo_1960_p2 imo_1968_p5_1 mathd_algebra_327 mathd_algebra_433",
    "logarithms_and_real_powers": "aime_1988_p3 amc12a_2020_p13 amc12b_2003_p17",
    "trigonometry": "aime_1991_p9 imo_1963_p5 imo_1969_p2",
    "inverse_functions": "mathd_algebra_323 mathd_algebra_393",
    "ensemble_cardinality": "mathd_algebra_185 mathd_algebra_224",
    "rounding_and_rationality": "aime_1991_p6 amc12a_2016_p3 mathd_algebra_282",
}


def mapping() -> dict[str, str]:
    names = allowed()
    result: dict[str, str] = {}
    for group, members in GROUPS.items():
        for name in members.split():
            if name not in names or name in result:
                raise ValueError(
                    "Invalid or repeated development family member: " + name
                )
            result[name] = group
    for name in names:
        result.setdefault(name, name)
    return result


def prepare() -> None:
    result = mapping()
    save(
        CAMPAIGN / "families.json",
        dict(
            mapping=result,
            groups=len(set(result.values())),
            method="Manual review of allowed formal statements; broad proof-method families, independent of outcomes. Exact numeral/variable-normalized statement equality found no duplicates. Main theorem-cluster and conservative method-family analyses are both reported.",
        ),
    )


if __name__ == "__main__":
    prepare()
