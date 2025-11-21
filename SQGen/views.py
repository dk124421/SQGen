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
            prompt = f''''SYSTEM:
You are an exam paper generator. ALWAYS follow the user’s required structure exactly.
Output only the question paper — no extra text, no notes, no markdown.
If a syllabus is provided, generate questions STRICTLY from it.
If something is NOT in the syllabus, do NOT invent a topic — instead use “[NOT COVERED]”.
If any question needs a diagram, algorithm, or flowchart, include a text placeholder:
“DIAGRAM/ALGO: <describe what should be drawn>”.

USER:
Generate a FINAL Semester University Question Paper using the structure below.

SUBJECT: {subject}
DIFFICULTY: {difficulty}
SYLLABUS (Optional):
{syllabus}

###  GENERAL RULES (VERY IMPORTANT)
1. Detect the subject type automatically:
   • If coding-based subject → include programming questions  
     (Java, Python, Web Development, ML coding, DBMS SQL, OS commands)
   • If math-heavy subject → include proofs, derivations, numerical problems  
     (ToC, Automata, DSA analysis, Discrete math)
   • If real-world/data subjects → include dataset-based questions  
     (ML, AI, Data Mining)
   • If system-level → include architecture diagrams  
     (CN, OS, DBMS)
   • If theory-heavy → include conceptual questions  
     (ToC, AI, Distributed Systems)

2. Only include diagrams when the subject naturally uses them  
   Examples:
   • DSA → Trees, Graphs, Heap  
   • CN → Network layers diagram  
   • DBMS → ER Diagram, Schema diagram  
   • ToC → DFA/NFA, parse trees  
   • ML → Model pipeline diagram  
   • Web Dev → System architecture or flow diagram

3. Dataset-based questions must be included **only for ML / Data Mining / AI**, not for other subjects.

4. Never include explanations or solutions. Only questions.

---

###  QUESTION PAPER FORMAT (STRICT)

PART - A  
Short Questions (5 × 1 = 5 Marks)  
Rules:  
• Must contain 5 short, crisp conceptual questions  
• Limit theory-only definitions  
• Include small examples if needed  
• Subject-dependent (detect automatically)

---

PART - B  
Analytical / Long Questions (5 × 5 = 25 Marks)  
Rules:  
• Mix of conceptual + analytical + applied questions  
• If subject supports coding → include one code-writing question  
• If subject supports diagrams → include exactly one diagram question  
• If subject supports math → include one problem-solving or derivation question  
• If subject is ML/data → include one dataset-based scenario  
• Questions must be clear, structured, and academic

---

PART - C  
Compulsory Problem-Solving / Programming Section (4 × 10 = 40 Marks)  
Rules:  
• Choose question type based on subject:
   - ML/AI → coding, dataset workflows, model evaluation  
   - DBMS → SQL queries, relational algebra, transactions  
   - Java/Python/Web Dev → full coding questions, output-based tasks  
   - DSA → algorithm writing, time complexity, tree/graph operations  
   - ToC → DFA/NFA, CFG, pumping lemma, TM design  
   - OS → scheduling, memory allocation, deadlock  
   - CN → subnetting, routing, protocols  
• Include pseudo-code or full code where appropriate  
• Include diagrams ONLY if required  
• Include real-world use cases when meaningful  

---

###  OUTPUT REQUIREMENTS
• Format must look like real final university paper  
• Marks must be correctly aligned  
• No explanations, only questions  
• No extra text or commentary  
• Clean academic language  
• Strictly follow the structure: PART A → PART B → PART C  

''' 
        else:
            prompt = f''''SYSTEM:
You generate clean, structured academic question papers.
Never include any extra text, suggestions, or formatting outside the required structure.
Use the syllabus strictly if provided. Never invent topics not in the syllabus.

USER:
Generate a MIDTERM Semester Question Paper EXACTLY in the following format:

SUBJECT: {subject}
DIFFICULTY LEVEL: {difficulty}

PART - A
Q1 – Compulsory Short Questions (5 × 1 = 5 Marks)
1. <short question 1> (1 Mark)
2. <short question 2> (1 Mark)
3. <short question 3> (1 Mark)
4. <short question 4> (1 Mark)
5. <short question 5> (1 Mark)

PART - B
Analytical/Long Questions (Attempt All) (5 × 3 = 15 Marks)
1. <long question 1> (3 Marks)
2. <long question 2> (3 Marks)
3. <long question 3> (3 Marks)
4. <long question 4> (3 Marks)
5. <long question 5> (3 Marks)

PART - C
Compulsory Problem-Solving Questions (2 × 5 = 10 Marks)
1. <problem question 1> (5 Marks)
2. <problem question 2> (5 Marks)

OUTPUT RULES:
• Strict academic tone.
• No headings outside the format.
• Use ONLY syllabus content if provided.
• If a topic is NOT in the syllabus, write “[NOT COVERED]”.

SYLLABUS (OPTIONAL):
{syllabus}

END

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
            paper_content = response.choices[0].message.content
            
            solution_prompt = f'''
SYSTEM:
You are an expert exam evaluator. You generate clean, accurate, academic-quality solutions.
Follow the question numbers exactly.
Do NOT change the questions.
Do NOT skip any question.
Do NOT add any new questions.
Keep formatting clean and suitable for a PDF.

USER:
Generate a full Solution Set for the following Question Paper.

SUBJECT: {subject}
DIFFICULTY LEVEL: {difficulty}

QUESTION PAPER:
{paper_content}

If a syllabus was provided earlier, use it to guide the depth and correctness of the solutions:
SYLLABUS (OPTIONAL):
{syllabus}

SOLUTION FORMAT (STRICT):
Provide structured answers like this:

PART - A SOLUTIONS  
Q1.1 <Short answer, 2–3 line explanation>  
Q1.2 <Short answer>  
Q1.3 <Short answer>  
Q1.4 <Short answer>  
Q1.5 <Short answer>

PART - B SOLUTIONS  
Q2.1 <Detailed explanation 8–12 lines, include diagrams in text form if required>  
Q2.2 <Explain using steps, derivation or comparison>  
Q2.3 <Algorithm/flowchart in text format if required>  
Q2.4 <Case study / real example explanation>  
Q2.5 <Long explanation with reasoning>

PART - C SOLUTIONS  
For programming/problem questions, provide:
• Full step-by-step reasoning  
• Pseudocode (if needed)  
• Flowcharts in text form  
• Time & space complexity  
• Final answers clearly highlighted  

OUTPUT RULES:
• No markdown formatting (no **, no ##, no * symbols)  
• Use only plain text suitable for PDF  
• No extra commentary  
• No instructions or system messages  
• Clean spacing with line breaks between answers  

END.
'''
            solution_response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "user", "content": solution_prompt}
                ]
            )
            solution_content = solution_response.choices[0].message.content
            paper_content += "\n\nSOLUTION SET\n\n" + solution_content
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