from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv 
import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain , SequentialChain
import streamlit as st

load_dotenv()

API_KEY = os.getenv("API_KEY")

client = ChatGroq(api_key=API_KEY, model="llama3-70b-8192")


clients = Groq(api_key=API_KEY)


TEMPLATE="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{RESPONSE_JSON}
"""


file_path = os.path.join(os.path.dirname(__file__), "../Response.json")

with open(file_path,"r") as f:
    RESPONSE_JSON=json.load(f)
    
    
    
quiz_generation_prompt=ChatPromptTemplate(
    input_variables=["text","number","subject","tone","RESPONSE_JSON"],
    messages=[ 
        {"role": "user", "content": TEMPLATE}
    ]
)


quiz_chain=LLMChain(llm=client,prompt=quiz_generation_prompt,output_key="quiz",verbose=True)

     
     
TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""


quiz_evaluation_prompt=ChatPromptTemplate(
    input_variables=["subject","quiz"],
    messages=[ 
        {"role": "user", "content": TEMPLATE2}
    ]
)

review_chain=LLMChain(llm=client,prompt=quiz_evaluation_prompt,output_key="review",verbose=True)

generate_evaluate_chain=SequentialChain(chains=[quiz_chain,review_chain] , input_variables=["text","number","subject","tone","RESPONSE_JSON"] , output_variables=["quiz","review"],verbose=True)



NUMBER=20
SUBJECT="AI"
TONE="Simple"
RESPONSE_JSON=RESPONSE_JSON
 

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



def generate_quiz_prompt(text, number, subject, tone, response_json):
    return TEMPLATE.format(
        text=text,
        number=number,
        subject=subject,
        tone=tone,
        RESPONSE_JSON=json.dumps(response_json)
    ) 

# quiz_prompt = generate_quiz_prompt(TEXT, NUMBER, SUBJECT, TONE, RESPONSE_JSON)
# mcq_response = call_groq(quiz_prompt) 
  
st.title("MCQ Generator")

question = st.text_area("Enter your Text for generate MCQs:",height=300)

if st.button("Generate MCQs"):
    quiz_prompt = generate_quiz_prompt(question, NUMBER, SUBJECT, TONE, RESPONSE_JSON)
    mcq_response = call_groq(quiz_prompt)

    st.text("Generated MCQs:")
    st.write(mcq_response)