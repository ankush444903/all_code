import tensorflow.keras as keras
import os
import os
from bs4 import BeautifulSoup
import sys
import re
import os
import re
from groq import Groq
import openai
from langchain.vectorstores import FAISS
import pdfplumber
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from flask import Flask, render_template, jsonify, request
from datasets import load_dataset
from flask import Flask, request, jsonify
#from TRANSLATION.Demo import TranslationService
import json
from Demo import TranslationService # Add translation funcation here

######api_key = ""
#pdf_folder_path = r"AIB\\PDF"
persist_directory = os.path.abspath('Croma_Database')
#folder_path = r"C:\\Users\\parth1729\\Desktop\\AIB\\Text_Data"
folder_path = r"C:\Users\parth1729\Desktop\AIB\1filetext"


def extract_text_from_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print("Plsease check the pdf to text extraction function, this is the error:",e)

def convert_pdfs_to_text(pdf_folder_path, output_folder_path):
    try:
        pdf_files = [os.path.join(pdf_folder_path, file) for file in os.listdir(pdf_folder_path) if file.endswith('.pdf')]
        for pdf_file in pdf_files:
            
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)
            pdf_file_name = os.path.basename(pdf_file)
            text_file_name = os.path.splitext(pdf_file_name)[0] + '.txt'
            file_path = os.path.join(output_folder_path, text_file_name)
            pdf_text = extract_text_from_pdf(pdf_file)
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(pdf_text)
    except Exception as e:
        print("Plsease check the convert pdf to text and save the ext in text data folder, this is the error:",e)

def load_documents_from_directory(directory_path):
    try:
        text_loader_kwargs={'autodetect_encoding': True}
        loader = DirectoryLoader(directory_path, glob="./*.txt", loader_cls=TextLoader,  loader_kwargs=text_loader_kwargs)
        return loader.load()
    except Exception as e:
        print("Plsease check the directory loader function, this is the error:",e)

def split_text_documents(documents, chunk_size=2500, chunk_overlap=260):
    try:    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_documents(documents)
    except Exception as e:
        print("Plsease check the text splitting function, this is the error:",e)

def create_vector_database(text_documents, persist_directory):
    try:
        embedding = OpenAIEmbeddings(api_key=api_key)
        vectordb = Chroma.from_documents(documents=text_documents, embedding=embedding, persist_directory=persist_directory)
        vectordb.persist()
        return vectordb
    except Exception as e:
        print("Plsease check the creating vector database function, this is the error:",e)

# def create_vector_database(text_documents):
#     try:
#         embedding = OpenAIEmbeddings(api_key=api_key)
#         vectordb = FAISS.from_documents(documents=text_documents, embedding=embedding)

#         return vectordb
#     except Exception as e:
#         print("Plsease check the creating vector database function, this is the error:",e)

def retrieve_relevant_documents(query, vectordb, k=2):
    try:
        retriever = vectordb.as_retriever(search_kwargs={"k": k})
        return retriever.get_relevant_documents(query)
    except Exception as e:
        print("Plsease check the document retrival function, this is the error:",e)

def extract_section(target_text, section_number):
    try:
        pattern = rf"({section_number}.*?)\n(.*?)(?=\n\d+\.\d+|\Z)"
        match = re.search(pattern, target_text, re.DOTALL)
        if match:
            section_title, extracted_text = match.groups()
            return f"{section_title}\n{extracted_text.strip()}"
        else:
            return f"Section '{section_number}' not found in the document."
    except Exception as e:
        print("Plsease check the section extraction function, this is the error:",e)

def Review_Manual(input_text):
    client = Groq(api_key="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")
    response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI User manual review  assistant. You are going to review the generated user manual and provide feedback on clarity, coherence, and overall quality."},
                {"role": "user", "content": "Review the generated user manual and provide feedback on clarity, coherence, and overall quality.\n\n{}" .format(input_text)},
                        ],
            model="Llama3-8b-8192",)
    
    Review = response.choices[0].message.content
    return Review



