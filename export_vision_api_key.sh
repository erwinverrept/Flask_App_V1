# This script exports the GOOGLE_APPLICATION_CREDENTIALS environment variable.
# Replace /path/to/your/key.json with the actual path to your Google Cloud service account key file.
# The previous path was incorrect, leading to a "File not found" error.
# It needs to be the full, absolute path to the key file, respecting case-sensitivity.
# Since your project is in /home/pi/Flask_App_V1, the correct path is:
export GOOGLE_APPLICATION_CREDENTIALS=/home/pi/FLASK_APP_V1/wordpress-vision-api-v2.json

echo "GOOGLE_APPLICATION_CREDENTIALS environment variable set."
