# AI Diagnosis
# features
# ** text = user_data, de_identify, extract, final data 
# ** image = user image, g_lens
# ** pdf = de-identify, remove unnecessary details, get data
# final report


import boto3
import google.generativeai as genai
import os
import streamlit as st
import os
import random
import google.generativeai as genai
import PyPDF2
import google.generativeai as genai
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# text
class MedicalDataProcessor:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='us-east-1'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.comprehend_client = self.initialize_comprehend_client()
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.initialize_google_genai()

    def initialize_comprehend_client(self):
        return boto3.client(
            service_name='comprehendmedical',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def detect_entities(self, text):
        result = self.comprehend_client.detect_entities(Text=text)
        entities = result['Entities']
        filtered_entities = [{'Text': item['Text'], 'Traits': item['Traits'], 'Score': item['Score']} for item in entities if item['Traits']]
        return filtered_entities

    def initialize_google_genai(self):
        genai.configure(api_key=self.google_api_key)

    def generate_content(self, prompt):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt).text
        return response

    def process_medical_data(self, data):
        entities = self.detect_entities(data)
        print("Detected entities from Comprehend Medical:", entities)

        prompt1 = f"from the given clinical data {data} extract the symptoms, treatment, medication dosage and frequency, health history, disorder(disease) and any other medical concepts only if mentioned in the given data. Your response should be like The symptoms are symptom1, symptom2, the treatments taken are treatment1,... and the same pattern for all. Also just give the data in a formatted manner for the final report"
        res1 = self.generate_content(prompt1)
        print("Response from Gemini:", res1)

        prompt2 = f"Based on the above responses from gemini {res1} and Comprehend Medical {str(entities)}, provide a final description of the patient's symptoms, treatment, medication and dosage of medication(if mentioned), health history, disorder(disease) and any other medical concepts. Your response should be like The symptoms are symptom1, symptom2, the treatments taken are treatment1,... and the same pattern for all. Also just give the data in a formatted manner for the final report. If some data is not mentioned or specified then no need to mention that in the final report. "
        res2 = self.generate_content(prompt2)
        return "Final description:\n"+ str(res2)

    def deidentify(self,data):
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        prompt=f"PFrom the given data {data}, remove personal details of the patient like name, address and any other non medical personal information about the patient."
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt).text
        return res


# Image class
class IAnalysis:

    def __init__(self, file_path):
        self.file_path = file_path
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
     
    def g_vision(self):
        sample_file = genai.upload_file(path=self.file_path, display_name="image")
        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content([sample_file, "What can be seen in the image? Describe what ever can be seen in the image. This is health related image. Mention if there are any abnormalities seen in the image. Describe the image in medical manner."])
        return response.text
    
    def gemini(self):
        v_data = self.g_vision()
        st.write(v_data)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"The following information is about the image uploaded by a patient(user). The google vision pro says: {v_data}.  Your duty is to consider the above given information and give a precise output about what the image is about. It is related to health. While analysing the data, give more importance to the google vision data.")
        res = model.generate_content(prompt).text
        return res


    def i_analysis(self):
        gemini_data = self.gemini()
        data = "The analysis of the uploaded image reveals the following data: "+ gemini_data


# pdf report
class R_Analysis:
    def __init__(self, file_path):
        self.file_path = file_path
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def extract_pdf(self):
        data = ""
        with open(self.file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]
                data += page.extract_text()
        return data        
    
    def deidentify(self,data):
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        prompt=f"PFrom the given data {data}, remove personal details of the patient like name, address and any other non medical personal information about the patient."
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt).text
        return res
    
    def get_data(self):
        data = self.extract_pdf()
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"the given data {data} is a medical lab report data. Organize this data is data is the right format with just the parameter/fields and the value. So that this data can be written in final diagnosis report of the patient. Remove unnecessary data.")
        res = model.generate_content(prompt).text
        result = self.deidentify(res)
        return result