# Define machine name lists
A = ["BD 1400+", "BD 1800+", "BD 2200+", "BD3000+"]
B = ["BD 1600+", "BD 2100+", "BD 2500+", "BD 3500+"]
C = ["BD330+", "BD 400+", "BD 550+", "BD 850+", "BD 1100+"]
D=  ["BD 480", "BD 630", "BD 970", "BD 1260"]
E=  ["PE 1020", "PE 1330", "PE 2016", "PE 2670", "PE 3390", "PE 1020 S", "PE 1330 S", "PE 2060 S", "PE 2670 S", "PE 3390 S"]
F=  ["BD 1600"]
G=  ["BD 360+", "BD 480+", "BD 630+", "BD 970+", "BD 1260+"]
H=  ["PB 760 HE", "PB 1000 HE", "PB 1350 HE", "PB 2050 HE", "PB 2650 HE"]
I=  ["PH 1150 HE", "PH 1800 HE", "PH 2350 HE", "PH 2950 HE", "PH 700 HE", "PH 850 HE"]
J=  ["CD 1260+", "CD 1600+", "CD 360+", "CD 480+","CD 630+", "CD 970+"]
K=  ["PH 1020 HE", "PH 1330 HE", "PH 2060 HE", "PH 2670 HE", "PH 3390 HE", "PH760 HE"]
L=  ["XD 550+", "XD 850+", "XD1100+"]
M=  ["XD 1400+", "XD 1800+", "XD 2200+"]
N=  ["XD 3000+", "XD 3600+"]


# Define folder paths
folders = {
    "A": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf1",
    "B": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf2",
    "C": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf3",
    "D": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf4",
    "E": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf5",
    "F": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf6",
    "G": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf7",
    "H": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf8",
    "I": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf9",
    "J": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf10",
    "K": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf11",
    "L": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf12",
    "M": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf13",
    "N": "C:\\Users\\parth1729\\Desktop\\AIB\\pdf_Data\\pdf14",
}


def find_machine_folder(query):
    query = query.lower()
    for machine in A:
        if machine.lower() in query:
            return "A"
    for machine in B:
        if machine.lower() in query:
            return "B"
    for machine in C:
        if machine.lower() in query:
            return "C"
    for machine in D:
        if machine.lower() in query:
            return "D"
    for machine in E:
        if machine.lower() in query:
            return "E"
    for machine in F:
        if machine.lower() in query:
            return "F"
    for machine in G:
        if machine.lower() in query:
            return "G"
    for machine in H:
        if machine.lower() in query:
            return "H"
    for machine in I:
        if machine.lower() in query:
            return "I"
    for machine in J:
        if machine.lower() in query:
            return "J"
    for machine in K:
        if machine.lower() in query:
            return "K"
    for machine in L:
        if machine.lower() in query:
            return "L"
    for machine in M:
        if machine.lower() in query:
            return "M"
    for machine in N:
        if machine.lower() in query:
            return "N"
    return None

def search_html_files(folder_path, file_name):
    results = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # if file == file_name:
            if file.lower() == file_name.lower(): # lower case convert promt this  line add
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    # results.append((file_path, soup.get_text()))
                    results.append((file_path, soup.prettify()))
    return results

# old API
# def user_requirements_data(prompt):
#     try:
#         #client = Groq(api_key="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")
#         client = Groq(api_key="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")
#         response = client.chat.completions.create(
#                 messages=[
#                     {"role": "system", "content": "You are a helpful AI assistant. You are trained on world data, you will respond as per user requirements"},
#                     {"role": "user", "content": prompt},
#                             ],
#                 model="Llama3-8b-8192",)
        
#         Responce = response.choices[0].message.content
#         return Responce
#     except Exception as e:
#         print("Plsease check the section extraction function, this is the error:",e)

# new updated API
def user_requirements_data(prompt):
    try:
        client = Groq(api_key="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")
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. You are trained on world data, you will respond as per user requirements"},
                {"role": "user", "content": "{}".format(prompt)},
            ],
            model="Llama3-8b-8192",
        )
        
        response_content = response.choices[0].message.content
        
        # Convert the response to HTML format
        html_response = """
        <html>
        <body>
            <h1>Response from AI</h1>
            <p>{}</p>
        </body>
        </html>
        """.format(response_content.replace('\n\n', '</p><p>').replace('\n', '<br>'))
        
        print(html_response)
        return html_response
    except Exception as e:
        print("Please check the section extraction function, this is the error:", e)




