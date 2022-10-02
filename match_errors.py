from __future__ import annotations

"""
Match error message templates.
"""

import csv
import re
from collections import Counter
from dataclasses import dataclass


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
    # TODO: one for compiler.err.class.cant.write?
    MessagePattern(
        message_id="compiler.err.illegal.char",
        pattern=re.compile(r"illegal character: "),
        signature="illegal character: '#'",
    ),
]


if __name__ == "__main__":
    # quick and dirty check that my regular expressions are all matched,
    # and that the signatures can be matched by the regular expression.
    c: Counter[MessagePattern] = Counter()
    with open("./grouped-errors.csv", encoding="UTF-8", newline="") as error_file:
        reader = csv.reader(error_file, delimiter=",", quotechar='"')
        for (message,) in reader:
            if pat := MessagePattern.match_all(message):
                c[pat] += 1

    for pat in PATTERNS:
        assert pat.match(pat.signature), "pattern did not match own signature"
        assert pat in c, "pattern never matched"

    for pat, count in c.most_common():
        print(count, pat.signature)
