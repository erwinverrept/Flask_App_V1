import os
import requests
from PIL import Image

def convert_and_remove_background(input_jpeg_path, output_png_path):
    """
    Converts a JPEG image to PNG and removes its background using the Remove.bg API.

    Args:
        input_jpeg_path (str): The absolute path to the input JPEG file.
        output_png_path (str): The absolute path where the output PNG file will be saved.

    Returns:
        bool: True if the process was successful, False otherwise.
    """
    api_key = os.getenv("REMOVE_BG_API_KEY")
    if not api_key:
        print("Error: REMOVE_BG_API_KEY environment variable not set.")
        return False

    try:
        # Ensure the input file exists
        if not os.path.exists(input_jpeg_path):
            print(f"Error: Input file not found at {input_jpeg_path}")
            return False

        # Open the image using Pillow to ensure it's a valid image and can be processed
        with Image.open(input_jpeg_path) as img:
            # Convert to RGB if not already (Remove.bg might prefer it, and it handles transparency better for PNG)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to a temporary buffer or file to send to API
            # For simplicity, we'll read the file directly for the API call
            
            print(f"Sending {input_jpeg_path} to Remove.bg API...")
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': open(input_jpeg_path, 'rb')},
                data={'size': 'auto'},
                headers={'X-Api-Key': api_key}
            )
            response.raise_for_status() # Raise an exception for HTTP errors

            with open(output_png_path, 'wb') as out_file:
                out_file.write(response.content)
            
            print(f"Background removed and image saved to {output_png_path}")
            return True

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_jpeg_path}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Remove.bg API: {e}")
        if response and response.status_code == 403:
            print("Check your API key and account limits.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    # Example usage (replace with actual paths and ensure API key is set)
    # input_file = "/home/erwin/app/project/Flask_App/analyse/uploads/topaz_steen.PNG" # Example JPEG/PNG
    # output_file = "/home/erwin/app/project/Flask_App/analyse/uploads/topaz_steen_no_bg.png"
    
    # if convert_and_remove_background(input_file, output_file):
    #     print("Conversion and background removal successful!")
    # else:
    #     print("Conversion and background removal failed.")
    print("This script is intended to be imported as a module.")
    print("To use it, call convert_and_remove_background(input_jpeg_path, output_png_path).")