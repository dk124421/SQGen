from django.test import TestCase
from SQGen.views import parse_mcq_ai_output

class MCQParsingTestCase(TestCase):
    def test_parse_mcq_ai_output_standard(self):
        ai_output = """
Q1. What does SQL stand for?
A) Structured Query Language
B) Simple Query Logic
C) Sequential Question List
D) Server Quality Level
Correct Answer: A
Explanation: SQL stands for Structured Query Language.

Q2. What is a primary key?
A) A key to open database
B) Unique identifier for a record
C) Public key
D) None of the above
Correct Answer: B
Explanation: Primary key uniquely identifies each record in a table.
"""
        mcqs = parse_mcq_ai_output(ai_output)
        self.assertEqual(len(mcqs), 2)
        self.assertEqual(mcqs[0]['question'], 'Q1. What does SQL stand for?')
        self.assertEqual(mcqs[0]['options']['A'], 'Structured Query Language')
        self.assertEqual(mcqs[0]['answer'], 'A')
        self.assertEqual(mcqs[0]['explanation'], 'SQL stands for Structured Query Language.')

    def test_parse_mcq_ai_output_irregular_format(self):
        ai_output = """
1. What is 2 + 2?
A. 3
B. 4
C. 5
D. 6
Answer - B
Explanation - 2 plus 2 equals 4.
"""
        mcqs = parse_mcq_ai_output(ai_output)
        self.assertEqual(len(mcqs), 1)
        self.assertEqual(mcqs[0]['answer'], 'B')
        self.assertEqual(mcqs[0]['options']['B'], '4')

