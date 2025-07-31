"""
Demonstration Interpreter.
"""

import importlib
import json
import sys
import traceback
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import delphyne.core as dp
from delphyne.analysis import browsable_traces as br
from delphyne.analysis import feedback as fb
from delphyne.analysis import navigation as nv
from delphyne.core import demos as dm
from delphyne.core import refs
from delphyne.utils import typing as tp

#####
##### Environment Execution Context
#####


@dataclass
class ModuleNotFound(Exception):
    module_name: str


@dataclass
class ObjectNotFound(Exception):
    object_name: str


@dataclass
class StrategyLoadingError(Exception):
    message: str


@dataclass(frozen=True)
class DemoExecutionContext:
    strategy_dirs: Sequence[Path]
    modules: Sequence[str]

    def with_root(self, root: Path) -> "DemoExecutionContext":
        return DemoExecutionContext(
            strategy_dirs=[root / p for p in self.strategy_dirs],
            modules=self.modules,
        )


class ObjectLoader:
    def __init__(
        self,
        ctx: DemoExecutionContext,
        extra_objects: dict[str, object] | None = None,
        reload: bool = True,
    ):
        """
        Raises `ModuleNotFound`.
        Modules can be part of packages and so their name may feature `.`.
        """
        self.ctx = ctx
        self.extra_objects = extra_objects if extra_objects is not None else {}
        self.modules: list[Any] = []
        with _append_path(self.ctx.strategy_dirs):
            for module_name in ctx.modules:
                try:
                    module = __import__(module_name)
                    if reload:
                        module = importlib.reload(module)
                    self.modules.append(module)
                except AttributeError:
                    raise ModuleNotFound(module_name)

    def find_object(self, name: str) -> Any:
        """
        Find an object with a given name. If the name is unqualified (it
        features no `.`), one attempts to find the object in every
        registered module in order. If the name is qualified, one looks
        at the specified registered module.
        """
        if name in self.extra_objects:
            return self.extra_objects[name]
        comps = name.split(".")
        assert comps
        if len(comps) == 1:
            # unqualified name
            for module in self.modules:
                if hasattr(module, name):
                    return getattr(module, name)
        else:
            # qualified name
            module = ".".join(comps[:-1])
            attr = comps[-1]
            if hasattr(module, attr):
                return getattr(module, attr)
        raise ObjectNotFound(name)

    def load_and_call_function(self, name: str, args: dict[str, Any]) -> Any:
        f = self.find_object(name)
        args = tp.parse_function_args(f, args)
        return f(**args)

    def load_strategy_instance(
        self, name: str, args: dict[str, Any]
    ) -> dp.StrategyComp[Any, Any, Any]:
        f = self.find_object(name)
        try:
            args = tp.parse_function_args(f, args)
            comp = f(**args)
            assert isinstance(comp, dp.StrategyComp), (
                f"Object {name} is not a strategy function."
                + " Did you forget to use the @strategy decorator?"
            )
            return cast(Any, comp)
        except Exception as e:
            raise StrategyLoadingError(str(e))

    def load_query(
        self, name: str, args: dict[str, Any]
    ) -> dp.AbstractQuery[Any]:
        obj = self.find_object(name)
        assert issubclass(obj, dp.AbstractQuery), (
            f"Object {name} is not a query type."
        )
        q = cast(type[dp.AbstractQuery[Any]], obj)
        return q.parse_instance(args)


@contextmanager
def _append_path(paths: Sequence[Path]):
    sys.path = [str(p) for p in paths] + sys.path
    yield
    sys.path = sys.path[len(paths) :]


#####
##### Demo Hint Resolver
#####


@dataclass(frozen=True)
class SerializedQuery:
    """
    A representation of a query used as an index for the example cache.
    """

    name: str
    args: str

    @staticmethod
    def make(query: dp.AbstractQuery[Any]) -> "SerializedQuery":
        args = json.dumps(query.serialize_args())
        return SerializedQuery(query.name(), args)