class F_Diagnose:

    def __init__(self, data):
        self.data = data
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def diagnosis_report(self):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"You are a healthcare assistant to help the health professional understand the problem. Thus you have to help prepare a diagnosis report based in the given patient data. The given data {self.data} of the medical details of the patient. Consider this information about the patient. Provide a detailed explaination as to what the person is suffering from based in the data. Tell what may be the reasons why the person is suffering from the problems he/she has. Basically you should help provide a diagnosis report based on the given data. Make sure the result repovided is well formatted.")
        res = model.generate_content(prompt).text
        return res
    
    def suggestions(self,data):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"Based on the given data given {data} about a patient you have to be the health care advisor. Suggest Dietary Restrictions, Required physical activities, Life style changes for better health, Health Goals the patient must set for better health. For all of these categories, provide a well formatted report to help manage the person's health condition.")
        res = model.generate_content(prompt).text
        return res
    
class PDFGenerator:
    def __init__(self, text_data, file_path_pdf):
        self.text_data = text_data
        self.file_path_pdf = file_path_pdf

    def create_pdf(self):
        # Create a buffer to hold the PDF data
        buffer = io.BytesIO()

        # Create a PDF with reportlab
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Define a title
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 50, "Clinical Data Report")

        # Define the starting position
        text = c.beginText(50, height - 100)
        text.setFont("Helvetica", 10)
        max_width = width - 100  # Set the max width for text wrapping

        # Split the text into lines
        lines = self.text_data.split('\n')

        for line in lines:
            # Wrap text to fit within the page width
            wrapped_lines = self.wrap_text(line, max_width, c)
            for wrapped_line in wrapped_lines:
                text.textLine(wrapped_line)
                # Check if the text exceeds the page height
                if text.getY() < 50:
                    c.drawText(text)
                    c.showPage()
                    text = c.beginText(50, height - 50)
                    text.setFont("Helvetica", 10)

        c.drawText(text)
        c.showPage()
        c.save()

        # Move buffer position to the beginning
        buffer.seek(0)

        # Save the PDF to a file
        with open(r"D:\h1\AIHealthCare\AIHealthCare\data\R.pdf", 'wb') as f:
            f.write(buffer.getvalue())

        return buffer

    @staticmethod
    def wrap_text(text, max_width, canvas):
        """Wrap text to fit within a specified width."""
        lines = []
        words = text.split(' ')
        line = ''
        for word in words:
            test_line = f"{line} {word}".strip()
            if canvas.stringWidth(test_line, "Helvetica", 10) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)  # Add the last line
        return lines