app = Flask(__name__)


# ------------Ankush ADD code here--------------
# @app.route('/generate_chapters/', methods=['POST'])
# def generate_chapters():
#     try:

#         #convert_pdfs_to_text(pdf_folder_path, folder_path)
#         document = load_documents_from_directory(folder_path)
#         text_documents = split_text_documents(document)
#         vectordb = create_vector_database(text_documents, persist_directory)
#         unique_docs = set()
#         docs_by_source = {}
#         output = ""
#         print("Request received:", request.json)
#         if request.method == 'POST':
#             query = request.json.get('query')
#             print("Query:", query)
            
#             machines = ["BD330+", "BD 400+", "BD 550+", "BD 850+",
#                         "BD 1100+", "BD 1600+", "BD 2100+", "BD 2500+",
#                         "BD 3500+","BD 1400+", "BD 1800+", "BD 2200+", "BD3000+",
#                         "BD 480", "BD 630", "BD 970", "BD 1260",
#                         "PE 1020", "PE 1330", "PE 2016", "PE 2670", "PE 3390", "PE 1020 S",
#                         "PE 1330 S", "PE 2060 S", "PE 2670 S", "PE 3390 S",
#                         "BD 1600","BD 360+", "BD 480+", "BD 630+", "BD 970+", "BD 1260+",
#                         "PB 760 HE", "PB 1000 HE", "PB 1350 HE", "PB 2050 HE","PB 2650 HE",
#                         "PH 1150 HE", "PH 1800 HE", "PH 2350 HE", "PH 2950 HE","PH 700 HE", "PH 850 HE",
#                         "CD 1260+", "CD 1600+", "CD 360+", "CD 480+", "CD 630+","CD 970+",
#                         "PH 1020 HE", "PH 1330 HE", "PH 2060 HE", "PH 2670 HE","PH 3390 HE", "PH760 HE",
#                         "XD 550+", "XD 850+", "XD1100+","XD 1400+", "XD 1800+", "XD 2200+","XD 3000+", "XD 3600+"
#                         ]

#             retriever = vectordb.as_retriever(search_kwargs={"k":4})
#             if any(machine in query for machine in machines):
#                 docs = retriever.get_relevant_documents(query)
#                 for doc in docs:
#                     file_name = doc.metadata["source"]  
#                     if file_name not in docs_by_source:
#                         docs_by_source[file_name] = []
#                     docs_by_source[file_name].append(doc.page_content)

#                 for file_name, contents in docs_by_source.items():
#                     output += f"\nSource File: {file_name}\n"  
#                     for content in contents:
#                         output += f"Document Content:\n{content}\n"

#                 print(output)
#             else:
#                 return jsonify({'response': "AIB: I don't have knowledge about this machine."})

#                 #print("AIB: I don't have knowledge about this machine.")

#             output= [line for line in output.split("\n") if not line.strip().startswith("Document Content:")]
#             response = "\n".join(output)
#             chapter_response = response.replace("\\n", "\n").strip("{").strip("}")
#             print(chapter_response)
#             return jsonify({'response': chapter_response})
#         else:           
#             return jsonify({'error': 'Only POST requests are allowed'})
        
#     except Exception as e:
#         print("Plsease check the generate chapter route, this is the error:",e)


