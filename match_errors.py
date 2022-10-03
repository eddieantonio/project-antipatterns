from __future__ import annotations

"""
Match error message templates.
"""

import csv
import re
from collections import Counter
from dataclasses import dataclass

from simple_error_messages import SIMPLE_ERROR_MESSAGES


@dataclass(frozen=True)
class MessagePattern:
    message_id: str
    pattern: re.Pattern
    signature: str

    def match(self, message: str) -> bool:
        return bool(self.pattern.match(message))

    @staticmethod
    def match_all(message: str) -> MessagePattern | None:
        for pattern in PATTERNS:
            if pattern.match(message):
                return pattern
        return None


# Big list of error message regular expressions 🙃
PATTERNS = [
    MessagePattern(
        message_id="compiler.err.does.not.override.abstract",
        pattern=re.compile(
            r"(?P<child_class_name>\S+)"
            r" is not abstract and does not override abstract method "
            r"(?P<method_name>\S+) in (?P<parent_class_name>\S+)$"
        ),
        signature="Mallard is not abstract and does not override abstract method quack(java.io.OutputStream) in Duck",
    ),
    MessagePattern(
        message_id="compiler.err.array.req.but.found",
        pattern=re.compile(
            r"array required, but (?P<type_name>\S+) found$",
        ),
        signature="array required, but java.lang.String found",
    ),
    MessagePattern(
        message_id="compiler.err.operator.cant.be.applied.1",
        pattern=re.compile(
            r"bad operand types for binary operator '[^']+'",
        ),
        signature=(
            "bad operand types for binary operator '+'\n"
            "  first type:  int\n"
            "  second type: boolean"
        ),
    ),
    MessagePattern(
        message_id="compiler.err.cant.access",
        pattern=re.compile(
            r"cannot access (?P<class_name>\S+)",
        ),
        signature=(
            "cannot access ducks.Mallard\n"
            "bad class file: ducks/Mallard.class(ducks:Mallard.class)\n"
            "class file has wrong version 52.0, should be 50.0\n"
            "Please remove or make sure it appears in the correct subdirectory of the classpath."
        ),
    ),
    MessagePattern(
        message_id="compiler.err.cant.assign.val.to.final.var",
        pattern=re.compile(
            r"cannot assign a value to final variable (?P<variable_name>\S+)$"
        ),
        signature="cannot assign a value to final variable NUMBER_OF_QUACKS",
    ),
    # For compiler.err.cant.resolve, although it can cover different kinds of symbols
    # (e.g., variables, methods, class names, etc), we'll just create
    # multiple signatures to match existing literature.
    MessagePattern(
        message_id="compiler.err.cant.resolve[class]",
        pattern=re.compile(r"cannot find symbol -   class (?P<class_name>\S+)"),
        signature="cannot find symbol -   class Dcuk",
    ),
    MessagePattern(
        message_id="compiler.err.cant.resolve[method]",
        pattern=re.compile(r"cannot find symbol -   method (?P<method_signature>\S+)"),
        signature="cannot find symbol -   method quackk(java.io.OutputStream)",
    ),
    MessagePattern(
        message_id="compiler.err.cant.resolve[variable]",
        pattern=re.compile(r"cannot find symbol -   variable (?P<variable_name>\S+)"),
        signature="cannot find symbol -   variable scroogeMcduck",
    ),
    MessagePattern(
        message_id="compiler.err.class.public.should.be.in.file",
        # kind can be class, enum, or interface, maybe something else.
        pattern=re.compile(
            r"(?P<kind>\S+) (?P<class_name>\S+)"
            r" is public, should be declared in a file named "
            r"(?P<name>\S+).java$"
        ),
        signature="class Mallard is public, should be declared in a file named Mallard.java",
    ),
    # TODO: oh dear... I might need to make this one less generic....
    # TODO: the "reason" message segment is quite annoying...
    MessagePattern(
        message_id="compiler.err.cant.apply.symbol",
        # kind can be class, enum, or interface, maybe something else.
        pattern=re.compile(
            r"(?P<kind1>\S+) "
            r"(?P<name>\S+)"
            r" in "
            r"(?P<kind2>\S+) "
            r"(?P<type>\S+)"
            r" cannot be applied to given types;\n"
        ),
        signature=(
            "constructor Mallard in class Mallard cannot be applied to given types;\n"
            "  required: no arguments\n"
            "  found: int\n"
            "  reason: actual and formal argument lists differ in length"
        ),
    ),
    MessagePattern(
        message_id="compiler.err.duplicate.class",
        pattern=re.compile(r"duplicate class: (?P<name>\S+)$"),
        signature="duplicate class: Duck",
    ),
    MessagePattern(
        message_id="compiler.err.class.cant.write",
        pattern=re.compile(r"error while writing (?P<symbol>\S+:)"),
        signature="error while writing Duck: C:\Program Files (x86)\BlueJ\examples\duck\Duck.class (Access is denied)",
    ),
    MessagePattern(
        message_id="compiler.err.illegal.char",
        pattern=re.compile(r"illegal character: "),
        signature="illegal character: '#'",
    ),
    # This one is too generic for my liking because "message segment" can be nearly
    # anything including "missing return value", "unexpected return value"
    MessagePattern(
        message_id="compiler.err.prob.found.req",
        pattern=re.compile(r"incompatible types: "),
        signature="incompatible types: double cannot be converted to java.lang.Integer",
    ),
    MessagePattern(
        message_id="compiler.err.cant.deref",
        pattern=re.compile(r"(?P<type>\S+) cannot be dereferenced"),
        signature="int cannot be dereferenced",
    ),
    # TODO: check how generic this one is
    MessagePattern(
        message_id="compiler.err.already.defined[method]",
        pattern=re.compile(
            r"method (?P<method_name>\S+)"
            " is already defined in "
            "(?P<kind2>\S+) (?P<type_name>\S+)"
        ),
        signature="method quack(java.io.OutputStream) is already defined in class Mallard",
    ),
    MessagePattern(
        message_id="compiler.err.already.defined[variable]",
        pattern=re.compile(
            r"variable (?P<variable_name>\S+)"
            " is already defined in "
            "(?P<kind2>\S+) (?P<symbol>\S+)"
        ),
        signature="variable i is already defined in method quack(java.io.OutputStream)",
    ),
    MessagePattern(
        message_id="compiler.err.anonymous.diamond.method.does.not.override.superclass",
        pattern=re.compile(
            r"method does not override or implement a method from a supertype"
        ),
        signature="method does not override or implement a method from a supertype",
    ),
    MessagePattern(
        message_id="compiler.err.modifier.not.allowed.here",
        pattern=re.compile(r"modifier (?P<name>\S+) not allowed here"),
        signature="modifier abstract not allowed here",
    ),
    # TODO: overly generic:
    MessagePattern(
        message_id="compiler.err.cant.apply.symbols",
        pattern=re.compile(r"no suitable (?P<symbol_kind>\S+) found for (?P<name>\S+)"),
        signature="no suitable constructor found for FileOutputStream()",
    ),
    # TODO: overly generic with symbol kind?
    MessagePattern(
        message_id="compiler.err.non-static.cant.be.ref",
        pattern=re.compile(
            r"non-static (?P<symbol_kind>\S+) (?P<symbol>\S+) cannot be referenced from a static context"
        ),
        signature="non-static method quack() cannot be referenced from a static context",
    ),
    MessagePattern(
        message_id="compiler.err.doesnt.exist",
        pattern=re.compile("package (?P<symbol>\S+) does not exist"),
        signature="package DUck does not exist",
    ),
    MessagePattern(
        message_id="compiler.err.unreported.exception.need.to.catch.or.throw",
        pattern=re.compile(
            r"unreported exception (?P<type>\S+); must be caught or declared to be thrown"
        ),
        signature=(
            "unreported exception java.io.FileNotFoundException; must be caught or declared to be thrown"
        ),
    ),
    MessagePattern(
        message_id="compiler.err.var.might.not.have.been.initialized",
        pattern=re.compile(
            r"variable (?P<symbol>\S+) might not have been initialized$"
        ),
        signature=("variable NUMBER_OF_QUACKS might not have been initialized"),
    ),
    MessagePattern(
        message_id="compiler.err.var.might.already.be.assigned",
        pattern=re.compile(
            "variable (?P<symbol>\S+) might already have been assigned$"
        ),
        signature=("variable NUMBER_OF_QUACKS might already have been assigned"),
    ),
]


