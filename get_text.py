import io
import os
from google.cloud import vision
from dotenv import load_dotenv
import openai
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
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("❌ OPENAI_API_KEY is not set.")
else:
    print("✅ OPENAI_API_KEY is set.")    
    
       
def detect_text_from_file(image):
    try:
        client = vision.ImageAnnotatorClient()

        # Pokud je to objekt PIL.Image (např. z Pillow), převedeme ho do bytes
        if hasattr(image, 'save'):
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='JPEG')  # nebo 'PNG', podle formátu
            content = image_bytes.getvalue()
        elif isinstance(image, str):
            # Jinak očekáváme cestu k souboru
            with io.open(image, 'rb') as file:
                content = file.read()
        else:
            raise ValueError("Neplatný typ vstupu – očekáván obrázek nebo cesta k souboru.")

        vision_image = vision.Image(content=content)
        response = client.text_detection(image=vision_image)
        texts = response.text_annotations

        if texts:
            return texts[0].description
        else:
            return "Nebyly rozpoznány žádné texty."
    except Exception as e:
        print(f"❌ Error in Vision API: {e}")
        return "Error in Vision API"


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
            response = openai.ChatCompletion.create(
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

            response_data = json.loads(assistent_response)   # s tímto budeme dále pracovat - např do db !!!
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