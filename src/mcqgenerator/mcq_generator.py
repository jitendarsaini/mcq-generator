from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import streamlit as st

load_dotenv()
API_KEY = os.getenv("API_KEY")

client = ChatGroq(api_key=API_KEY, model="llama3-70b-8192")
clients = Groq(api_key=API_KEY)

file_path = os.path.join(os.path.dirname(__file__), "../Response.json")
with open(file_path, "r") as f:
	RESPONSE_JSON = json.load(f)

TEMPLATE = """
                    Text: {text}
                    You are an expert MCQ maker. Given the above text, it is your job to \
                    create a quiz of {number} multiple choice questions for {subject} students. 
           
                    **Boundaries:** 
                    The questions must follow these constraints: {boundaries}.
                    
                    Ensure that the questions:
                    - Are not repeated.
                    - Strictly adhere to the text and the given boundaries.
                    - Align with the subject and student level.
                    
                    Make sure to format your response like RESPONSE_JSON below and use it as a guide.
                    Ensure to generate exactly {number} MCQs.
                    ### RESPONSE_JSON
                    {RESPONSE_JSON}
           """

quiz_generation_prompt = ChatPromptTemplate(
	input_variables=["text", "number", "subject", "boundaries", "RESPONSE_JSON"],
	messages=[
		{"role": "user", "content": TEMPLATE}
	]
)

quiz_chain = LLMChain(llm=client, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

def call_groq(prompt):
	response = clients.chat.completions.create(
		model="llama-3.3-70b-versatile",
		messages=[
			{"role": "system", "content": "You are an expert MCQ creator."},
			{"role": "user", "content": prompt}
		],
		temperature=0.7,
		max_tokens=3000
	)
	return response.choices[0].message.content

def generate_quiz_prompt(text, number, subject, boundaries, response_json):
	return TEMPLATE.format(
		text=text,
		number=number,
		subject=subject,
		boundaries=boundaries,
		RESPONSE_JSON=json.dumps(response_json)
	)

st.title("MCQ Generator")

if "show_errors" not in st.session_state:
	st.session_state["show_errors"] = False

question = st.text_area("Enter your Text for MCQs:", height=100)
if st.session_state["show_errors"] and not question.strip():
	st.warning("⚠️ Please enter the text for MCQs.")

subject = st.text_input("Enter Subject (e.g., Mathematics, Science, AI):")
if st.session_state["show_errors"] and not subject.strip():
	st.warning("⚠️ Please enter the subject.")

boundaries = st.text_input("Define MCQ Boundaries (e.g., Difficulty Level, Focus Topics):")
if st.session_state["show_errors"] and not boundaries.strip():
	st.warning("⚠️ Please define the MCQ boundaries.")

number_of_mcqs = st.number_input("Number of MCQs:", min_value=1, max_value=50, value=10)
if st.session_state["show_errors"] and number_of_mcqs <= 0:
	st.warning("⚠️ Please select a valid number of MCQs.")

if st.button("Generate MCQs"):
	if not question.strip() or not subject.strip() or not boundaries.strip() or number_of_mcqs <= 0:
		st.session_state["show_errors"] = True 
		st.rerun() 
	else:
		st.session_state["show_errors"] = False 
		quiz_prompt = generate_quiz_prompt(question, number_of_mcqs, subject, boundaries, RESPONSE_JSON)
		mcq_response = call_groq(quiz_prompt)
		st.subheader("Generated MCQs:")
		st.write(mcq_response)
  
  
  
  
  
  
  
  
#   if "show_errors" not in st.session_state:
#     st.session_state["show_errors"] = False

# if "mcq_response" not in st.session_state:
#     st.session_state["mcq_response"] = {}

# if "user_answers" not in st.session_state:
#     st.session_state["user_answers"] = {}

# # Sample MCQ JSON (Replace with API response)
# RESPONSE_JSON = {
#     "1": {"mcq": "What does the text 'adsds' primarily consist of?", "options": {"a": "Letters", "b": "Numbers", "c": "Symbols", "d": "Punctuation"}, "correct": "a"},
#     "2": {"mcq": "How many characters are in the text 'adsds'?", "options": {"a": "3", "b": "4", "c": "5", "d": "6"}, "correct": "c"},
# }

# # Input fields
# question = st.text_area("Enter your Text for MCQs:", height=100)
# subject = st.text_input("Enter Subject (e.g., Mathematics, Science, AI):")
# boundaries = st.text_input("Define MCQ Boundaries (e.g., Difficulty Level, Focus Topics):")
# number_of_mcqs = st.number_input("Number of MCQs:", min_value=1, max_value=50, value=10)

# # Show warnings if "Generate MCQs" was clicked without valid inputs
# if st.session_state["show_errors"]:
#     if not question.strip():
#         st.warning("⚠️ Please enter the text for MCQs.")
#     if not subject.strip():
#         st.warning("⚠️ Please enter the subject.")
#     if not boundaries.strip():
#         st.warning("⚠️ Please define the MCQ boundaries.")
#     if number_of_mcqs <= 0:
#         st.warning("⚠️ Please select a valid number of MCQs.")

# # Generate MCQs
# if st.button("Generate MCQs"):
#     if not question.strip() or not subject.strip() or not boundaries.strip() or number_of_mcqs <= 0:
#         st.session_state["show_errors"] = True
#         st.rerun()
#     else:
#         st.session_state["show_errors"] = False
#         # Simulate API call (Replace with actual API call)
#         st.session_state["mcq_response"] = RESPONSE_JSON
#         st.rerun()

# # Display MCQs only if they exist
# if st.session_state["mcq_response"]:
#     st.subheader("Generated MCQs:")
#     for q_id, data in st.session_state["mcq_response"].items():
#         st.write(f"**Q{q_id}: {data['mcq']}**")
#         options = data["options"]
        
#         # Create a radio button for each question
#         user_choice = st.radio(
#             f"Select your answer for Q{q_id}",
#             list(options.keys()),
#             format_func=lambda x: f"{x}. {options[x]}",
#             key=f"q_{q_id}"
#         )
#         st.session_state["user_answers"][q_id] = user_choice  # Store user response

# # Submit Quiz
# if st.button("Submit Quiz") and st.session_state["mcq_response"]:
#     score = 0
#     total_questions = len(st.session_state["mcq_response"])
#     results = []

#     # Calculate the score
#     for q_id, data in st.session_state["mcq_response"].items():
#         correct_answer = data["correct"]
#         user_answer = st.session_state["user_answers"].get(q_id, None)

#         if user_answer == correct_answer:
#             score += 1
#             results.append(f"✅ **Q{q_id}: Correct!**")
#         else:
#             results.append(f"❌ **Q{q_id}: Incorrect!** (Correct: {correct_answer})")

#     # Display results
#     st.subheader(f"Your Score: {score}/{total_questions}")
#     for res in results:
#         st.write(res)
