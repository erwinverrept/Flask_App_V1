import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
from werkzeug.utils import secure_filename
from google.cloud import vision
from PIL import Image
from PIL.ExifTags import TAGS
from .HSL import rgb_to_hsl
import io
from .output_to_csv import output_to_csv
from .jpeg_to_png import convert_and_remove_background

analyse_bp = Blueprint('analyse', __name__, template_folder='templates')

# Configureer een map om uploads op te slaan
# The original UPLOAD_FOLDER was hardcoded to a path for a different user ('erwin').
# This caused a PermissionError when running as the 'pi' user.
# We'll change it to a path relative to the current file's location.
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
# Zorg ervoor dat de 'uploads' map bestaat
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- NIEUWE CODE VOOR GOOGLE CLOUD CREDENTIALS EN INITIALISATIE VAN DE CLIENT ---
# Check if credentials file exists and is set in the environment variable

credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not credentials_path or not os.path.exists(credentials_path):
    raise Exception("Google Cloud credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable.")

# Initialize the client
vision_client = vision.ImageAnnotatorClient()

# --- De functie analyseer_afbeelding blijft ongewijzigd ---
def analyseer_afbeelding(image_path):
    """
    Analyseert een afbeelding met Google Vision API voor kleuren en een webbeschrijving.
    """
    try:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        features = [
            {'type_': vision.Feature.Type.IMAGE_PROPERTIES},
            {'type_': vision.Feature.Type.WEB_DETECTION},
        ]
        request = vision.AnnotateImageRequest(image=image, features=features)
        response = vision_client.annotate_image(request=request)

        props = response.image_properties_annotation
        kleuren_data = []
        for color_info in props.dominant_colors.colors:
            percentage = round(color_info.pixel_fraction * 100, 2)
            r = int(color_info.color.red)
            g = int(color_info.color.green)
            b = int(color_info.color.blue)
            hsl = rgb_to_hsl(r, g, b)  # <-- HSL berekenen
            kleuren_data.append({
                'rgb': f'rgb({r}, {g}, {b})',
                'hsl': hsl,  # <-- toevoegen aan dict
                'percentage': percentage,
                'pixelFraction': color_info.pixel_fraction,
                'score': color_info.score
            })

        web_detection = response.web_detection
        beschrijving = "Geen beschrijving gevonden."
        if web_detection.best_guess_labels:
            beschrijving = web_detection.best_guess_labels[0].label.capitalize()
        elif web_detection.web_entities:
            for entity in web_detection.web_entities:
                if entity.description:
                    beschrijving = entity.description.capitalize()
                    break

        return kleuren_data, beschrijving, None
    except Exception as e:
        print(f"Fout tijdens API-aanroep: {e}")
        return None, None, str(e)
def get_exif_data(image_path):
    """
    Haalt EXIF-informatie op uit een afbeelding.
    """
    try:
        image = Image.open(image_path)
        exif = {}
        
        if hasattr(image, '_getexif') and image._getexif():
            for tag_id, value in image._getexif().items():
                tag = TAGS.get(tag_id, tag_id)
                # Filter alleen relevante EXIF-tags
                if tag in ['DateTimeOriginal', 'Make', 'Model', 'ExposureTime', 
                          'FNumber', 'ISOSpeedRatings', 'FocalLength']:
                    if tag == 'ExposureTime':
                        # Converteer belichtingstijd naar leesbaar formaat
                        value = f"1/{int(1/float(value))} sec" if value < 1 else f"{value} sec"
                    elif tag == 'FNumber':
                        value = f"f/{value}"
                    elif tag == 'FocalLength':
                        value = f"{value}mm"
                    exif[tag] = value
        
        return exif
    except Exception as e:
        print(f"Fout bij het lezen van EXIF data: {e}")
        return {}

@analyse_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Verwerkt de hoofdpagina: toont het uploadformulier en handelt de upload af.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            kleuren, beschrijving, error = analyseer_afbeelding(filepath)
            exif_data = get_exif_data(filepath)
            if error:
                return render_template('analyse.html', error=error)
            return render_template('resultaat.html', kleuren=kleuren, beschrijving=beschrijving, image_name=filename, exif_data=exif_data)
    return render_template('analyse.html')


# --- NIEUWE ROUTE OM AFBEELDINGEN TE TONEN ---
@analyse_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Deze functie levert de opgeslagen afbeelding aan de browser.
    """
    return send_from_directory(UPLOAD_FOLDER, filename)

@analyse_bp.route('/export', methods=['GET', 'POST'])
def export_csv():
    """
    Toont een formulier om een bestandsnaam te kiezen en exporteert de analyse naar CSV.
    """
    # Gebruik de laatst geanalyseerde afbeelding uit de sessie of een globale variabele
    # (voor demo: neem gewoon de laatste upload uit de uploads-map)
    image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    uploads = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(image_exts)]
    if not uploads:
        return redirect(url_for('analyse.index'))
    latest_file = max([os.path.join(UPLOAD_FOLDER, f) for f in uploads], key=os.path.getctime)
    kleuren, beschrijving, _ = analyseer_afbeelding(latest_file)
    exif_data = get_exif_data(latest_file)

    if request.method == 'POST':
        filename = request.form.get('filename', '').strip()
        if not filename:
            return render_template('output.html', error='Geef een bestandsnaam op!')
        if not filename.endswith('.csv'):
            filename += '.csv'
        output_path = os.path.join(UPLOAD_FOLDER, filename)
        output_to_csv(exif_data, kleuren, output_path)
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    return render_template('output.html')

@analyse_bp.route('/kleurwiel')
def kleurwiel():
    """
    Toont het interactieve HSL kleurwiel.
    """
    return render_template('kleurwiel.html')

@analyse_bp.route('/remove_background', methods=['GET', 'POST'])
def remove_background():
    image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    uploaded_images = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(image_exts)]
    
    message = None
    error = None
    original_image_name = None
    processed_image_name = None

    if request.method == 'POST':
        selected_file = request.form.get('image_file')
        if not selected_file:
            error = "Geen afbeelding geselecteerd."
        else:
            original_image_path = os.path.join(UPLOAD_FOLDER, selected_file)
            
            name, ext = os.path.splitext(selected_file)
            output_filename = f"{name}-result.png"
            output_image_path = os.path.join(UPLOAD_FOLDER, output_filename)

            success = convert_and_remove_background(original_image_path, output_image_path)
            
            if success:
                message = f"Achtergrond succesvol verwijderd en opgeslagen als {output_filename}"
                original_image_name = selected_file
                processed_image_name = output_filename
            else:
                error = "Fout bij het verwijderen van de achtergrond. Controleer de API-sleutel en het logboek."

    return render_template('remove_background.html', 
                           uploaded_images=uploaded_images, 
                           message=message, 
                           error=error,
                           original_image_name=original_image_name,
                           processed_image_name=processed_image_name)
