"""
Delphyne Demonstrations.

A demo file can be directly parsed as a value of type `DemoFile`. Thus,
field names are optimized to make for a pleasant YAML syntax.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from delphyne.core import refs
from delphyne.core.refs import Hint, SpaceRef

type TestCommandString = str
"""
A non-parsed test command (`TestCommand`).
"""


@dataclass
class ToolCall:
    """
    A tool call, as a part of a query answer.

    Attributes:
        tool: The name of the tool to call.
        args: The arguments to pass to the tool.
    """

    tool: str
    args: dict[str, Any]


@dataclass
class Answer:
    """
    A query answer.

    Attributes:
        answer: the answer content, which can be a string or a
           structured JSON object. When a string is provided, the
           `structured` field is used to desambiguate whether or not the
           content should be interpreted as structured data.
        call: a sequence of tool calls. mode: the answer mode (`None` by
            default), which determines in particular how the answer must
            be parsed.
        label: an optional label for the answer, which can be referenced
            in demonstration tests.
        example: a boolean value indicating whether the answer should be
            usable as a few-shot exmple (some answers are only used s
            negative examples or to describe alternative paths in the
            strategy tree and thus should not be used as examples).
        tags: a sequence of example tags that can be used by policies to
            select appropriate examples.
        justification: an optional justification for the answer (see
            [`delphyne.core.refs.Answer`][]).
    """

    answer: str | object
    call: Sequence[ToolCall] = ()
    structured: Literal["auto", True] = "auto"
    mode: str | None = None
    label: str | None = None
    example: bool | None = None
    tags: Sequence[str] = ()
    justification: str | None = None


@dataclass
class QueryDemo:
    """
    A query demonstration.

    A query demonstration describes a query and associates answers to
    it. It can stand alone in a demonstration file, or be part of a
    strategy demonstration.

    Attributes:
        query: the query name.
        args: the query arguments.
        answers: a sequence of quer answers.
        demonstration: for standalone query demonstrations, an optional
            demonstration label (usully specified first in YAML syntax).
    """

    query: str
    args: dict[str, Any]
    answers: list[Answer]
    demonstration: str | None = None  # optional label


@dataclass
class StrategyDemo:
    """
    A strategy demonstration.

    For a given strategy instance, a strategy demonstration gathers a
    sequence of relevant query demonstrations, along with a sequence of
    unit tests that combine them into coherent scenarios of navigating
    the strategy tree.

    Attributes:
        strategy: the name of the strategy function.
        args: arguments to pass to the strategy function.
        tests: a sequence of unit tests that describe navigation
            scenarios in the strategy tree.
        queries: a sequence of query demonstrations. Featured answers
            are used when executing the tests.
        demonstration: an optional label for the demonstration (usually
            specified first in YAML syntax)
    """

    strategy: str
    args: dict[str, Any]
    tests: list[TestCommandString]
    queries: list[QueryDemo]
    demonstration: str | None = None  # optional label


type Demo = QueryDemo | StrategyDemo
"""
A demonstration is either a standalone query demonstration or a strategy
demonstration.
"""


type DemoFile = list[Demo]
"""
A demonstration file is a sequence of demonstrations. Demonstrations are
independent and can thus be separately evaluted.
"""


#####
##### Describing Test Commands
#####


type NodeSelector = TagSelectors | WithinSpace
"""
Describes a node as a path of tags from the current tree.

A node selector either denotes a node that matches a series of tags in
the surrounding tree (`TagSelectors`), or a node within nested tree,
which induces a space that is itself described by a series of tags
(`WithinSpace`).
"""


type TagSelectors = Sequence[TagSelector]
"""
A series of tag selectors that must **all** be matched.

Tag selectors apply to either nodes or spaces.
"""


@dataclass(frozen=True)
class TagSelector:
    """
    A tag selector consists in a tag along with an optional occurence
    number.

    Attributes:
        tag: the tag to match.
        num: an optional occurence number. When equal to integer `n`,
            the selector does not match the first occurence of the tag
            (along the walked path) but the `n`-th occurence instead.
    """

    tag: str
    num: int | None


@dataclass
class WithinSpace:
    """
    A node selector that matches a node within a particular space of the
    surrounding tree.

    Attributes:
        space: a conjunction of tags describing a space in the
            surrounding tree.
        selector: a node selector, relative to the tree that induces the
           aforementioned space.
    """

    space: TagSelectors
    selector: NodeSelector


@dataclass
class Run:
    """
    Walk through the tree, using local node navigation functions along
    with the content of the demonstration's `query` section to answer
    queries.

    Depending on whether `until` is provided, this corresponds to either
    the "run" or "at" instruction in concrete syntax.

    Attributed:
        hints: Whenever a query must be answered, the first answer
            provided in the `query` section is used, unless an answer
            whose label matches the first remaining hint exists, in
            which case it is used insted and the hint is consumed. This
            mechanism allows concisely describing alternative paths in
            the tree that only differ from the default path in a small
            number of key decisions.
        until: When provided, the walk stops when the current node
            matches the provided description (see `NodeSelector`).
    """

    hints: Sequence[Hint]
    until: NodeSelector | None


@dataclass
class SelectSpace:
    """
    Select a particular local space of the current node, using a
    hint-based reference.

    Depending on the value of `expects_query`, this corresponds to
    either the "go" or the "answer" instruction in concrete syntax.

    Attributes:
        space: Local, hint-based reference for the space to select.
        expects_query: Whether the space is expected to be induced by a
            query. When true, the current node position is left
            unchanged and the instruction fails if the selected space is
            not induced by a query or if this query is not answered.
            When set to false, the current node position is updated to
            the root of the tree inducing the selected space (the
            instruction fails if this space is induced by a query).
    """

    space: SpaceRef
    expects_query: bool


@dataclass
class IsSuccess:
    """
    Do not move but fail if the current node is *not* a success leaf.
    """

    pass


@dataclass
class IsFailure:
    """
    Do not move but fail if the current node is *not* a failure node
    (i.e., a leaf node that is not a success leaf).
    """

    pass


@dataclass
class Save:
    """
    Save the current node under a given name.
    """

    name: str


@dataclass
class Load:
    """
    Go to a tree node that was previously saved under a given name.
    """

    name: str


type TestStep = Run | SelectSpace | IsSuccess | IsFailure | Save | Load
"""
A test instruction.

Each instruction updates the current node position in the strategy tree.
In addition, instructions can error or get stuck.
"""


type TestCommand = Sequence[TestStep]
"""
A test command is a sequence of test instructions.

It describes a path in the strategy tree, starting from the root and
reaching a destination node. A test can succeed, error or be stuck
(i.e., reach a node where it cannot make further progress due to a
missing answer in the `queries` section). It can also emit various
warnings (i.e., a hint was not used).
"""


def translate_answer(ans: Answer) -> refs.Answer:
    if isinstance(ans.answer, str) and ans.structured == "auto":
        content = ans.answer
    else:
        content = refs.Structured(ans.answer)
    tool_calls = tuple([refs.ToolCall(c.tool, c.args) for c in ans.call])
    return refs.Answer(ans.mode, content, tool_calls, ans.justification)
