"""
check_grammer.py
"""

from typing import List, Dict
import language_tool_python

# Initialize the language tool instance once
tool = language_tool_python.LanguageTool("en-US")


def check_grammar(text: str) -> List[Dict[str, List[str] | str]]:
    """
    Checks grammar of the given text and returns a list of detected errors.
    """
    return [
        {
            "error": rule.message,
            "suggestions": rule.replacements,
        }
        for rule in tool.check(text)
    ]


print(check_grammar("A sentence with a error."))
