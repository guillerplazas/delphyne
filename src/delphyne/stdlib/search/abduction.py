"""
Strategies and Policies for Recursive Abduction.
"""

import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol, cast

import delphyne.core as dp
from delphyne.stdlib.nodes import spawn_node
from delphyne.stdlib.policies import log, search_policy
from delphyne.stdlib.streams import take_all, take_one

# For readability of the `Abduction` definition
type _Fact = Any
type _Proof = Any
type _Feedback = Any
type _Status = Any


@dataclass
class Abduction(dp.Node):
    """
    Node for the singleton tree produced by `abduction`.
    See `abduction` for details.

    An action is a successful proof of the main goal.
    """

    prove: Callable[
        [Sequence[tuple[_Fact, _Proof]], _Fact | None],
        dp.OpaqueSpace[Any, _Status],
    ]
    suggest: Callable[
        [_Feedback],
        dp.OpaqueSpace[Any, Sequence[_Fact]],
    ]
    search_equivalent: Callable[
        [Sequence[_Fact], _Fact],
        dp.OpaqueSpace[Any, _Fact | None],
    ]
    redundant: Callable[
        [Sequence[_Fact], _Fact],
        dp.OpaqueSpace[Any, bool],
    ]

    def navigate(self) -> dp.Navigation:
        def aux(fact: dp.Tracked[_Fact] | None) -> dp.Navigation:
            res = yield self.prove([], fact)
            status, payload = res[0], res[1]
            if status.value == "proved":
                return payload
            elif status.value == "disproved":
                assert False
            else:
                assert status.value == "feedback"
                feedback = payload
                suggestions = yield self.suggest(feedback)
                proved: list[Any] = []
                for s in suggestions:
                    proved.append((s, (yield from aux(s))))
                res = yield self.prove(proved, fact)
                status, payload = res[0], res[1]
                assert status.value == "proved"
                return payload

        return (yield from aux(None))


type AbductionStatus[Feedback, Proof] = (
    tuple[Literal["disproved"], None]
    | tuple[Literal["proved"], Proof]
    | tuple[Literal["feedback"], Feedback]
)


def abduction[Fact, Feedback, Proof, P](
    prove: Callable[
        [Sequence[tuple[Fact, Proof]], Fact | None],
        dp.OpaqueSpaceBuilder[P, AbductionStatus[Feedback, Proof]],
    ],
    suggest: Callable[
        [Feedback],
        dp.OpaqueSpaceBuilder[P, Sequence[Fact]],
    ],
    search_equivalent: Callable[
        [Sequence[Fact], Fact], dp.OpaqueSpaceBuilder[P, Fact | None]
    ],
    redundant: Callable[
        [Sequence[Fact], Fact], dp.OpaqueSpaceBuilder[P, bool]
    ],
    inner_policy_type: type[P] | None = None,
) -> dp.Strategy[Abduction, P, Proof]:
    """
    Higher-order strategy for proving a fact via recursive abduction.

    Arguments:

      prove: take a sequence of already established facts as an
        argument along with a new fact, and attempt to prove this new
        fact. Three outcomes are possible: the fact is proved,
        disproved, or a list of suggestions are made that might be
        helpful to prove first. `None` denotes the top-level goal to be
        proved.

      suggest: take some feedback from the `prove` function and return a
        sequence of fact candidates that may be useful to prove before
        reattempting the original proof.

      search_equivalent: take a collection of facts along with a new
        one, and return either the first fact of the list equivalent to
        the new fact or `None`. This is used to avoid spending search in
        proving equivalent facts.

      redundant: take a collection of established facts and decide
        whether they imply a new fact candidate. This is useful to avoid
        trying to prove and accumulating redundant facts.

    Returns:
      a proof of the top-level goal.
    """
    res = yield spawn_node(
        Abduction,
        prove=prove,
        suggest=suggest,
        search_equivalent=search_equivalent,
        redundant=redundant,
    )
    return cast(Proof, res)


