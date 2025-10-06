from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import google.generativeai as genai
from .config import get_gemini_api_key, validate_required_config


def home(request):
    """Render the home page with the prompt interface."""
    # Check if required configuration is present
    missing_config = validate_required_config()
    if missing_config:
        return render(request, 'django_app/error.html', {
            'error': f'Missing required configuration: {", ".join(missing_config)}',
            'missing_config': missing_config
        })

    return render(request, 'django_app/home.html')


@csrf_exempt
@require_http_methods(["POST"])
def chat_with_llm(request):
    """Handle the LLM chat request."""
    try:
        # Parse the JSON request
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)

        # Check if API key is configured
        api_key = get_gemini_api_key()
        if not api_key:
            return JsonResponse({'error': 'Gemini API key not configured'}, status=500)

        # Configure and use Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Generate response
        response = model.generate_content(prompt)

        return JsonResponse({
            'response': response.text,
            'success': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error generating response: {str(e)}'}, status=500)
