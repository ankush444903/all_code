from flask import Flask, request, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from nltk.tokenize import sent_tokenize
from requests.exceptions import RequestException
###############
import nltk

# Download both 'punkt' and 'punkt_tab'
nltk.download('punkt')
nltk.download('punkt_tab')
#################################
app = Flask(__name__)

memory_translations_path = r"C:\Users\DD\Desktop\varahi\Translation with HTML formating\Dutch.xlsx"

def load_memory_translations(file_path):
    try:
        df = pd.read_excel(file_path)
        return dict(zip(df['en'], df['nl']))
    except Exception as e:
        print(f"Error loading translations from Excel: {e}")
        return {}

def normalize_sentence(sentence):
    return re.sub(r'^[•\s]+', '', sentence).strip()

def translate_with_deepl(sentence):
    try:
        url = "https://api-free.deepl.com/v2/translate"
        normalized_sentence = sentence[0].upper() + sentence[1:].lower()
        data = {
            "text": normalized_sentence,
            "source_lang": "EN",
            "target_lang": "NL",
            "auth_key": 'b7d50a17-e614-4437-8c3e-6b593abc569a:fx'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()

        return response.json()['translations'][0]['text']
    except (RequestException, KeyError, IndexError) as e:
        print(f"Error translating sentence: {sentence}")
        print(f"Error details: {e}")
        return f"{sentence} (Translation failed)"

@app.route('/translate', methods=['POST'])
def translate():
    input_data = request.get_json()
    input_html = input_data.get('text', '')
    memory_based_translations = load_memory_translations(memory_translations_path)
    soup = BeautifulSoup(input_html, 'html.parser')

    for element in soup.find_all(text=True):
        text = element.strip()
        if text:
            sentences = sent_tokenize(text)
            translated_sentences = []
            for sentence in sentences:
                normalized_sentence = normalize_sentence(sentence)
                if normalized_sentence in memory_based_translations:
                    translated_sentences.append(memory_based_translations[normalized_sentence])
                else:
                    translated_sentences.append(translate_with_deepl(sentence))
            element.replace_with(' '.join(translated_sentences))

    return jsonify({"translated_html": str(soup)})

if __name__ == '__main__':
    app.run(debug=True)
