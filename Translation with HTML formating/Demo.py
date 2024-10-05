import re
import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from requests.exceptions import RequestException

# Download NLTK data if not already downloaded
nltk.download('punkt')

class TranslationService:

    @staticmethod
    def spanish_translation(input_html):
        memory_translations_path = r"C:\\Users\\lenovo\\Downloads\\modify spanish memory.xlsx"
        try:
            def load_memory_translations(file_path):
                try:
                    df = pd.read_excel(file_path)
                    memory_based_translations = dict(zip(df['en'], df['es']))
                    return memory_based_translations
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
                        "target_lang": "ES",
                        "auth_key": 'b7d50a17-e614-4437-8c3e-6b593abc569a:fx'
                    }
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                    response = requests.post(url, data=data, headers=headers)
                    response.raise_for_status()

                    translation = response.json()['translations'][0]['text']
                    return translation
                except (RequestException, KeyError, IndexError) as e:
                    print(f"Error translating sentence: {sentence}")
                    print(f"Error details: {e}")
                    return f"{sentence} (Translation failed)"

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
                            translated_text = memory_based_translations[normalized_sentence]
                            translated_sentences.append(translated_text)
                        else:
                            translation = translate_with_deepl(sentence)
                            translated_sentences.append(translation)
                    element.replace_with(' '.join(translated_sentences))

            return str(soup)
        except Exception as e:
            print("Please check the translate_html function, this is the error:", e)
            return None

    def german_translation(input_html):
        memory_translations_path = r"C:\\Users\\lenovo\\Desktop\\AIB project\\Translation with HTML formating\\German.xlsx"
        try:
            def load_memory_translations(file_path):
                try:
                    df = pd.read_excel(file_path)
                    memory_based_translations = dict(zip(df['en'], df['de']))
                    return memory_based_translations
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
                        "target_lang": "DE",
                        "auth_key": 'b7d50a17-e614-4437-8c3e-6b593abc569a:fx'
                    }
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                    response = requests.post(url, data=data, headers=headers)
                    response.raise_for_status()

                    translation = response.json()['translations'][0]['text']
                    return translation
                except (RequestException, KeyError, IndexError) as e:
                    print(f"Error translating sentence: {sentence}")
                    print(f"Error details: {e}")
                    return f"{sentence} (Translation failed)"

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
                            translated_text = memory_based_translations[normalized_sentence]
                            translated_sentences.append(translated_text)
                        else:
                            translation = translate_with_deepl(sentence)
                            translated_sentences.append(translation)
                    element.replace_with(' '.join(translated_sentences))

            return str(soup)
        except Exception as e:
            print("Please check the translate_html function, this is the error:", e)
            return None
    def french_translation(input_html):
        memory_translations_path = r"C:\\Users\\lenovo\\Desktop\\AIB project\\Translation with HTML formating\\French.xlsx"
        try:
            def load_memory_translations(file_path):
                try:
                    df = pd.read_excel(file_path)
                    memory_based_translations = dict(zip(df['en'], df['fr']))
                    return memory_based_translations
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
                        "target_lang": "FR",
                        "auth_key": 'b7d50a17-e614-4437-8c3e-6b593abc569a:fx'
                    }
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                    response = requests.post(url, data=data, headers=headers)
                    response.raise_for_status()

                    translation = response.json()['translations'][0]['text']
                    return translation
                except (RequestException, KeyError, IndexError) as e:
                    print(f"Error translating sentence: {sentence}")
                    print(f"Error details: {e}")
                    return f"{sentence} (Translation failed)"

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
                            translated_text = memory_based_translations[normalized_sentence]
                            translated_sentences.append(translated_text)
                        else:
                            translation = translate_with_deepl(sentence)
                            translated_sentences.append(translation)
                    element.replace_with(' '.join(translated_sentences))

            return str(soup)
        except Exception as e:
            print("Please check the translate_html function, this is the error:", e)
            return None
        
    def dutch_translation(input_html):
        memory_translations_path = r"C:\\Users\\lenovo\\Desktop\\AIB project\\Translation with HTML formating\\French.xlsx"
        try:
            def load_memory_translations(file_path):
                try:
                    df = pd.read_excel(file_path)
                    memory_based_translations = dict(zip(df['en'], df['nl']))
                    return memory_based_translations
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

                    translation = response.json()['translations'][0]['text']
                    return translation
                except (RequestException, KeyError, IndexError) as e:
                    print(f"Error translating sentence: {sentence}")
                    print(f"Error details: {e}")
                    return f"{sentence} (Translation failed)"

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
                            translated_text = memory_based_translations[normalized_sentence]
                            translated_sentences.append(translated_text)
                        else:
                            translation = translate_with_deepl(sentence)
                            translated_sentences.append(translation)
                    element.replace_with(' '.join(translated_sentences))

            return str(soup)
        except Exception as e:
            print("Please check the translate_html function, this is the error:", e)
            return None