@app.route('/generate_chapters/', methods=['POST'])
def generate_chapters():
    try:
        print("Request received:", request.json)
        if request.method == 'POST':
            query = request.json.get('query')
            query = query.lower() # change here for lower case
            print("Query:", query)

            parts = query.split(' for ')
            if len(parts) == 2:
                file_name = parts[0].strip()
                if not file_name.endswith(".html"):
                    file_name += ".html"

                machine_query = parts[1].strip()
                folder_key = find_machine_folder(machine_query)
                if folder_key:
                    folder_path = folders[folder_key]
                    results = search_html_files(folder_path, file_name)
                    if results:
                        for result in results:
                            file_path, file_content1 = result
                            file_content = file_content1.replace('\n', ' ')
                            #print(f"Found '{file_name}' in: {file_path}")
                            #print(f"Content:\n{file_content[:200]}...")  
                        return jsonify({"status": "success", "results": file_content})  
                    else:
                        print(f"No results found for '{file_name}' in folder {folder_key}")
                        #return jsonify({"status": "error", "message": f"No results found for '{file_name}' in folder {folder_key}"})
                        return jsonify({"status": "error", "message": f"No results found this Machine"})
                else:
                    print("sorry, I don't have knowledge.")
                    return jsonify({"status": "error", "message": "No matching machine found in the query."})
            else:
                print("Please write a proper query in the format. Use 'filename for machine_name'.")
                return jsonify({"status": "error", "message": "Please write a proper query in the format. Use 'filename for machine_name'."})
        else:
            return jsonify({'error': 'Request does not contain JSON data.'}), 400            
                
    except Exception as e:
        print("Please check the generate chapter route, this is the error:", e)
        return jsonify({"status": "error", "message": "An error occurred while processing the request."})

@app.route('/generate_specific_book/', methods=['POST'])
def generate_specific_book():
    try:
        if request.method == 'POST':
            data = request.json
            target_file_name = data['target_file_name']
            Chapter = data['Chapter']
            data = request.json
            target_file_name = data.get('target_file_name')
            Chapter = data.get('Chapter')

            data = Chapter.replace("\\n", "\n").strip("{").strip("}")
            pattern = rf"{re.escape(target_file_name)}\n(.*?)(?=\nSource File:|\Z)"
            match = re.search(pattern, data, re.DOTALL)
            if match:
                print(match.group(0).strip()) 
                chapter_response = match.group(0).strip()
                print(chapter_response)
                return jsonify({'response': chapter_response})
            else:
                print(f"Source file '{target_file_name}' not found in the document.")
                return jsonify({'response':f"Source file '{target_file_name}' not found in the document."})
        else:           
            return jsonify({'error': 'Only POST requests are allowed'})
        
    except Exception as e:
        print("Plsease check the generate specific book route, this is the error:",e)



@app.route('/generate_specific_section/', methods=['POST'])
def generate_specific_section():
    try:    
        if request.method == 'POST':
            data = request.json
            section_number = data['section_number']
            target_text = data['target_text']
            data = request.json
            section_number = data.get('section_number')
            target_text = data.get('target_text')
            extracted_section = extract_section(target_text, section_number)

            lines = extracted_section.split("\n")
            filtered_lines = [line for line in lines if "Instruction book" not in line]
            filtered_text = "\n".join(filtered_lines)
            result_text = filtered_text.strip()
            print(result_text)
            return jsonify({'response': result_text})
        
        else:           
            return jsonify({'error': 'Only POST requests are allowed'})
        
    except Exception as e:
        print("Plsease check the generate specific section route, this is the error:",e)   


# @app.route('/translate', methods=['POST'])
# def translate_text():
#     try:
#         if request.method == 'POST':
#             data = request.json
#             language = data['language']
#             text = data['text']
#             data = request.json
#             language = data.get('language')
#             text = data.get('text')
#             print(text)

#             if not language or not text:
#                 return jsonify({'error': 'Missing language or text in request'}), 400

#             if language == 'spanish':
#                 translation = TranslationService.spanish_translation(text)
#                 translation = translation.replace("\n", " ")
#             elif language == 'french':
#                 translation = TranslationService.french_translation(text)
#                 translation = translation.replace("\n", " ")
#             elif language == 'german':
#                 translation = TranslationService.german_translation(text)
#                 translation = translation.replace("\n", " ")
#             else:
#                 return jsonify({'error': 'Unsupported language'}), 400

