# -*- coding: utf-8 -*-
"""anakin.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YB3CvYX4FPvvzRXLUPLh2-8joVEgoWFo
"""

import streamlit as st
import pandas as pd
import os
import google.generativeai as genAI
import seaborn as sns
import tempfile
import pyperclip
import io
import matplotlib.pyplot as plt

# Set Google Generative AI API key


# Function to generate content
@st.cache_data
def generate_content(prompt, data):
    apikey=st.text_input("Google Ai API key: ")
    input_text = data + " " + prompt
    os.environ['API_KEY'] = apikey
    genAI.configure(api_key=os.environ['API_KEY'])
   # Initialize GenerativeModel
    model = genAI.GenerativeModel('gemini-pro')

    
    response = model.generate_content(input_text)

    if response.text:  # Check if the response contains any text
        return response.text
    else:
        st.error("Failed to generate content. Please try again later.")
        return ""

@st.cache_data
def shorten(prompt):
  simplify=model.generate_content(prompt+"   "+"shorten this to 1-2 words")
  return simplify.text



# Main app/dashboard
def main():
    st.set_page_config(
        page_title="Data Analysis using Generative AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    theme = st.color_picker("pick a background color")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme};
        }}
        .sidebar .sidebar-content {{
            background-color: {theme};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Set app title with colorful background and AI image
    st.title("Data Analysis using Generative AI")
    st.markdown(
        f"""
        <style>
        .title {{
            background-color: {theme};
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Prompt input from user with illustration
    st.subheader("Enter the prompt for analysis:")
    analysis_prompt = st.text_input("For example: 'Summarize the data.'", "")

    # File uploader with colorful background
    st.subheader("Upload your data:")
    uploaded_file = st.file_uploader(
        "Upload a file (CSV or TXT)", type=["txt", "csv"], key="fileUploader"
    )

    q = None
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        try:
            if file_ext == 'csv':
                q = pd.read_csv(uploaded_file)
            elif file_ext == 'txt':
                q = pd.read_csv(uploaded_file, sep='\t')
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")

    # Display file content
    a=st.radio("uploaded file",options=["View","Hide"])
    if a=="View":
      st.write(q)

    # Plotting
    if q is not None:
        if uploaded_file.name.endswith(('.csv', '.txt')):
            st.write("Plot graph")
            x = st.selectbox("x", q.columns.tolist())
            y = st.multiselect("y", q.columns.tolist())
            try:
              w = q.plot(x, y, kind='line')
              z = st.radio("Graph", ["View", "Hide"])
              a = w.figure
              if z == "View":
                  st.pyplot(a)
            except:
              if len(y)==0:
                st.error("no data to plot with")
              elif x in y:
                st.warning("same data cannot be present on both axes")
              else:
                st.write("not possible to plot")


    if analysis_prompt and q is not None:
        # Generate content
        try:
            response = generate_content(analysis_prompt, q.to_string())
            short=shorten(analysis_prompt)
            # Display generated content with colorful background and AI illustration
            st.subheader("Generated content:")
            st.markdown(
                f"""
                <div style='background-color:{theme}; color:white; padding: 10px; border-radius: 10px; border-color:#ff0000'>
                {response}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Export option
            text_bytes = response.encode('latin1')

            # Create a file-like object
            text_stream = io.BytesIO(text_bytes)

            st.download_button(
               label="Download Text File",
               data=text_stream,
               file_name=uploaded_file.name+short+".txt",
               mime="text/plain"
            )

# Offer the file for download


            # Copy to clipboard option
            if st.button("Copy to Clipboard"):
                pyperclip.copy(response)
                st.success("Generated content copied to clipboard!")

        except ValueError:
            st.error("Something unexpected happened, please try again")
        except:
            st.warning("Please use a smaller file")

if __name__ == "__main__":
    main()
