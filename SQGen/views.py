import sys
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from PaperGenerator.models import PaperGenerator
from MCQTest.models import MCQTest
from openai import OpenAI, APIError
from io import BytesIO
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas



# Create your views here.
def paper(request):
    paper_content = None
    msg = None
    prompt = None 
    if request.method == "POST":
        exam_type = request.POST.get("exam_type")
        subject = request.POST.get("subject")
        syllabus = request.POST.get("syllabus")  # New syllabus input
        difficulty = request.POST.get("difficulty")
        paper = PaperGenerator(exam_type=exam_type, subject=subject, difficulty=difficulty)
        # paper.save()
        
        syllabus_text = ""
        if syllabus:
            syllabus_text = "According to the syllabus"
        msg = f"Generated {exam_type} paper for {subject} at {difficulty} difficulty {syllabus_text}."

        if exam_type.upper() == "FINAL EXAM":
            prompt = f'''
Generate a university-level question paper using the following parameters:

SUBJECT: {subject}
DIFFICULTY LEVEL: {difficulty}
SYLLABUS (Optional): {syllabus}

If the syllabus is provided, strictly generate questions ONLY from the syllabus. 
If syllabus is NOT provided, generate based on the subject’s standard university curriculum.

GENERAL RULES FOR ALL PAPERS:
1. Follow the exact structure and marking scheme depending on MIDTERM or FINAL.
2. Maintain academic exam tone — no extra explanations, no introduction, no summary.
3. Questions must be clear, unique, and cover complete syllabus breadth.
4. Use both theory and practical questions.
5. Create subject-appropriate question styles:
   - DBMS → SQL queries, schema diagrams, relational algebra, table-based data.
   - ML → numerical problems, datasets, confusion matrix, algorithm steps.
   - TOC → automata diagrams, grammar conversions, DFA/NFA tables.
   - DSA → dry-run, tree/graph diagrams, complexity table.
   - OS → CPU scheduling tables, memory allocation diagrams.
   - CN → subnetting tables, packet diagrams.
   - Java/Web Dev → code-based, debugging, output prediction.
6. **Include diagrams, pseudo code, flowcharts, tables, datasets when required.**
7. Tables must be aligned properly.
8. Difficulty must reflect as:
   - EASY → conceptual, definitions, direct questions
   - MEDIUM → application, case-based, moderate reasoning
   - HARD → deep reasoning, multi-step, numerical and logical problems

Generate a FINAL Semester Question Paper in the following exact structure:

------------------------------------------
FINAL SEMESTER EXAM QUESTION PAPER
SUBJECT: {subject}
DIFFICULTY: {difficulty}
------------------------------------------

PART – A (5 × 1 = 5 Marks)
Compulsory Short Questions:
• 5 questions
• Concept recall + basic definitions + introductory reasoning
• No long explanations

PART – B (5 × 5 = 25 Marks)
Analytical / Long Answer Questions:
• 5 questions
• Include deep explanation, derivations, diagrams, algorithms, pseudo code if required
• For subjects like DBMS/ML/OS/TOC/DSA – include numerical problems or dataset-based questions

PART – C (4 × 10 = 40 Marks)
Compulsory Advanced Problem-Solving:
• 4 full-length questions
• Include:
  - numerical problems
  - dataset / table-based questions
  - case studies
  - algorithm implementation
  - code writing or debugging
  - multi-part reasoning
• One of the questions can include an OR option

GENERAL NOTES FOR FINAL:
• At least 1 question must include a TABLE (if subject fits)
• At least 1 must involve a DIAGRAM (tree, flowchart, automata, ER diagram, scheduling chart)
• At least 1 should require PRACTICAL/NUMERICAL solution
• Avoid repetition

No additional notes, no explanations — Only the question paper.


''' 
        else:
            prompt = f''''
Generate a university-level question paper using the following parameters:

SUBJECT: {subject}
DIFFICULTY LEVEL: {difficulty}
SYLLABUS (Optional): {syllabus}

If the syllabus is provided, strictly generate questions ONLY from the syllabus. 
If syllabus is NOT provided, generate based on the subject’s standard university curriculum.

GENERAL RULES FOR ALL PAPERS:
1. Follow the exact structure and marking scheme depending on MIDTERM or FINAL.
2. Maintain academic exam tone — no extra explanations, no introduction, no summary.
3. Questions must be clear, unique, and cover complete syllabus breadth.
4. Use both theory and practical questions.
5. Create subject-appropriate question styles:
   - DBMS → SQL queries, schema diagrams, relational algebra, table-based data.
   - ML → numerical problems, datasets, confusion matrix, algorithm steps.
   - TOC → automata diagrams, grammar conversions, DFA/NFA tables.
   - DSA → dry-run, tree/graph diagrams, complexity table.
   - OS → CPU scheduling tables, memory allocation diagrams.
   - CN → subnetting tables, packet diagrams.
   - Java/Web Dev → code-based, debugging, output prediction.
6. **Include diagrams, pseudo code, flowcharts, tables, datasets when required.**
7. Tables must be aligned properly.
8. Difficulty must reflect as:
   - EASY → conceptual, definitions, direct questions
   - MEDIUM → application, case-based, moderate reasoning
   - HARD → deep reasoning, multi-step, numerical and logical problems


Generate a MIDTERM (Internal Assessment) Question Paper in the following exact structure:

------------------------------------------
MIDTERM EXAM QUESTION PAPER
SUBJECT: {subject}
DIFFICULTY: {difficulty}
------------------------------------------

PART – A (5 × 1 = 5 Marks)
Short Answer Questions:
• 5 questions of 1 mark each
• Definitions, direct concepts, short reasoning

PART – B (5 × 3 = 15 Marks)
Moderate Analytical Questions:
• 5 questions
• Include diagrams/flowcharts only when required
• Must reflect the difficulty level
• Balance of conceptual + light practical
• Questions length: 2 - 4 lines


PART – C (2 × 5 = 10 Marks)
Problem-Solving / Practical:
• 2 questions
• Can include:
  - small dataset or table
  - short numerical problem
  - algorithm step tracing
  - program output or bug-fixing
• No overly long theory (short-medium practical)

GENERAL NOTES FOR MIDTERM:
• Include at least ONE table/diagram IF relevant to subject.
• Must be shorter and lighter than Final Exam.

'''
    
        if prompt:
            
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )

            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct:free",

                messages=[
                    {"role": "user", "content": prompt}
                    
                ]
            )
            paper_content = response.choices[0].message.content
            
            solution_prompt = f'''
You are an expert university examiner.  
Generate a COMPLETE, HIGH-QUALITY SOLUTION PAPER for the following question paper:

=====================================
      QUESTION PAPER  
=====================================
{paper_content}
=====================================
       SOLUTION RULES  
=====================================

1) PROVIDE SOLUTIONS FOR EVERY QUESTION  
Do not skip ANY question, sub-question, or numerical part.

2) FOLLOW THE SAME STRUCTURE AS THE QUESTION PAPER  
Use identical numbering:
PART A → Q1, Q2, Q3 …  
PART B → Q6, Q7 …  
PART C → Q11, Q12 …

3) SOLUTION FORMAT REQUIREMENTS

------------------------------------------
A) SHORT ANSWER SOLUTIONS (PART A)
------------------------------------------
• 3–6 lines per question  
• Clear definitions  
• One example (if relevant)  
• No unnecessary depth  

------------------------------------------
B) LONG ANSWER SOLUTIONS (PART B)
------------------------------------------
• Detailed explanation  
• Step-by-step logic  
• Diagrams if needed  
• Algorithms in pseudocode or code  
• Real examples where applicable  

------------------------------------------
C) PROBLEM-SOLVING SOLUTIONS (PART C)
------------------------------------------
Solve according to question type:

------------------------------------------
1. NUMERICAL PROBLEMS
------------------------------------------
• Formula first  
• Substitute values  
• Step-by-step calculations  
• Final answer clearly highlighted:

Final Answer: **value**

------------------------------------------
2. CODING QUESTIONS
------------------------------------------
Use clean code blocks, correct syntax, and comments:

Example (Python)
def add(a, b):
return a + b

markdown
Copy code

Include:
• Output example  
• Explanation of code logic  

------------------------------------------
3. DIAGRAM-BASED QUESTIONS
------------------------------------------
Use clean ASCII diagrams where required:

  (q0) --a--> (q1)
     \        /
      b      a
       \    /
        (q2)

mathematica
  Root
 /   \
A     B

------------------------------------------
4. TABLE-BASED SOLUTIONS
------------------------------------------
Provide clean tables if the answer requires structured data:

| Field | Description |
|-------|-------------|
| ID    | Unique key  |

or dataset examples:

| ID | Age | Score |
|----|-----|--------|
| 1  | 21  | 89     |

------------------------------------------
5. PRACTICAL / APPLICATION QUESTIONS
------------------------------------------
For ML, AI, DBMS, DSA, WEB, OS etc:
• Provide practical logic  
• Algorithms  
• SQL queries  
• Small datasets  
• Flowcharts  
• Model architectures  
Only where needed — NOT for every question.

------------------------------------------
6. SUBJECT-WISE REQUIREMENT HANDLING
------------------------------------------
• ML / AI → more practical, dataset-driven, algorithm steps  
• DBMS → SQL queries + ER diagrams  
• DSA → tree/graph diagrams  
• TOC → DFA/NFA diagrams, grammar derivations  
• Java/WebDev → code + output  
• CN/OS → tables, buffer calculations, diagrams  

------------------------------------------
7. LANGUAGE QUALITY
------------------------------------------
• Academic tone  
• Clear structuring  
• No unnecessary repetition  
• No additional commentary outside solutions  

=====================================
END OF SOLUTION PAPER REQUIREMENTS
=====================================

Now generate the complete SOLUTION PAPER.
'''
            solution_response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "user", "content": solution_prompt}
                ]
            )
            solution_content = solution_response.choices[0].message.content
            paper_content += solution_content
            if paper_content:
                # ---------- PDF GENERATION (Send to browser) ----------
                buffer = BytesIO()
                pdf = canvas.Canvas(buffer)
                pdf.setFont("Helvetica", 12)

                y = 800
                left_margin = 40
                right_margin = 40
                page_width = pdf._pagesize[0]
                available_width = page_width - left_margin - right_margin
                line_height = 15

                for line in paper_content.split("\n"):
                    stripped_line = line.strip()

                    # Header detection
                    if stripped_line.startswith("**") and stripped_line.endswith("**"):
                        pdf.setFont("Helvetica-Bold", 14)
                        content = stripped_line.replace("*", "")
                        pdf.drawString(left_margin, y, content)
                        pdf.setFont("Helvetica", 12)
                        y -= line_height * 1.5
                    else:
                        cleaned_line = line.replace("*", "")
                        wrapped_lines = simpleSplit(cleaned_line, "Helvetica", 12, available_width)

                        if not wrapped_lines:
                            wrapped_lines.append('')

                        for segment in wrapped_lines:
                            pdf.drawString(left_margin, y, segment)
                            y -= line_height
                            if y < 40:
                                pdf.showPage()
                                pdf.setFont("Helvetica", 12)
                                y = 800

                pdf.save()
                buffer.seek(0)

                # ---- Send PDF to browser and display in browser (not save to server) ----
                
                response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="paper.pdf"'
                response['X-Frame-Options'] = 'ALLOWALL'
                return response
                
    return render(request, "paper_generator.html", {"msg": msg})