if __name__ == "__main__":
    # Quick and dirty checks that my regular expressions are all matched,
    # and that the signatures can be matched by the regular expression.

    unmatched_messages = 0
    total_messages = 0
    patterns_matched: Counter[MessagePattern] = Counter()
    simple_errors_matched = 0

    with open("./grouped-errors.csv", encoding="UTF-8", newline="") as error_file:
        reader = csv.reader(error_file, delimiter=",", quotechar='"')
        for (message,) in reader:
            if pat := MessagePattern.match_all(message):
                patterns_matched[pat] += 1
            elif message in SIMPLE_ERROR_MESSAGES:
                simple_errors_matched += 1
            else:
                unmatched_messages += 1
            total_messages += 1

    # Check that all of the patterns matched at least once:
    for pat in PATTERNS:
        assert pat.match(pat.signature), f"{pat.message_id} did not match own signature"
        assert pat in patterns_matched, f"pattern never matched"

    print("== Summary ==")
    for pat, count in patterns_matched.most_common():
        print(f"\x1b[1m{count:3d}\x1b[m: \x1b[33m{pat.signature}\x1b[m")
    print(f"\x1b[1m{unmatched_messages}\x1b[m/{total_messages} message unmatched")
    print(f"({simple_errors_matched} simple errors)")