#             return jsonify({'translation': translation})
#     except Exception as e:
#         print("Plsease check the Transaltion route, this is the error:",e)

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        if request.method == 'POST':
            data = request.json
            language = data.get('language')
            text = data.get('text')

            if not language or not text:
                return jsonify({'error': 'Missing language or text in request'}), 400

            if language == 'spanish':
                translation = TranslationService.spanish_translation(text)
                translation = translation.replace("\n", " ")
            elif language == 'french':
                translation = TranslationService.french_translation(text)
                translation = translation.replace("\n", " ")
            elif language == 'german':
                translation = TranslationService.german_translation(text)
                translation = translation.replace("\n", " ")
            elif language == 'dutch':
                translation = TranslationService.dutch_translation(text)
                translation = translation.replace("\n", " ")
            else:
                return jsonify({'error': 'Unsupported language'}), 400

            return jsonify({'translation': translation})
    except Exception as e:
        print("Please check the Translation route, this is the error:", e)
        return jsonify({'error': 'Internal server error'}), 500

# @app.route('/review', methods=['POST'])
# def review_manual():
#     try:
#         if request.method == 'POST':
#             response = request.json.get('response')
#             print("Response:", response)
#             Review = Review_Manual(response)
#             return jsonify({'response': Review})
#     except Exception as e:
#         print("Plsease check the Review route, this is the error",e)

@app.route('/review', methods=['POST'])
def review_manual():
    try:
        if request.method == 'POST':
            response = request.json.get('response')
            print("Response:", response)
            # Remove newlines from the response
            cleaned_response = response.replace('\n', ' ')
            Review = Review_Manual(cleaned_response)
            return jsonify({'response': Review})
    except Exception as e:
        print("Please check the Review route, this is the error", e)

def Review_Manual(response):
    # This is a placeholder function, replace it with your actual logic
    return f"Processed Review: {response}"



# old api
# @app.route('/user_requirements', methods=['POST'])
# def user_requirements():
#         try:
#             if request.method == 'POST':
#                 data = request.json
#                 #response = data['response']
#                 prompt = data['prompt']
#                 #data = request.json
#                 #response = data.get('response')
#                 prompt = data.get('prompt')
#                 #print("Response:", response)
#                 print("prompt", prompt)
#                 Generated_data = user_requirements_data(prompt)
#                 Generated_data = Generated_data.replace("\n", "")

#             return jsonify({'response': Generated_data})

                        
#         except Exception as e:
#                 print("Plsease check the Review route, this is the error",e)
# updated API
from flask import Flask, request, Response
@app.route('/user_requirements', methods=['POST'])
def user_requirements():
    try:
        if request.method == 'POST':
            data = request.json
            prompt = data.get('prompt', '')
            
            # Get the HTML response from the user_requirements_data function
            generated_html = user_requirements_data(prompt)
            
            # Return the HTML response
            return Response(generated_html, content_type='text/html')
        
    except Exception as e:
        print("Please check the Review route, this is the error:", e)
        return Response(f"<html><body><h1>Error</h1><p>{e}</p></body></html>", content_type='text/html')
#####################################################################################    

