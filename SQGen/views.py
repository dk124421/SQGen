from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from io import BytesIO
from openai import OpenAI
import re

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table,Image,
    TableStyle, Spacer, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

from PaperGenerator.models import PaperGenerator
from MCQTest.models import MCQTest
from utils.diagram_generator import generate_dfa_diagram

# ---------- HELPERS ----------
def extract_table(lines, start):
    table = []
    i = start

    while i < len(lines):
        line = lines[i].strip()

        # Stop if not a table row
        if not line.startswith("|") or line.count("|") < 2:
            break

        # Extract cells safely
        cells = [c.strip() for c in line.split("|")[1:-1]]

        # Skip separator rows like |----|----|
        if all(set(c) <= {"-"} for c in cells):
            i += 1
            continue

        # Skip empty rows
        if not any(cells):
            i += 1
            continue

        table.append(cells)
        i += 1

    return table, i



def extract_code_block(lines, start):
    code = []
    i = start + 1
    while i < len(lines) and not lines[i].startswith("```"):
        code.append(lines[i])
        i += 1
    return "\n".join(code), i + 1

def is_table_row(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def extract_table(lines, start):
    table_data = []
    i = start

    # Read table rows
    while i < len(lines) and is_table_row(lines[i]):
        row = [c.strip() for c in lines[i].strip().split("|")[1:-1]]
        table_data.append(row)
        i += 1

    # Validate column consistency
    col_count = len(table_data[0])
    for row in table_data:
        if len(row) != col_count:
            return None, start + 1

    return table_data, i

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
Include diagrams, tables, pseudocode, datasets ONLY when required.
ALL diagrams must be ASCII (no images).
ALL tables must be pipe-formatted.

SUBJECT-SPECIFIC RULES
--------------------------------------------------
• DBMS → SQL queries, ER diagrams (ASCII), tables
• ML/AI → datasets, confusion matrix, numerical problems
• TOC → DFA/NFA ASCII diagrams, grammar conversion
• DSA → tree/graph ASCII diagrams, dry-run
• OS → CPU scheduling tables, memory diagrams
• CN → subnetting tables, packet flow
• Java/Web → code writing, debugging, output-based
No additional notes, no explanations — Only the question paper.


''' 
        else:
            prompt = f'''
You are an expert university examiner.

Generate a UNIVERSITY-LEVEL MIDTERM (INTERNAL) QUESTION PAPER using the following parameters:

SUBJECT: {subject}
DIFFICULTY LEVEL: {difficulty}
SYLLABUS (Optional): {syllabus}

--------------------------------------------------
SYLLABUS HANDLING RULE
--------------------------------------------------
• If syllabus is PROVIDED → generate questions STRICTLY from it.
• If syllabus is NOT provided → follow standard university curriculum.

--------------------------------------------------
GENERAL RULES
--------------------------------------------------
1. Maintain academic exam tone.
2. NO introduction, NO explanation, NO summary.
3. Questions must be concise and syllabus-aligned.
4. Include light practical questions.
5. Diagrams/tables ONLY when required.
6. ASCII diagrams only.
7. Pipe-format tables only.

==================================================
MIDTERM EXAM STRUCTURE
==================================================

------------------------------------------
MIDTERM EXAM QUESTION PAPER
SUBJECT: {subject}
DIFFICULTY: {difficulty}
------------------------------------------

PART – A (5 × 1 = 5 Marks)
• Short answer questions
• Definitions, basic concepts

PART – B (5 × 3 = 15 Marks)
• Moderate analytical questions
• 2–4 line answers
• Diagrams only if required

PART – C (2 × 5 = 10 Marks)
• Practical / problem-solving questions
• Small numericals, tables, algorithm tracing

MIDTERM CONSTRAINTS:
• Easier and shorter than final exam
• At least ONE diagram OR table if relevant

--------------------------------------------------
IMPORTANT:
Return ONLY the QUESTION PAPER.


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
            
            if not response or not response.choices:
                return HttpResponse("AI response failed. Try again.")

            
            solution_prompt = f'''
You are an expert university examiner.  
Generate a COMPLETE, HIGH-QUALITY SOLUTION PAPER for the following question paper:

==============================================================================
      QUESTION PAPER  
==============================================================================
{paper_content}\n
\n\n\n
==============================================================================
       SOLUTION RULES  
==============================================================================


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
If a DFA/NFA or graph diagram is required, use this EXACT format:

[DIAGRAM]
Type: DFA
States: q0, q1, q2
Transitions:
q0 0 q0
q0 1 q1
q1 1 q2
Final: q2

For other diagrams, use ASCII.

mathematica
  Root
 /   \
A     B

------------------------------------------
4. TABLE RULES (VERY IMPORTANT):
• Every table must use PIPE format
• NO dashed-only rows
• Each row must contain real values
• Do NOT include empty columns
• Example:

| ID | Age | Score |
| 1  | 21  | 89    |
| 2  | 22  | 91    |


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

8. question solution numbering must EXACTLY MATCH the question paper.

9 or question includes an OR option, provide solutions for BOTH options. with same question number.

=====================================
END OF SOLUTION PAPER REQUIREMENTS
=====================================
IMPORTANT:
Return ONLY the SOLUTION PAPER with que number.
Now generate the complete SOLUTION PAPER.
'''
            solution_response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "user", "content": solution_prompt}
                ]
            )
            solution_content = solution_response.choices[0].message.content
            if not response or not response.choices:
                return HttpResponse("AI response failed. Try again.")

            paper_content += solution_content
            if paper_content:
                # ---------- PDF GENERATION (Send to browser) ----------
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    rightMargin=40,
                    leftMargin=40,
                    topMargin=40,
                    bottomMargin=40
                )

                styles = getSampleStyleSheet()

                styles.add(ParagraphStyle(
                    name="CustomBody",
                    fontName="Times-Roman",
                    fontSize=11,
                    leading=15,
                    alignment=TA_LEFT
                ))

                styles.add(ParagraphStyle(
                    name="CustomCode",
                    fontName="Courier",
                    fontSize=9,
                    leading=12,
                    backColor=colors.whitesmoke,
                    leftIndent=6
                ))

                elements = []
                lines = paper_content.split("\n")
                i = 0

                while i < len(lines):
                    line = lines[i].strip()

                    # ---------- TABLE ----------
                    if "|" in line and line.strip().startswith("|"):
                        table_data, i = extract_table(lines, i)

                        # 🚨 CRITICAL SAFETY CHECK
                        if table_data and all(len(row) > 0 for row in table_data):
                            table = Table(table_data)
                            table.setStyle(TableStyle([
                                ('GRID', (0,0), (-1,-1), 1, colors.black),
                                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 12))
                        else:
                            # Fallback to text
                            for row in table_data:
                                elements.append(Paragraph(" | ".join(row), styles["CustomBody"]))
                                elements.append(Spacer(1, 6))

                        continue
                    # ---------- DIAGRAM ----------
                    if line == "[DIAGRAM]":
                        states = []
                        transitions = []
                        finals = []

                        i += 1
                        while i < len(lines) and lines[i].strip():
                            row = lines[i].strip()

                            if row.startswith("States:"):
                                states = [s.strip() for s in row.split(":", 1)[1].split(",")]

                            elif row.startswith("Final:"):
                                finals = [s.strip() for s in row.split(":", 1)[1].split(",")]

                            elif re.match(r"^[a-zA-Z0-9]+\s+[01]\s+[a-zA-Z0-9]+$", row):
                                src, sym, dst = row.split()
                                transitions.append((src, sym, dst))

                            i += 1

                        # Render diagram only if valid
                        if states and transitions:
                            img_path = generate_dfa_diagram(states, transitions, finals)
                            if img_path:
                                elements.append(Image(img_path, width=320, height=160))
                                elements.append(Spacer(1, 14))
                            else:
                                elements.append(Paragraph(
                                    "Diagram could not be rendered. Please refer to the description above.",
                                    styles["CustomBody"]
                                ))
                        continue

                    # ---------- CODE BLOCK ----------
                    if line.startswith("```"):
                        code, i = extract_code_block(lines, i)
                        elements.append(Preformatted(code, styles["CustomCode"]))
                        elements.append(Spacer(1, 12))
                        continue

                    # ---------- NORMAL TEXT ----------
                    if line:
                        clean_line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
                        elements.append(Paragraph(clean_line, styles["CustomBody"]))
                        elements.append(Spacer(1, 8))

                    i += 1

                doc.build(elements)
                buffer.seek(0)

                return HttpResponse(
                    buffer.getvalue(),
                    content_type="application/pdf",
                    headers={"Content-Disposition": "inline; filename=paper.pdf"}
                )


                
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