class DemoHintResolver(nv.HintResolver):
    def __init__(self, loader: ObjectLoader, demo: dm.StrategyDemo):
        self.demo = demo
        self.queries: list[SerializedQuery] = []
        for i, q in enumerate(demo.queries):
            try:
                query = loader.load_query(q.query, q.args)
                self.queries.append(SerializedQuery.make(query))
            except Exception as e:
                raise DemoHintResolver.InvalidQuery(i, e)
            # We try to parse all answers in anticipation, to avoid
            # an error later.
            for j, a in enumerate(q.answers):
                parsed = query.parse_answer(dm.translate_answer(a))
                if isinstance(parsed, dp.ParseError):
                    raise DemoHintResolver.InvalidAnswer(i, j, parsed)
        # Used to populate `DemoFeedback.answer_refs`, which is needed
        # to implement the `Jump to Answer` action in the UI tree view.
        self.answer_refs: dict[nv.AnswerRef, fb.DemoAnswerId] = {}
        # To keep track of what queries are reachable
        self.query_used: list[bool] = [False] * len(self.queries)
        # Keeping track of implicit answers
        self.implicit: list[tuple[SerializedQuery, fb.ImplicitAnswer]] = []

    def __call__(
        self,
        query: dp.AttachedQuery[Any],
        hint: refs.HintValue | None,
        implicit_answer: Callable[[], str] | None,
    ) -> refs.Answer | None:
        serialized = SerializedQuery.make(query.query)
        # Look at the query demonstrations included in the demo
        for i, q in enumerate(self.queries):
            if q == serialized:
                self.query_used[i] = True
                answers = self.demo.queries[i].answers
                if not answers:
                    return None
                if hint is None:
                    answer_id = 0
                else:
                    for j, a in enumerate(answers):
                        if a.label == hint:
                            answer_id = j
                            break
                    else:
                        return None
                demo_answer = answers[answer_id]
                answer = dm.translate_answer(demo_answer)
                self.answer_refs[(query.ref, answer)] = (i, answer_id)
                return answer
        # We only look at implicit answers if no hint is provided.
        if hint is not None:
            return None
        # Look at previous implicit answers
        for serialized_key, a in self.implicit:
            if serialized == serialized_key:
                return refs.Answer(None, a.answer)
        # Maybe we try adding an implicit answer
        if implicit_answer:
            try:
                ans_text = implicit_answer()
            except Exception as e:
                raise dp.StrategyException(e)
            implicit = fb.ImplicitAnswer(
                query.query.name(), query.query.serialize_args(), ans_text
            )
            self.implicit.append((serialized, implicit))
            return refs.Answer(None, ans_text)
        return None

    def get_answer_refs(self) -> dict[nv.AnswerRef, fb.DemoAnswerId]:
        return self.answer_refs

    def get_implicit_answers(self) -> list[fb.ImplicitAnswer]:
        return [a for _, a in self.implicit]

    def set_reachability_diagnostics(self, feedback: fb.StrategyDemoFeedback):
        for i, used in enumerate(self.query_used):
            if not used:
                msg = "Unreachable query."
                feedback.query_diagnostics.append((i, ("warning", msg)))

    def navigator(self) -> nv.Navigator:
        return nv.Navigator(self)

    @dataclass
    class InvalidQuery(Exception):
        id: int
        exn: Exception

    @dataclass
    class InvalidAnswer(Exception):
        query_id: int
        answer_id: int
        parse_error: dp.ParseError


#####
##### Test Interpreter
#####


def _unused_hints(diagnostics: list[fb.Diagnostic], rem: Sequence[refs.Hint]):
    if rem:
        msg = f"Unused hints: {dp.pprint.hints(rem)}."
        diagnostics.append(("warning", msg))


def _strategy_exn(diagnostics: list[fb.Diagnostic], exn: dp.StrategyException):
    details = f"{repr(exn.exn)}\n\n{traceback.format_exc()}"
    msg = f"Exception raised in strategy:\n\n{details}"
    diagnostics.append(("error", msg))


def _stuck_warning(diagnostics: list[fb.Diagnostic], exn: nv.Stuck):
    msg = "Test is stuck."
    diagnostics.append(("warning", msg))


def _navigation_error(
    diagnostics: list[fb.Diagnostic], exn: dp.NavigationError
):
    details = f"{repr(exn.message)}\n\n{traceback.format_exc()}"
    msg = f"Navigation error:\n\n{details}"
    diagnostics.append(("error", msg))


type SavedNodes = dict[str, dp.AnyTree]


def _interpret_test_run_step(
    hint_resolver: DemoHintResolver,
    hint_rev: nv.HintReverseMap,
    diagnostics: list[fb.Diagnostic],
    tree: dp.AnyTree,
    tracer: dp.Tracer,
    step: dm.Run,
) -> tuple[dp.AnyTree, Literal["stop", "continue"]]:
    try:
        encountered = nv.EncounteredTags()
        navigator = hint_resolver.navigator()
        navigator.info = nv.NavigationInfo(hint_rev)
        navigator.tracer = tracer
        try:
            tree, rem = navigator.follow_hints(
                tree, step.hints, step.until, encountered
            )
        except nv.ReachedFailureNode as e:
            tree = e.tree
            rem = e.remaining_hints
        _unused_hints(diagnostics, rem)
        if step.until is not None:
            until_pp = dp.pprint.node_selector(step.until)
            msg = f"Leaf node reached before '{until_pp}'."
            diagnostics.append(("warning", msg))
        if step.until is None and not tree.node.leaf_node():
            msg = "The `run` command did not reach a leaf."
            diagnostics.append(("warning", msg))
        return tree, "continue"
    except nv.MatchedSelector as intr:
        tree = intr.tree
        _unused_hints(diagnostics, intr.remaining_hints)
        return tree, "continue"
    except nv.Stuck as stuck:
        tree = stuck.tree
        _stuck_warning(diagnostics, stuck)
        return tree, "stop"
    except dp.StrategyException as e:
        _strategy_exn(diagnostics, e)
        return tree, "stop"
    except dp.NavigationError as e:
        _navigation_error(diagnostics, e)
        return tree, "stop"


