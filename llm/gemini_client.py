import os
import google.generativeai as genai
from llm.prompts import COMPREHENSIVE_PROMPT
from PIL import Image
from flask import current_app
import tempfile

def extract_document_data(file):
    print("Starting LLM extraction process...")

    # Configure Gemini API key
    api_key = current_app.config['GEMINI_API_KEY']
    print("Configuring Gemini API key...")
    genai.configure(api_key=api_key)

    # Save the uploaded file to a temporary location for PIL
    print("Saving uploaded file to a temporary location...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.seek(0)
        tmp.write(file.read())
        tmp_path = tmp.name

    print(f"Temporary file saved at: {tmp_path}")

    # Now the file is closed, so we can open it with PIL
    try:
        print("Opening file with PIL...")
        img = Image.open(tmp_path)
        img.load()  # Force loading image data into memory
    except Exception as e:
        print("Error opening file with PIL.")
        os.remove(tmp_path)
        raise ValueError(f"Could not open file as image: {e}")

    # Prepare the model and prompt
    print("Preparing Gemini model and prompt...")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = COMPREHENSIVE_PROMPT

    # Generate content
    print("Sending prompt and image to Gemini...")
    response = model.generate_content([prompt, img])
    print("Gemini response received:")
    print(response.text)
    # Close the image before deleting the file!
    img.close()

    # Clean up temp file
    print("Cleaning up temporary file...")
    os.remove(tmp_path)

    # Try to extract JSON from the response
    print("Extracting JSON from Gemini response...")
    import json, re
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        print("Extraction successful.")
        return json.loads(match.group(0))
    else:
        print("No JSON found in LLM response.")
        raise ValueError("No JSON found in LLM response")