# FITNESS
import requests
import json
# API keys and URLs
NUTRITIONIX_API_KEY = 'key'  # Replace with your Nutritionix API key
NUTRITIONIX_API_URL = 'https://api.nutritionix.com/v1_1/nutrition'
EXERCISE_DB_BASE_URL = "https://exercisedb.p.rapidapi.com/exercises"
querystring = {"limit":"10","offset":"0"}
headers = {
    "x-rapidapi-key": "Your key",  # Replace with your RapidAPI key
    "x-rapidapi-host": "exercisedb.p.rapidapi.com"
}
def get_exercises():
    """
    Fetch all exercises from ExerciseDB API.
    Returns:
        list: A list of exercises.
    """
    try:
        response = requests.get(EXERCISE_DB_BASE_URL, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def filter_exercises_by_body_type(exercises, body_type):
    """
    Filter exercises based on the body type.
    Args:
        exercises (list): List of exercises from ExerciseDB API.
        body_type (str): The user's body type.
    Returns:
        list: A list of filtered exercises.
    """
    body_type_exercises = {
        'ectomorph': ['full body', 'upper legs', 'lower legs'],
        'mesomorph': ['strength', 'chest', 'back', 'upper arms'],
        'endomorph': ['cardio', 'waist']
    }

    categories = body_type_exercises.get(body_type.lower(), ['full body'])

    filtered_exercises = [
        exercise for exercise in exercises
        if any(category in exercise['bodyPart'] for category in categories)
    ] 
    return filtered_exercises
def get_calorie_intake(body_type):
    """
    Calculate recommended calorie intake based on the body type.
    Args:
        body_type (str): The user's body type.
    Returns:
        dict: Calorie intake recommendation.
    """
    calorie_intake = {
        'ectomorph': '2500 calories',
        'mesomorph': '3000 calories',
        'endomorph': '2000 calories'
    }
    intake = calorie_intake.get(body_type.lower(), '2500 calories')
    return {"recommended_calorie_intake": intake}
def fitness():
    """
    Main function to run the script. Prompts the user for body type and prints recommendations.
    """
    body_type = input("Enter your body type (ectomorph, mesomorph, endomorph): ").strip().lower()
    
    # Get all exercises from ExerciseDB API
    exercises = get_exercises()
    
    if "error" in exercises:
        print(json.dumps(exercises, indent=4))
        return
    # Filter exercises based on the body type
    filtered_exercises = filter_exercises_by_body_type(exercises, body_type)
    # Get calorie intake recommendation
    calorie_intake = get_calorie_intake(body_type)
    # Print the results in JSON format
    result = {
        "exercises": filtered_exercises,
        "calorie_intake": calorie_intake
    }
    # Convert the result to a JSON string
    result_json = json.dumps(result, indent=4)
    # Convert the JSON string back to a Python dictionary
    result_dict = json.loads(result_json)
    return result_dict





# ##################################

# INTRODUCTION
st.markdown("<h1 style='color: black; font-style: italic; font-family: Comic Sans MS; font-size:5rem' >SmartHealth AI</h1> <h3 style='color: #494F55; font-style: italic; font-family: Comic Sans MS; font-size:2rem'> Your Digital Health Companion for Early Diagnosis and Better Care</h3>", unsafe_allow_html=True)


# TEXT
aws_access_key_id = 'key id'
aws_secret_access_key = 'access key'
text_data = st.text_area("Enter the patient details here")
f_text = ""
if text_data:
    processor = MedicalDataProcessor(aws_access_key_id, aws_secret_access_key)
    text_deidentified = processor.deidentify(text_data)
    f_text = processor.process_medical_data(text_deidentified)
    st.write(f_text)

# Image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
dir = "D:/h1/AIHealthCare/AIHealthCare/data"
i_data=""
if uploaded_file is not None:
    file_path = os.path.join(dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer()) 
    st.success(f"Saved file: {file_path}")
    i_analysis = IAnalysis(file_path)
    i_data = i_analysis.g_vision()
    st.image(uploaded_file)
    st.write(i_data)
    i_data = "The image uploaded by the user reveals" + i_data



# pdf report
uploaded_pdf = st.file_uploader("Upload an image", type=["pdf"])
r_data=""
if uploaded_pdf is not None:
    file_path = os.path.join(dir, uploaded_pdf.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_pdf.getbuffer()) 
    st.success(f"Saved file: {file_path}")
    r_analysis = R_Analysis(file_path)
    r_data = r_analysis.get_data()
    st.write(r_data)


# final report
def format(data):
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (f"For the given data {data} format the data in a precise manner. This formatted data will be the diagnosis report to be written to a pdf and given to the user. This pdf will then be used for RAG. So format this data such that RAG can eisily extract the required medical concepts based on the query. Like Instead of Giving Symptoms: symptom1, symptom2 format the data to Symptoms: the symptoms are symptom1, symptom2. For Treatment: The treatments are treatment1, treatment 2. For Dietary Restrictions: the Dietary Restrictions are dietary_restrictions1,dietary_restrictions2. For  Health Goals: health_goal1, health_goal2.  This way the RAG will easily be able to extract specific data when question like What? are asked.")
    res = model.generate_content(prompt).text
    return res

# final data
file_path_pdf = r"D:\recurzive\project\data\clinical_data_report.pdf"
os.makedirs(os.path.dirname(file_path_pdf), exist_ok=True)
if text_data and i_data and r_data:
    final_data = f"{f_text}\n{i_data}\n{r_data}"
    # diagnosis report
    f_diagnose = F_Diagnose(final_data)
    diagnosis_report = f_diagnose.diagnosis_report()
    diagnosis_report+=f_diagnose.suggestions(diagnosis_report)
    st.write("Final combined data:")
    st.write(diagnosis_report)
    pdf_data_input = format(diagnosis_report)
    pdf_gen = PDFGenerator(pdf_data_input, file_path_pdf)
    pdf_buffer = pdf_gen.create_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="clinical_data_report.pdf",
        mime="application/pdf"
    )