def _interpret_test_select_step(
    hint_resolver: DemoHintResolver,
    hint_rev: nv.HintReverseMap,
    diagnostics: list[fb.Diagnostic],
    tree: dp.AnyTree,
    tracer: dp.Tracer,
    step: dm.SelectSpace,
) -> tuple[dp.AnyTree, Literal["stop", "continue"]]:
    navigator = hint_resolver.navigator()
    nav_info = nv.NavigationInfo(hint_rev)
    navigator.info = nav_info
    navigator.tracer = tracer
    space_ref = step.space
    space_ref_pretty = dp.pprint.space_ref(space_ref)
    try:
        space = navigator.resolve_space_ref(tree, space_ref)
        source = space.source()
        _unused_hints(diagnostics, nav_info.unused_hints)
        if step.expects_query:
            if not isinstance(source, dp.AttachedQuery):
                msg = f"Not a query: {space_ref_pretty}."
                diagnostics.append(("error", msg))
                return tree, "stop"
            answer = hint_resolver(source, None, None)
            if answer is None:
                msg = f"Query not answered: {space_ref_pretty}."
                diagnostics.append(("error", msg))
                return tree, "stop"
            return tree, "continue"
        else:
            if not isinstance(source, dp.NestedTree):
                msg = f"Not a nested tree: {space_ref_pretty}."
                diagnostics.append(("error", msg))
                return tree, "stop"
            tree = source.spawn_tree()
            return tree, "continue"
    except nv.ReachedFailureNode as e:
        tree = e.tree
        msg = f"Failed to reach: {space_ref_pretty}"
        diagnostics.append(("error", msg))
        return tree, "stop"
    except nv.Stuck as stuck:
        tree = stuck.tree
        _stuck_warning(diagnostics, stuck)
        return tree, "stop"
    except dp.StrategyException as e:
        _strategy_exn(diagnostics, e)
        return tree, "stop"
    except dp.NavigationError as e:
        _navigation_error(diagnostics, e)
        return tree, "stop"
    except nv.InvalidSpace as e:
        tree = e.tree
        name = dp.pprint.space_name(e.space_name)
        msg = f"Invalid reference to space '{name}'."
        diagnostics.append(("error", msg))
        return tree, "stop"
    except nv.NoPrimarySpace as e:
        tree = e.tree
        msg = f"Node {tree.node.effect_name()} has no primary space"
        diagnostics.append(("error", msg))
        return tree, "stop"


def _interpret_test_step(
    hint_resolver: DemoHintResolver,
    hint_rev: nv.HintReverseMap,
    diagnostics: list[fb.Diagnostic],
    saved: SavedNodes,
    tree: dp.AnyTree,
    tracer: dp.Tracer,
    step: dm.TestStep,
) -> tuple[dp.AnyTree, Literal["stop", "continue"]]:
    match step:
        case dm.Run():
            return _interpret_test_run_step(
                hint_resolver, hint_rev, diagnostics, tree, tracer, step
            )
        case dm.SelectSpace():
            return _interpret_test_select_step(
                hint_resolver, hint_rev, diagnostics, tree, tracer, step
            )
        case dm.IsSuccess():
            if not isinstance(tree.node, dp.Success):
                msg = "Success check failed."
                diagnostics.append(("error", msg))
                return tree, "stop"
            else:
                return tree, "continue"
        case dm.IsFailure():
            node = tree.node
            if not (node.leaf_node() and not isinstance(node, dp.Success)):
                msg = "Failure check failed."
                diagnostics.append(("error", msg))
                return tree, "stop"
            else:
                return tree, "continue"
        case dm.Save():
            saved[step.name] = tree
            return tree, "continue"
        case dm.Load():
            if step.name not in saved:
                msg = f"No saved node named: '{step.name}'."
                diagnostics.append(("error", msg))
                return tree, "stop"
            return saved[step.name], "continue"


