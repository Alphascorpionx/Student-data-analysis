# -*- coding: utf-8 -*-
"""anakin.ipynb

Automatically generated by Colab.

Original file is located at
https://colab.research.google.com/drive/1YB3CvYX4FPvvzRXLUPLh2-8joVEgoWFo"""

import streamlit as st
import pandas as pd
import os
import google.generativeai as genAI
import seaborn as sns
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import tempfile

# Set Google Generative AI API key

# Function to generate content
@st.cache_data
def generate_content(prompt, data, key):
    os.environ['API_KEY'] = key
    genAI.configure(api_key=os.environ['API_KEY'])
    model = genAI.GenerativeModel('gemini-pro')
    input_text = data + " " + prompt
    response = model.generate_content(input_text)
    if response.text:
        return response.text
    else:
        st.error("Failed to generate content. Please try again later.")
        return ""

@st.cache_data
def shorten(prompt, key):
    os.environ['API_KEY'] = key
    genAI.configure(api_key=os.environ['API_KEY'])
    model = genAI.GenerativeModel('gemini-pro')
    simplify = model.generate_content(prompt + " " + "shorten this to 1-2 words")
    return simplify.text

# Function to read PDF
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to save plot as an image
def save_plot_image(image_path):
    plt.savefig(image_path, format='png')

# Function to create a PDF with content and plot
def create_pdf(content, plot_image_path, student_id):
    pdf_path = tempfile.mktemp(suffix=".pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    # Add generated content to the PDF
    content_paragraph = Paragraph("<b>Generated Content:</b>", styles['Title'])
    flowables.append(content_paragraph)
    flowables.append(Spacer(1, 12))

    # Ensure text fits within margins and wrap correctly
    content_paragraph = Paragraph(content, styles['BodyText'])
    flowables.append(content_paragraph)
    flowables.append(Spacer(1, 24))

    # Add plot image to the PDF
    if plot_image_path:
        flowables.append(Paragraph("Plot:", styles['Title']))
        flowables.append(Spacer(1, 12))
        img = Image(plot_image_path)
        img.drawHeight = 4*inch
        img.drawWidth = 6*inch
        flowables.append(img)

    doc.build(flowables)
    return pdf_path

# Main app/dashboard
def main():
    st.set_page_config(
        page_title="Data Analysis using Generative AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    theme = st.color_picker("Pick a background color")
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

    apikey = st.text_input("Google AI API key: ")
    st.subheader("Enter the prompt for analysis:")
    analysis_prompt = st.text_input("For example: 'Summarize the data.'", "")

    st.subheader("Upload your data:")
    uploaded_file = st.file_uploader(
        "Upload a file (CSV, TXT, or PDF)", type=["txt", "csv", "pdf"], key="fileUploader"
    )

    q = None
    pdf_text = ""
    file_ext = "" # Initialize file_ext with a default value

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        try:
            if file_ext == 'csv':
                q = pd.read_csv(uploaded_file)
            elif file_ext == 'txt':
                q = pd.read_csv(uploaded_file, sep='\t')
            elif file_ext == 'pdf':
                pdf_text = read_pdf(uploaded_file)
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")

    a = st.radio("Uploaded file", options=["View", "Hide"])
    if a == "View":
        if file_ext in ['csv', 'txt']:
            st.write(q)
        elif file_ext == 'pdf':
            st.write(pdf_text)

    plot_image_path = None
    if q is not None:
        if uploaded_file.name.endswith(('.csv', '.txt')):
            st.write("Plot graph")
            x = st.selectbox("Select x-axis", q.columns.tolist())

            y = st.multiselect("Select y-axis", q.columns.tolist())

            if x and y:
               xy = st.multiselect("Select elements for x", q[x].tolist(), default=q[x].tolist())

               # Filter DataFrame based on selected x-axis elements
               filtered_q = q[q[x].isin(xy)]

               # Plotting
               if not filtered_q.empty:
                  try:
                    fig, ax = plt.subplots()
                    filtered_q.plot(x=x, y=y, kind='line', ax=ax, marker='o')
                    ax.set_title('Filtered Data Plot')
                    ax.set_xlabel(x)
                    ax.set_ylabel(', '.join(y))
                    ax.tick_params(axis='both', labelsize=8)
                    wew=st.radio("Annotations",options=["Hide", "View"])
                    if wew=="View":
                      for col in y:
                       for i in range(filtered_q.shape[0]):
                            ax.annotate(f'({filtered_q[x].iloc[i]}, {filtered_q[col].iloc[i]})',
                                (i, filtered_q[col].iloc[i]),  # Using index `i` for positioning
                                textcoords="offset points", xytext=(5, 5), ha='center')


                  except KeyError:
                    st.error("same column cannot be present on both axes")
                  except TypeError:
                    st.error("data must be numeric")

                  # Save the plot as an image
                  plot_image_path = tempfile.mktemp(suffix=".png")
                  save_plot_image(plot_image_path)

                  # Display the plot in Streamlit
                  z = st.radio("Graph", ["View", "Hide"])
                  if z == "View":
                     st.pyplot(fig)

    if analysis_prompt and (q is not None or pdf_text):
        try:
            if q is not None:
                response = generate_content(analysis_prompt, q.to_string(), apikey)
            else:
                response = generate_content(analysis_prompt, pdf_text, apikey)

            short = shorten(analysis_prompt, apikey)
            st.subheader("Generated content:")
            st.markdown(
                f"""
                <div style='background-color:{theme}; color:white; padding: 10px; border-radius: 10px; border-color:#ff0000'>
                {response}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if plot_image_path:
                pdf_path = create_pdf(response, plot_image_path, xy)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Report",
                        data=pdf_file,
                        file_name=f"{shorten(analysis_prompt,apikey)}.pdf",
                        mime="application/pdf"
                    )

        except ValueError:
            st.error("Something unexpected happened, please try again")
        except Exception as e:
            st.warning(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
