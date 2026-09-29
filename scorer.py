"""
A scorer for the project.

This module contains the judge function, which is used to score the project.
It takes in a question, expects, answer, and results, and returns a boolean
indicating whether the answer is correct.
"""

def judge(question: str, expects: str, answer: str, results) -> bool:
  if not expects:
    return False
  return expects.strip().lower() in (answer or "".lower)