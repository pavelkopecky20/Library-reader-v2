import io
import os
import re
from google.cloud import vision
from dotenv import load_dotenv
from openai import OpenAI
import json

# Nastavíme proměnnou prostředí k API klíči
load_dotenv()
# image_path = r"C:\Users\m000xz009726\OneDrive\Programování\Library_reader\library_reader\kniha3.jpg"        # jen testovací, později zrušit

# Debugging environmentální proměnné pro Google Cloud Vision API Credentials
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS is not set.")
elif not os.path.exists(credentials_path):
    print(f"❌ File not found: {credentials_path}")
else:
    print(f"✅ Credentials file found: {credentials_path}")
    
# Debugging environment variable for OpenAI API key
_openai_api_key = os.getenv("OPENAI_API_KEY")
if not _openai_api_key:
    print("❌ OPENAI_API_KEY is not set.")
else:
    print("✅ OPENAI_API_KEY is set.")

openai_client = OpenAI(api_key=_openai_api_key)    
    
       
def detect_text_from_file(image):
    client = vision.ImageAnnotatorClient()

    if hasattr(image, 'save'):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        content = image_bytes.getvalue()
    elif isinstance(image, str):
        with io.open(image, 'rb') as file:
            content = file.read()
    else:
        raise ValueError("Neplatný typ vstupu – očekáván obrázek nebo cesta k souboru.")

    response = client.text_detection(image=vision.Image(content=content))

    if response.error.message:
        raise RuntimeError(f"Google Vision API chyba: {response.error.message}")

    texts = response.text_annotations
    if not texts:
        raise RuntimeError("Na obrázku nebyl rozpoznán žádný text.")

    return texts[0].description


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # - původní, změnilo se knihovna import openai
MOCK_MODE = False # Přepínač: True = testovací režim bez volání API
# image_path = r"C:\Users\m000xz009726\OneDrive\Programování\Library_reader\library_reader\kniha3.jpg"  - # uživatel nahraje jpg přes formulář, takže se nepoužívá. Ale funguje

# PROMPT pro OpenAI (co se má dít)
prompt_system = (
    "You are an expert in Czech and world literature. "
    "You will be given a raw OCR-like text with book titles and author names. "
    "Be very careful: sometimes the author's name and book title are on the same line without a newline, "
    "and sometimes they are split over multiple lines. "
    "Each book must have exactly one author. An author always has a first name and a last name; "
    "some names may contain multiple parts. "
    "Your task is to extract all books and their authors from the text. "
    "Return the result strictly as a JSON array of objects with the keys 'title' and 'author'. "
    "Do not include explanations or extra text. "
    "Capitalize names and titles according to the rules for titles and names."
    "If you are unsure of the author or title, don't make it up. Use 'Unknown' instead."
    "Output only valid JSON, for example:\n"
    "[\n"
    "  {\"title\": \"1984\", \"author\": \"George Orwell\"},\n"
    "  {\"title\": \"Šikmý kostel, třetí díl\", \"author\": \"Karin Lednická\"},\n"
    "  {\"title\": \"Sport je bolest\", \"author\": \"Michal Novotný\"},\n"
    "  {\"title\": \"Zimní moře\", \"author\": \"Susanna Kearsleyová\"}\n"
    "  {\"title\": \"Žena, kterou jsem byla\", \"author\": \"Kerry Fisherová\"}\n"
    "  {\"title\": \"Ateliér Rosen\", \"author\": \"Anne Jacobsová\"}\n"
    "  {\"title\": \"Hluboká modř moře\", \"author\": \"Marie Lamballe\"}\n"   
    "]" )

def get_books_and_authors(text): 
    # ===== MOCK MODE ===== - jen testovací, šetří se tokeny
    if MOCK_MODE:
        print("🧪 MOCK_MODE aktivní – volání API se simuluje.")
        response_data =[
                {"title": "Nesnesitelná lehkost bytí", "author": "Milan Kundera"},
                {"title": "1984", "author": "George Orwell"},
                {"title": "Harry Potter a Kámen mudrců", "author": "J.K. Rowlingová"}      ]

    # ===== REÁLNÉ API VOLÁNÍ =====
    else:
        try:
            print("🔄 Posílám dotaz na OpenAI...")
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": text}
                ],
                temperature=0.2
            )
            assistent_response = response.choices[0].message.content
            print("✅ Odpověď z OpenAI:")
            print(assistent_response)

            # GPT někdy obalí JSON do markdown bloku ```json ... ```
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", assistent_response.strip(), flags=re.MULTILINE)
            response_data = json.loads(cleaned)
            return(response_data)
        
        except Exception as e:
            print("❌ Chyba při volání OpenAI API:")
            print(e)
            response_data = []
            
    return(response_data)

    # # ===== VÝSTUP =====              # PAK PŘEPÍŠU DO CYKLU V ŠABLONĚ
    # print("\n📚 Rozpoznané knihy:")
    # for book in response_data:
    #     print(f" {book['title']} - {book['author']}")


# get_books_and_authors(image_path) VOLÁ SE V APP.PY