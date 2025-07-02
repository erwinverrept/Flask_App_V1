import csv

def output_to_csv(exif_data, kleuren_data, output_path):
    """
    Exporteert EXIF-informatie en kleureninformatie naar een CSV-bestand.
    Elke rij bevat de EXIF-data (zelfde voor alle rijen) en één kleur.
    """
    # Bepaal de EXIF-kolommen
    exif_keys = ['Make', 'Model', 'DateTimeOriginal', 'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength']
    # Bepaal de kleur-kolommen
    kleur_keys = ['rgb', 'hsl', 'percentage', 'pixelFraction', 'score']

    # Maak de header
    header = exif_keys + kleur_keys

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for kleur in kleuren_data:
            row = {key: exif_data.get(key, '') for key in exif_keys}
            row.update({key: kleur.get(key, '') for key in kleur_keys})
            writer.writerow(row)