#####
##### Policies
#####


@dataclass
class _CandInfo:
    feedback: dp.Tracked[_Feedback]
    num_proposed: float
    num_visited: float


class _Abort(Exception): ...


class _ProofFound(Exception): ...


type _EFact = _Fact | None  # an extended fact
type _Tracked_EFact = dp.Tracked[_Fact] | None


class ScoringFunction(Protocol):
    def __call__(self, num_proposed: float, num_visited: float) -> float: ...


def _default_scoring_function(
    num_proposed: float, num_visited: float
) -> float:
    return -(num_visited / max(1, math.sqrt(num_proposed)))


def _argmax(seq: Iterable[float]) -> int:
    return max(enumerate(seq), key=lambda x: x[1])[0]


@search_policy
def abduct_and_saturate[P, Proof](
    tree: dp.Tree[Abduction, P, Proof],
    env: dp.PolicyEnv,
    policy: P,
    max_rollout_depth: int = 3,
    scoring_function: ScoringFunction = _default_scoring_function,
    verbose: bool = False,
) -> dp.Stream[Proof]:
    """
    A standard, sequential policy to process abduction nodes.

    Note: facts must be hashable.
    """

    # TODO: we are currently allowing redundant facts in `proved` since
    # we never clean up `proved`. For example, if `x > 0` is established
    # before the stronger `x >= 0`, the former won't be deleted from
    # `proved`.

    # Invariant: `candidates`, `proved`, `disproved` and `redundant` are
    # disjoint. Together, they form the set of "canonical facts".
    candidates: dict[_EFact, _CandInfo] = {}
    proved: dict[_EFact, _Proof] = {}
    disproved: set[_EFact] = set()
    # Facts that are implied by the conjunction of all proved facts.
    redundant: set[_EFact] = set()

    # It is easier to manipulate untracked facts and so we keep the
    # correspondence with tracked facts here.
    # Invariant: all canonical facts are included in `tracked`.
    tracked: dict[_EFact, _Tracked_EFact] = {None: None}

    # The `equivalent` dict maps a fact to its canonical equivalent
    # representative that is somewhere in `candidates`, `proved`,
    # `disproved` or `redundant`.
    equivalent: dict[_EFact, _EFact] = {}

    # Can a new fact make a candidate redundant? YES. So we should also
    # do this in `propagate`

    assert isinstance(tree.node, Abduction)
    node = tree.node

    def dbg(msg: str):
        if verbose:
            log(env, msg)

    def all_canonical() -> Sequence[_EFact]:
        return [*candidates, *proved, *disproved, *redundant]

    def is_redundant(f: _EFact) -> dp.StreamGen[bool]:
        respace = node.redundant([tracked[o] for o in proved], tracked[f])
        res = yield from take_one(respace.stream(env, policy))
        if res is None:
            raise _Abort()
        return res.value

    def add_candidate(c: _EFact) -> dp.StreamGen[None]:
        # Take a new fact and put it into either `proved`, `disproved`,
        # `candidates` or `redundant`. If a canonical fact is passed,
        # nothing is done.
        if c in all_canonical():
            return
        # We first make a redundancy check
        if (yield from is_redundant(c)):
            dbg(f"Redundant: {c}")
            redundant.add(c)
            return
        # If not redundant, we try and prove it
        facts_list = [(tracked[f], p) for f, p in proved.items()]
        pstream = node.prove(facts_list, tracked[c]).stream(env, policy)
        res = yield from take_one(pstream)
        if res is None:
            raise _Abort()
        status, payload = res[0], res[1]
        if status.value == "disproved":
            disproved.add(c)
            dbg(f"Disproved: {c}")
            if c is None:
                raise _Abort()
        elif status.value == "proved":
            proved[c] = payload
            dbg(f"Proved: {c}")
            if c is None:
                raise _ProofFound()
        else:
            candidates[c] = _CandInfo(payload, 0, 0)

    def propagate() -> dp.StreamGen[Literal["updated", "not_updated"]]:
        # Go through each candidate and see if it is now provable
        # assuming all established facts.
        old_candidates = candidates.copy()
        candidates.clear()
        for c, i in old_candidates.items():
            yield from add_candidate(c)
            if c in candidates:
                # Restore the counters if `c` is still a candidate
                candidates[c].num_proposed = i.num_proposed
                candidates[c].num_visited = i.num_visited
        return (
            "updated"
            if len(candidates) != len(old_candidates)
            else "not_updated"
        )

    def saturate() -> dp.StreamGen[None]:
        # Propagate facts until saturation
        while (yield from propagate()) == "updated":
            pass

    def get_canonical(f: _EFact) -> dp.StreamGen[_EFact]:
        # The result is guaranteed to be in `tracked`
        if f in proved or f in disproved or f in candidates:
            # Case where f is a canonical fact
            return f
        if f in equivalent:
            # Case where an equivalent canonical fact is known already
            nf = equivalent[f]
            assert nf in all_canonical()
            return equivalent[f]
        # New fact whose equivalence must be tested
        eqspace = node.search_equivalent(
            [tracked[o] for o in all_canonical()], tracked[f]
        )
        res = yield from take_one(eqspace.stream(env, policy))
        if res is None:
            raise _Abort()
        if res.value is None:
            return f
        elif res.value in all_canonical():
            equivalent[f] = res.value
            return res.value
        else:
            log(env, "invalid_equivalent_call")
            return f

    def get_raw_suggestions(c: _EFact) -> dp.StreamGen[Sequence[_EFact]]:
        assert c in candidates
        sstream = node.suggest(candidates[c].feedback).stream(env, policy)
        res = yield from take_all(sstream)
        tracked_suggs = [s for r in res for s in r]
        # Populate the `tracked` cache (this is the only place where new
        # facts can be created and so the only place where `tracked`
        # must be updated).
        suggs = [s.value for s in tracked_suggs]
        dbg(f"Suggestions: {suggs}")
        for s, ts in zip(suggs, tracked_suggs):
            if s not in tracked:
                tracked[s] = ts
        return suggs

    def get_suggestions(c: _EFact) -> dp.StreamGen[dict[_EFact, int]]:
        # Return a dict representing a multiset of suggestions
        assert c in candidates
        raw_suggs = yield from get_raw_suggestions(c)
        suggs: list[_EFact] = []
        for s in raw_suggs:
            suggs.append((yield from get_canonical(s)))
        len_proved_old = len(proved)
        for s in suggs:
            yield from add_candidate(s)
        if len_proved_old != len(proved):
            assert len(proved) > len_proved_old
            yield from saturate()
        suggs = [s for s in suggs if s in candidates]
        suggs_multiset: dict[_EFact, int] = {}
        for s in suggs:
            if s not in suggs_multiset:
                suggs_multiset[s] = 0
            suggs_multiset[s] += 1
        dbg(f"Filtered: {suggs_multiset}")
        return suggs_multiset

    try:
        yield from add_candidate(None)
        while True:
            cur: _EFact = None
            for _ in range(max_rollout_depth):
                dbg(f"Explore fact: {cur}")
                suggs = yield from get_suggestions(cur)
                if not suggs:
                    break
                n = sum(suggs.values())
                for s, k in suggs.items():
                    candidates[s].num_proposed += k / n
                infos = [candidates[c] for c in suggs]
                best = _argmax(
                    scoring_function(i.num_proposed, i.num_visited)
                    for i in infos
                )
                cur = list(suggs.keys())[best]
                candidates[cur].num_visited += 1
    except _Abort:
        return
    except _ProofFound:
        action = proved[None]
        child = tree.child(action)
        assert isinstance(child.node, dp.Success)
        yield dp.Yield(child.node.success)
        return