def mcq(request):
    mcqs = None
    msg = None
    prompt = None
    if request.method == "POST":
        topic = request.POST.get("topic")
        num_questions = request.POST.get("num_questions")
        difficulty = request.POST.get("difficulty")
        mcq = MCQTest(topic=topic, num_questions=num_questions, difficulty=difficulty)
        # mcq.save() 
        
        msg = f''' Generated {num_questions} MCQ questions on the topic "{topic}" with {difficulty} difficulty. '''
        prompt = f'''Generate high-quality Multiple Choice Questions (MCQs) based on the following topic/content:

Topic: **{topic}**

Requirements:
1. Create **{num_questions} MCQs**.
2. Difficulty level: **{difficulty}**
3. Each question must be:
   - Clear and conceptual
   - Non-repetitive
   - Exam-oriented
   - Based strictly on the topic
4. Provide options labeled A, B, C, and D.
5. Clearly mention:
   - Correct Answer (Just the letter, e.g., "Correct Answer: B")
   - Short Explanation (1–2 lines)
6. Format strictly as:

Q1. <question text>
A) option
B) option
C) option
D) option
Correct Answer: <letter>
Explanation: <short explanation>

Q2. ...
(continue in same format)

Do NOT include extra text, introduction, or summary.
'''    
        if prompt:
            
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )

            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
                
            mcqs = []
            blocks = response.choices[0].message.content.strip().split("Q")[1:]
            for i, block in enumerate(blocks):
                lines = block.strip().split("\n")
                if len(lines) < 7: continue # Skip malformed blocks

                question = f"Q{i+1}. {lines[0][3:]}"
                options = {
                    "A": lines[1][3:],
                    "B": lines[2][3:],
                    "C": lines[3][3:],
                    "D": lines[4][3:]
                }
                # Fix: Strip potential extra spaces from the answer and explanation
                answer = lines[5].split(":")[1].strip()
                explanation = lines[6].split(":",1)[1].strip()

                mcqs.append({
                    "question": question,
                    "options": options,
                        "answer": answer,
                    "explanation": explanation
                })
    return render(request, "mcq_test.html", {"msg": msg, "mcq_questions": mcqs})