def _evaluate_test(
    root: dp.AnyTree,
    tracer: dp.Tracer,
    hint_resolver: DemoHintResolver,
    hint_rev: nv.HintReverseMap,
    saved: SavedNodes,
    test_str: dm.TestCommandString,
) -> fb.TestFeedback:
    diagnostics: list[fb.Diagnostic] = []
    tree = root
    try:
        test = dp.parse.test_command(test_str)
    except dp.parse.ParseError:
        diagnostics = [("error", "Syntax error.")]
        return fb.TestFeedback(diagnostics, None)
    for step in test:
        tree, status = _interpret_test_step(
            hint_resolver, hint_rev, diagnostics, saved, tree, tracer, step
        )
        if status == "stop":
            break
    ref = tracer.trace.convert_global_node_path(tree.ref)
    return fb.TestFeedback(diagnostics, ref.id)


#####
##### Strategy Demo Evaluation
#####


def evaluate_strategy_demo_and_return_trace(
    demo: dm.StrategyDemo,
    context: DemoExecutionContext,
    extra_objects: dict[str, object],
) -> tuple[fb.StrategyDemoFeedback, dp.Trace | None]:
    feedback = fb.StrategyDemoFeedback(
        "strategy", fb.Trace({}), {}, {}, [], [], [], [], []
    )
    try:
        loader = ObjectLoader(context, extra_objects)
        strategy = loader.load_strategy_instance(demo.strategy, demo.args)
    except Exception as e:
        msg = f"Failed to instantiate strategy:\n{e}"
        feedback.global_diagnostics.append(("error", msg))
        return feedback, None
    try:
        cache: dp.TreeCache = {}
        tracer = dp.Tracer()
        trace = tracer.trace
        monitor = dp.TreeMonitor(cache=cache, hooks=[dp.tracer_hook(tracer)])
        tree = dp.reify(strategy, monitor)
    except dp.StrategyException as e:
        _strategy_exn(feedback.global_diagnostics, e)
        return feedback, None
    try:
        hresolver = DemoHintResolver(loader, demo)
    except DemoHintResolver.InvalidQuery as e:
        msg = f"Failed to load query:\n{e.exn}"
        feedback.query_diagnostics.append((e.id, ("error", msg)))
        return feedback, trace
    except DemoHintResolver.InvalidAnswer as e:
        msg = f"Failed to parse answer:\n{e.parse_error}"
        diag = ("error", msg)
        feedback.answer_diagnostics.append(((e.query_id, e.answer_id), diag))
        return feedback, trace
    saved: SavedNodes = {}
    rm: nv.HintReverseMap = nv.HintReverseMap()
    for test_str in demo.tests:
        test_feedback = _evaluate_test(
            tree, tracer, hresolver, rm, saved, test_str
        )
        feedback.test_feedback.append(test_feedback)
    feedback.saved_nodes = {
        k: tracer.trace.convert_global_node_path(v.ref).id
        for k, v in saved.items()
    }
    trace.check_consistency()
    hresolver.set_reachability_diagnostics(feedback)
    simplifier = br.RefSimplifier(cache, rm)
    feedback.trace = br.compute_browsable_trace(trace, cache, simplifier)
    feedback.answer_refs = {
        trace.convert_answer_ref(k).id: v
        for k, v in hresolver.get_answer_refs().items()
    }
    feedback.implicit_answers = hresolver.get_implicit_answers()
    return feedback, trace


#####
##### Standalone Query Evaluation
#####


def evaluate_standalone_query_demo(
    demo: dm.QueryDemo,
    context: DemoExecutionContext,
    extra_objects: dict[str, object],
) -> fb.QueryDemoFeedback:
    feedback = fb.QueryDemoFeedback("query", [], [])
    try:
        loader = ObjectLoader(context, extra_objects)
        query = loader.load_query(demo.query, demo.args)
    except Exception as e:
        msg = f"Failed to instantiate query:\n{e}"
        feedback.diagnostics.append(("error", msg))
        return feedback
    # We just check that all the answers parse
    for i, a in enumerate(demo.answers):
        try:
            elt = query.parse_answer(dm.translate_answer(a))
            if isinstance(elt, dp.ParseError):
                diag = ("error", f"Parse error: {str(elt)}")
                feedback.answer_diagnostics.append((i, diag))
        except Exception as e:
            diag = ("error", f"Internal parser error: {str(e)}")
            feedback.answer_diagnostics.append((i, diag))
    return feedback


#####
##### Main EntryPoint
#####


def evaluate_demo(
    demo: dm.Demo,
    context: DemoExecutionContext,
    extra_objects: dict[str, object],
) -> fb.DemoFeedback:
    if isinstance(demo, dm.StrategyDemo):
        feedback, _ = evaluate_strategy_demo_and_return_trace(
            demo, context, extra_objects
        )
        return feedback
    else:
        return evaluate_standalone_query_demo(demo, context, extra_objects)
