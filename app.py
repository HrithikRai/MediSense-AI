import streamlit as st
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv, find_dotenv
import numpy as np

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("multi-qa-distilbert-cos-v1")

pc = Pinecone( api_key = os.environ.get("PINECONE_API_KEY"), environment = os.environ.get("PINECONE_ENV"))

index_name = 'medi-sense-ai'
index = pc.Index(index_name)

gif_path = 'misc/ambulance.gif'

# Function to search for medicines
def search_medicines(symptoms):
    symptoms_embedding = model.encode(symptoms, show_progress_bar=False).tolist()
    score_threshold = 0.6
    query_results = index.query(
        vector=[symptoms_embedding],
        top_k=3,
        include_metadata=True
    )
    recommendations = []
    for match in query_results['matches']:
        if match['score'] >= score_threshold:
            details = match.get('metadata', {})
            recommendations.append({
                'possible_disease': details.get('disease', 'N/A'),
                'medicine_name': details.get('medicine_name', 'N/A'),
                'treatment_drug': details.get('treatment_drug', 'N/A'),
                'type_of_drug': details.get('type_of_drug', 'N/A'),
                'symptoms': details.get('symptoms', 'N/A'),
                'daily_adult_dosage': details.get('daily_adult_dosage', 'N/A'),
                'num_days': details.get('num_days', 'N/A'),
                'price': details.get('price/unit', 'N/A'),
            })
    print(recommendations)
    return recommendations

# Streamlit App
st.set_page_config(page_title="medi-sense-ai", page_icon="💊", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    body { font-family: Arial, sans-serif; }
    .prescription-box {
        background-color: #ffffff;
        padding: 20px;
        border: 2px solid #c4c4c4;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }
    .title { font-size: 2em; color: #2d6a4f; text-align: center; font-weight: bold; }
    .subtitle { color: #7f7f7f; text-align: center; font-style: italic; }
    .warning { font-size: 0.85em; color: red; text-align: center; }
    .prescription { font-size: 1.1em; margin: 0; color: #333; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='title'>MediSense-AI- Sense your symptoms, find your cure.</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your personal guide to medicine recommendations</div>", unsafe_allow_html=True)
st.write("")

# Input symptoms
st.subheader("Enter your symptoms:")
user_input = st.text_input("List your symptoms, separated by commas (e.g., fever, cough, headache)")

# Search and display recommendations
if st.button("Get Prescription"):
    if user_input:
        recommendations = search_medicines(user_input)
        possible_diseases = []
        cost = []
        if recommendations:
            st.image(gif_path, use_column_width=True)

            for rec in recommendations:
                possible_diseases.append(rec['possible_disease'])
                st.write("**Medicine Name:**", rec['medicine_name'])
                st.write("**Active Ingredient:**", rec['treatment_drug'])
                st.write("**Type of Drug:**", rec['type_of_drug'])
                st.write("**Symptoms Addressed:**", rec['symptoms'])
                st.write("**Dosage (per day):**", rec['daily_adult_dosage'])
                st.write("**Days Required:**", rec['num_days'])
                
                # Estimating cost for treatment
                try:
                    dosage_required = int(rec['daily_adult_dosage']) * int(rec['num_days'])
                    price_per_unit = float(rec['price'])
                    total_cost = (dosage_required) * price_per_unit  
                    cost.append(total_cost)
                    st.write(f"**Estimated treatment Cost:** ₹{total_cost:.2f}")
                except:
                    st.write("**Estimated Cost:** Not available")
                
                st.write("---")

            
            st.write("**Possible Disease/Condition:**", possible_diseases)
            st.write("**Total Treatment Cost ₹", sum(cost))
            st.markdown("<div class='warning'>⚠️ This recommendation is not a substitute for a medical diagnosis. Please consult a licensed healthcare provider before taking any medication.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write("No recommendations found. Please try again with different symptoms.")
    else:
        st.write("Please enter your symptoms.")

# Search by Disease or Drug Name
st.sidebar.header("Advanced Search")
st.sidebar.write("Looking for specific disease or drug?")
disease_search = st.sidebar.text_input("Enter disease name:")
if st.sidebar.button("Search Disease"):
    disease_recommendations = search_medicines(disease_search)
    if disease_recommendations:
        st.sidebar.write("### Recommended Medicines for", disease_search)
        for rec in disease_recommendations:
            st.sidebar.write("**Medicine:**", rec['medicine_name'])
            st.sidebar.write("**Symptoms:**", rec['symptoms'])
            st.sidebar.write("**Dosage:**", rec['daily_adult_dosage'])
            st.sidebar.write("---")
    else:
        st.sidebar.write("No medicines found for this disease.")