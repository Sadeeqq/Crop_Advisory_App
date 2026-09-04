import os
from dotenv import load_dotenv
from google import genai
from utils.exceptions import GeminiAPIError

load_dotenv()

GEMINI_MODEL = 'gemini-3.6-flash'


class GeminiClient:
    def __init__(self):
        
        self.api_key = os.environ.get('GEMINI_API_KEY')

    def _get_client(self):
        if not self.api_key:
            raise GeminiAPIError('GEMINI_API_KEY is not set. Add it to your .env file (see .env.example).')

        return genai.Client(api_key=self.api_key)

    def generate_advice(self, advisory_data):
        client = self._get_client()
        prompt = self._build_prompt(advisory_data)

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
        except Exception as e:
            
            raise GeminiAPIError(f'Gemini request failed: {e}')

        if not response or not getattr(response, 'text', None):
            raise GeminiAPIError('Gemini returned an empty response')

        return response.text

    def _build_prompt(self, advisory_data):
        return f"""You are a friendly, experienced farming advisor talking directly to a farmer in Nigeria.

Use ONLY the structured data below. Do NOT invent or assume any weather data that is
not provided. If something is missing or says "unavailable", say so plainly instead of
guessing.

Crop: {advisory_data.get('crop_name')}
Location coordinates: ({advisory_data.get('latitude')}, {advisory_data.get('longitude')})

Current conditions: {advisory_data.get('current_conditions')}

Rule-based planting suitability verdict: {advisory_data.get('suitability_verdict')}
Reason for verdict: {advisory_data.get('suitability_reason')}

Recommended planting window: {advisory_data.get('planting_window')}

Irrigation need level: {advisory_data.get('irrigation_level')}
Irrigation reason: {advisory_data.get('irrigation_reason')}

Detected weather threats: {advisory_data.get('threats')}

Common pests for this crop: {advisory_data.get('common_pests')}
Common diseases for this crop: {advisory_data.get('common_diseases')}

Write a short, warm response, like you're speaking to the farmer directly, not writing a
formal report. 3-4 sentences, under about 80 words. No headers, no bullet points, no bold
text, no numbered lists - just plain, natural sentences a person would actually say.
Naturally touch on whether now looks like a good time to plant, how much watering they
should expect to do, and any pest or disease risk worth watching for, but only as much as
fits naturally in a short conversation - don't force in every detail. Use cautious,
everyday language (e.g. "looks like...", "you might want to...", "keep an eye out for...")
since this is guidance based on limited data, not certain fact or professional agricultural
certification.
"""
