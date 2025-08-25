"""
Standard commands for running strategies.
"""

import dbm
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Literal, cast

import delphyne.analysis as analysis
import delphyne.analysis.feedback as fb
import delphyne.core as dp
import delphyne.stdlib.environments as en
import delphyne.stdlib.models as md
import delphyne.stdlib.policies as pol
import delphyne.stdlib.tasks as ta
import delphyne.utils.caching as ca
from delphyne.core.streams import Barrier, Solution, Spent
from delphyne.utils.typing import pydantic_dump

type CacheFormat = Literal["yaml", "db"]
"""
Format used to store the cache on disk:

- `yaml`: the cache is stored in YAML files, one file per hash
- `db`: the cache is stored in a database
"""


@dataclass(kw_only=True)
class RunStrategyResponse:
    """
    Response type for the `run_strategy` command.

    Attributes:
        success: Whether at least one success value was generated.
        values: Generated success values.
        spent_budegt: Spent budget.
        raw_trace: Raw trace of the strategy execution, if requested.
        log: Log messages generated during the strategy execution.
        browsable_trace: A browsable trace, if requested.
    """

    success: bool
    values: Sequence[Any | None]
    spent_budget: Mapping[str, float]
    raw_trace: dp.ExportableTrace | None
    log: Sequence[dp.ExportableLogMessage] | None
    browsable_trace: fb.Trace | None


@dataclass(kw_only=True)
class RunLoadedStrategyArgs[N: dp.Node, P, T]:
    """
    Arguments for the `run_loaded_strategy` command.

    See `RunStrategyArgs` for details.
    """

    strategy: dp.StrategyComp[N, P, T]
    policy: pol.Policy[N, P]
    num_generated: int = 1
    budget: dict[str, float] | None = None
    cache_dir: str | None = None
    cache_mode: ca.CacheMode = "read_write"
    cache_format: CacheFormat = "yaml"
    export_raw_trace: bool = True
    export_log: bool = True
    export_browsable_trace: bool = True


def run_loaded_strategy_with_cache[N: dp.Node, P, T](
    task: ta.TaskContext[ta.CommandResult[RunStrategyResponse]],
    exe: ta.CommandExecutionContext,
    args: RunLoadedStrategyArgs[N, P, T],
    cache_spec: ca.CacheSpec | None,
):
    env = en.PolicyEnv(
        prompt_dirs=exe.prompt_dirs,
        data_dirs=exe.data_dirs,
        demonstration_files=exe.demo_files,
        cache=cache_spec,
        do_not_match_identical_queries=True,
    )
    cache: dp.TreeCache = {}
    monitor = dp.TreeMonitor(cache, hooks=[dp.tracer_hook(env.tracer)])
    tree = dp.reify(args.strategy, monitor)
    policy = args.policy
    stream = policy.search(tree, env, policy.inner)
    if args.budget is not None:
        stream = stream.with_budget(dp.BudgetLimit(args.budget))
    stream = stream.take(args.num_generated)
    results: list[T] = []
    success = False
    total_budget = dp.Budget.zero()

    def serialize_result(res: T) -> Any | None:
        ret_type = args.strategy.return_type()
        return pydantic_dump(ret_type, res)

    def compute_result():
        trace = env.tracer.trace
        raw_trace = trace.export() if args.export_raw_trace else None
        browsable_trace = (
            analysis.compute_browsable_trace(trace, cache)
            if args.export_browsable_trace
            else None
        )
        log = list(env.tracer.export_log()) if args.export_log else None
        values = [serialize_result(r) for r in results]
        response = RunStrategyResponse(
            success=success,
            values=values,
            spent_budget=total_budget.values,
            raw_trace=raw_trace,
            log=log,
            browsable_trace=browsable_trace,
        )
        return ta.CommandResult([], response)

    def compute_status():
        num_nodes = len(env.tracer.trace.nodes)
        num_requests = total_budget.values.get(md.NUM_REQUESTS)
        price = total_budget.values.get(md.DOLLAR_PRICE)

        ret: list[str] = [f"{num_nodes} nodes"]
        if num_requests is not None:
            # If num_requests is a float equal to an int, cast to int
            # for display
            if isinstance(num_requests, float) and num_requests.is_integer():
                num_requests = int(num_requests)
            ret += [f"{num_requests} requests"]
        if price is not None:
            price *= 100  # in cents
            ret += [f"{price:.2g}¢"]

        return ", ".join(ret)

    last_refreshed_result = time.time()
    last_refreshed_status = time.time()
    # TODO: generating each element is blocking here. Should we spawn a
    # thread for every new element?
    for msg in stream.gen():
        match msg:
            case Solution():
                success = True
                results.append(msg.tracked.value)
            case Spent(b):
                total_budget += b
            case Barrier():
                pass
        interrupted = task.interruption_requested()
        if interrupted or (
            exe.result_refresh_period is not None
            and time.time() - last_refreshed_result > exe.result_refresh_period
        ):
            task.set_result(compute_result())
            last_refreshed_result = time.time()
        if (
            exe.status_refresh_period is not None
            and time.time() - last_refreshed_status > exe.status_refresh_period
        ):
            task.set_status(compute_status())
            last_refreshed_status = time.time()
        if interrupted:
            break
    task.set_result(compute_result())


