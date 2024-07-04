# ** rag- query
# food- **nutrition value, preference+ingredients- recipe, image
# fitness


import requests
import streamlit as st
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai
# from serpapi import GoogleSearch
import os
import pyimgur
import random
import google.generativeai as genai
# from IPython.display import Markdown
import streamlit as st

import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# ###############################################

class RAG:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.documents = None
        self.nodes = None
        self.query_engine = None
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def load_documents(self):
        loader = PDFReader()
        self.documents = loader.load_data(file=self.pdf_path)
        logging.debug(f"Loaded {len(self.documents)} documents from {self.pdf_path}")
        print("############# load documents")

    def parse_documents(self):
        parser = SimpleNodeParser.from_defaults(chunk_size=200, chunk_overlap=10)
        self.nodes = parser.get_nodes_from_documents(self.documents)
        logging.debug(f"Extracted {len(self.nodes)} nodes from documents")
        print("############### nodes")
    

    def setup_llm_and_index(self):
        llm = Gemini(model="models/gemini-pro")
        embed_model = GeminiEmbedding(model_name="models/embedding-001")
        
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 512

        vector_index = VectorStoreIndex(self.nodes)
        self.query_engine = vector_index.as_query_engine()

    def query(self, query_text):
        response_vector = self.query_engine.query(query_text)
        return response_vector.response
    
    def response(self,query_text):
        res = self.query(query_text)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"This data {res} is from the rag chatbot for the question {query_text}. Use the given data to answer the question {query_text} in a precise manner. Give answers to the point. Then for the explanation write EXPLANATION then explain. ")
        res = model.generate_content(prompt).text
        return res
    
    def response_food(self,query_text):
        query_text = f"Based on the health status of the patient, remove the unnecessary ingredients in {query_text} tell why. Also suggest a healthy recipe for the patient using these ingredients."
        res = self.query(query_text)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"This data {res} is from the rag chatbot for the question {query_text}. Use the given data to answer the question {query_text} in a precise manner. Give answers to the point. Then for the explanation write EXPLANATION then explain. ")
        res = model.generate_content(prompt).text
        return res


class NutritionAnalyzer:
    def __init__(self, ingredients):
        self.ingredients = ingredients
        self.dict_data = {}

    def nutrition(self, ingredient):
        app_key = 'your app id'  # Replace with your Edamam API app ID
        app_id = 'app key'  # Replace with your Edamam API app key
        result = requests.get(
            'https://api.edamam.com/api/nutrition-data?ingr={}&app_id={}&app_key={}'.format(ingredient, app_id, app_key)
        )
        data = result.json()
        return data

    def update_dict_data(self):
        for ingredient in self.ingredients:
            data = self.nutrition(ingredient)
            if 'calories' in self.dict_data:
                self.dict_data['calories'] += data['calories']
            else:
                self.dict_data['calories'] = data['calories']

            for key, value in data['totalNutrients'].items():
                label = value['label']
                quantity = value['quantity']
                if label in self.dict_data:
                    self.dict_data[label] += quantity 
                else:
                    self.dict_data[label] = quantity

    
        # Create final string representation of dict_data
        final_string = str(self.dict_data)
        return final_string
    
    def get_final_string(self):
        # Convert quantities to string with units
        dummy = self.nutrition(self.ingredients[0])
        units = {value['label']: value['unit'] for label, value in dummy['totalNutrients'].items()}
        final_data = {}
        for label, quantity in self.dict_data.items():
            if label in units:
                unit = units[label]
                final_data[label] = f"{quantity} {unit}, \n"
            else:
                final_data[label] = str(quantity) +", \n"
        if 'calories' in self.dict_data:
            final_data['calories'] = str(self.dict_data['calories'])+", \n"

        # Create final string representation of dict_data
        final_string = " ".join([f"{label}: {value}" for label, value in final_data.items()])
        return final_string
    
###################################################

st.markdown("<h1 style='color: black; font-style: italic; font-family: Comic Sans MS; font-size:3rem' >SmartHealth AI</h1> <h3 style='color: #494F55; font-style: italic; font-family: Comic Sans MS; font-size:1rem'> Your Digital Health Companion for Early Diagnosis and Better Care</h3>", unsafe_allow_html=True)

# rag model
rag = RAG(r"C:\Users\Lakshmi\Downloads\clinical_data_report (9).pdf")
rag.load_documents()
rag.parse_documents()
rag.setup_llm_and_index()

# extract data
symptoms = rag.response("What are symptoms mentioned in the data?")
treatments = rag.response("What are treatments mentioned in the data?")
dietary_restrictions = rag.response("What are dietary restrictions mentioned in the data?")
health_goals= rag.response("What are health goals mentioned in the data?")

# rag query
query = st.text_area("Enter query here")
if query:
    res = rag.response(query)
    st.write(res)

# FOOD
st.markdown("<h1 style='color: black; font-style: italic; font-family: Comic Sans MS; font-size:3rem' >SmartHealth AI</h1> <h3 style='color: #494F55; font-style: italic; font-family: Comic Sans MS; font-size:1rem'> Your Digital Health Companion for Early Diagnosis and Better Care</h3>", unsafe_allow_html=True)

# food-nutrition value
food = st.text_area("Enter food item here")
if food:
    ingredients = [name.strip() for name in food.split(",")]
    nutri = NutritionAnalyzer(ingredients)
    nutri.update_dict_data()
    nutri_res = nutri.get_final_string()
    st.write(f"the nutrition value of {food} is:")
    st.write(nutri_res)

# recipe-text
def recipe(data, symptoms, treatments, health_goals, restrictions):
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (f"You are a healthy recipe advisor. Based on the preference {data}, {health_goals}, and {restrictions}, provide a healthy recipe that is suitable for the individual. Please mention the ingredients and their quantities precisely. Note: This is for informational purposes only and should not replace professional medical advice.")
    res = model.generate_content(prompt).text
    return res

def get_imgredients(data):
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (f"For the recipe {data} give all the ingredients and quantity of the ingredients in the recipe to be made for a single person. Make sure that only healthy ingredients are mentions in a healthy quantity. Give the quantity and ingredient only, each data seperated by comma. Your response should be like 1 apple, 200g rice. ")
    res = model.generate_content(prompt).text
    return res

preference = st.text_area("Enter food preference here")
if preference:
    res1 = recipe(preference, symptoms, treatments, health_goals, dietary_restrictions)
    st.write("The suggested recipe is:")
    st.write(res1)
    ingredients = get_imgredients(res1)
    st.write("The ingredients are:")
    st.write(ingredients)
    i_arr = ingredients.split(',')
    nutri = NutritionAnalyzer(i_arr)
    nutri.update_dict_data()
    nutri_res = nutri.get_final_string()
    st.write("### the nutrition value of this recipe is:")
    st.write(nutri_res)