import json
@app.route('/save_data', methods=['POST'])
def save_json():
    if request.method == 'POST':
        Response = request.get_json("response")
        print(Response)
        save_dir = 'BOOK'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filename = 'Data.json'
        file_path = os.path.join(save_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(Response, f)

        return jsonify({'message': 'JSON data saved successfully.'}), 200
    else:
        return jsonify({'error': 'Request does not contain JSON data.'}), 400

######################################################################################
# @app.route('/knowledge_based/', methods=['POST'])
# def knowledge_based():
#     try:
#         #convert_pdfs_to_text(pdf_folder_path, folder_path)
#         document = load_documents_from_directory(folder_path)
#         text_documents = split_text_documents(document)
#         vectordb = create_vector_database(text_documents, persist_directory)
#         unique_docs = set()
#         docs_by_source = {}
#         output = ""
#         print("Request received:", request.json)
#         if request.method == 'POST':
#             query = request.json.get('query')
#             print("Query:", query)
#             docs = retrieve_relevant_documents(query, vectordb)
#             for doc in docs:
#                 file_name = doc.metadata["source"]
#                 if file_name not in docs_by_source:
#                     docs_by_source[file_name] = []
#                 docs_by_source[file_name].append(doc.page_content)
#             for file_name, contents in docs_by_source.items():
#                 output += f"\nSource File: {file_name}\n"  # Start on a new line
#                 for content in contents:
#                     output += f"Document Content:\n{content}\n"
#                     unique_docs.add(content)
#             output= [line for line in output.split("\n") if not line.strip().startswith("Document Content:")]
#             response = "\n".join(output)
#             chapter_response = response.replace("\\n", "\n").strip("{").strip("}")
#             print(chapter_response)
#             return jsonify({'response': chapter_response})
#         else:
#             return jsonify({'error': 'Only POST requests are allowed'})
#     except Exception as e:
#         print("Plsease check the generate chapter route, this is the error:",e)

##################################################################################################
#@app.route('/knowledge_based/', methods=['POST'])
# def knowledge_based():
#     try:
#         # Convert PDFs to text (commented out, assuming it's done elsewhere)
#         # convert_pdfs_to_text(pdf_folder_path, folder_path)
#         document = load_documents_from_directory(folder_path)
#         text_documents = split_text_documents(document)
#         vectordb = create_vector_database(text_documents, persist_directory)
#         unique_docs = set()
#         docs_by_source = {}
#         output = ""
#         print("Request received:", request.json)
        
#         if request.method == 'POST':
#             query = request.json.get('query')
#             print("Query:", query)
#             docs = retrieve_relevant_documents(query, vectordb)
#             for doc in docs:
#                 file_name = doc.metadata["source"]
#                 if file_name not in docs_by_source:
#                     docs_by_source[file_name] = []
#                 docs_by_source[file_name].append(doc.page_content)
            
#             # Create HTML output
#             output += "<html><body>"
#             for file_name, contents in docs_by_source.items():
#                 output += f"<h2>Source File: {file_name}</h2>"
#                 for content in contents:
#                     output += f"<p>{content}</p>"
#                     unique_docs.add(content)
#             output += "</body></html>"
            
#             # Clean up the output
#             output_lines = [line for line in output.split("\n") if not line.strip().startswith("Document Content:")]
#             response = "\n".join(output_lines)
#             chapter_response = response.replace("\\n", "\n").strip("{").strip("}")
#             print(chapter_response)
#             return chapter_response, 200, {'Content-Type': 'text/html'}
#         else:
#             return jsonify({'error': 'Only POST requests are allowed'}), 405
#     except Exception as e:
#         print("Please check the generate chapter route, this is the error:", e)
#         return jsonify({'error': str(e)}), 500
###################################################################
@app.route('/knowledge_based/', methods=['POST'])
def knowledge_based():
    try:
        # Assuming PDF to text conversion and loading documents is done elsewhere
        document = load_documents_from_directory(folder_path)
        text_documents = split_text_documents(document)
        vectordb = create_vector_database(text_documents, persist_directory)
        docs_by_source = {}
        output = ""

        if request.method == 'POST':
            print("Request received:", request.json)
            query = request.json.get('query')
            print("Query:", query)
            docs = retrieve_relevant_documents(query, vectordb)
            for doc in docs:
                file_name = doc.metadata["source"]
                if file_name not in docs_by_source:
                    docs_by_source[file_name] = []
                docs_by_source[file_name].append(doc.page_content)
            
            # Create HTML output
            output += "<html><body>"
            for file_name, contents in docs_by_source.items():
                output += f"<h2>Source File: {file_name}</h2>"
                for content in contents:
                    # Replace newlines with HTML line breaks
                    formatted_content = content.replace('\n', '<br>')
                    output += f"<p>{formatted_content}</p>"
            output += "</body></html>"
            
            print(output)
            return output, 200, {'Content-Type': 'text/html'}
        else:
            return jsonify({'error': 'Only POST requests are allowed'}), 405
    except Exception as e:
        print("Please check the generate chapter route, this is the error:", e)
        return jsonify({'error': str(e)}), 500


################################################################################################

if __name__ == '__main__':
    app.run(debug=False)
    # app.run(debug=True,host="20.115.48.0")