def run_loaded_strategy[N: dp.Node, P, T](
    task: ta.TaskContext[ta.CommandResult[RunStrategyResponse]],
    exe: ta.CommandExecutionContext,
    args: RunLoadedStrategyArgs[N, P, T],
):
    """
    Command for running an oracular program.
    """
    with_cache_spec(
        partial(run_loaded_strategy_with_cache, task, exe, args),
        cache_root=exe.cache_root,
        cache_dir=args.cache_dir,
        cache_mode=args.cache_mode,
        cache_format=args.cache_format,
    )


def with_cache_spec[T](
    f: Callable[[ca.CacheSpec | None], T],
    *,
    cache_root: Path | None,
    cache_dir: str | None,
    cache_mode: ca.CacheMode,
    cache_format: CacheFormat,
) -> T:
    cache_spec = None
    db: Any | None = None
    if cache_dir is not None:
        assert cache_root is not None, "Nonspecified cache root."
        cache_dir_path = cache_root / cache_dir
        if cache_format == "yaml":
            cache_info = ca.CacheYaml(cache_dir_path)
        else:
            db = dbm.open(ca.cache_database_file(cache_dir_path), "c")
            cache_info = ca.CacheDb(db)
        cache_spec = ca.CacheSpec(cache_info, mode=cache_mode)
    try:
        return f(cache_spec)
    finally:
        if db is not None:
            db.close()


@dataclass(kw_only=True)
class RunStrategyArgs:
    """
    Arguments for the `run_strategy` command that runs an oracular
    program.

    Attributes:
        strategy: Name of the strategy to run.
        args: Arguments to pass to the strategy constructor.
        policy: Name of the policy to use.
        policy_args: Arguments to pass to the policy constructor.
        num_generated: Number of success values to generate.
        budget: Budget limit (infinite for unspecified metrics).
        cache_dir: Subdirectory of the global cache directory to use for
            caching, or `None` to disable caching.
        cache_mode: Cache mode to use.
        cache_format: Cache format to use.
        export_raw_trace: Whether to export the raw execution trace.
        export_log: Whether to export the log messages.
        export_browsable_trace: Whether to export a browsable trace,
            which can be visualized in the VSCode extension (see
            [delphyne.analysis.feedback.Trace][]).
    """

    strategy: str
    args: dict[str, object]
    policy: str
    policy_args: dict[str, object]
    budget: dict[str, float]
    num_generated: int = 1
    cache_dir: str | None = None
    cache_mode: ca.CacheMode = "read_write"
    cache_format: CacheFormat = "yaml"
    export_raw_trace: bool = True
    export_log: bool = True
    export_browsable_trace: bool = True


def run_strategy(
    task: ta.TaskContext[ta.CommandResult[RunStrategyResponse]],
    exe: ta.CommandExecutionContext,
    args: RunStrategyArgs,
):
    """
    Command for running an oracular program from a serialized
    specification.
    """
    loader = analysis.ObjectLoader(exe.base)
    strategy = loader.load_strategy_instance(args.strategy, args.args)
    policy = loader.load_and_call_function(args.policy, args.policy_args)
    assert isinstance(policy, dp.AbstractPolicy)
    policy = cast(pol.Policy[Any, Any], policy)
    run_loaded_strategy(
        task=task,
        exe=exe,
        args=RunLoadedStrategyArgs(
            strategy=strategy,
            policy=policy,
            num_generated=args.num_generated,
            budget=args.budget,
            cache_dir=args.cache_dir,
            cache_mode=args.cache_mode,
            cache_format=args.cache_format,
            export_raw_trace=args.export_raw_trace,
            export_log=args.export_log,
            export_browsable_trace=args.export_browsable_trace,
        ),
    )
