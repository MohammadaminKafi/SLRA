import requests
from together import Together
from django.conf import settings
from . import exceptions

from slra.models import LLMModel, LLMProvider


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def call_ollama(model_name: str, prompt: str, stream: bool = False) -> str:
    """
    Calls the local Ollama endpoint using the specified model_name
    and returns the final text response.
    """
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream
    }

    try:
        response = requests.post(DEFAULT_OLLAMA_URL, json=payload, stream=stream)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.LLMError(f"Ollama request failed: {e}")

    # If streaming, you'd read chunks. For now, let's assume we wait for the full content:
    if stream:
        content = []
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                content.append(chunk)
        return "".join(content)
    else:
        # Non-streaming: parse JSON or plain text
        try:
            data = response.json()
            # The actual Ollama response schema might differ; adapt as needed:
            return data.get('generated_text', '')
        except ValueError:
            return response.text or ''


def call_together_ai(model_name: str, prompt: str) -> str:
    """
    Example integration with together.ai's Python SDK.
    Assumes a global or environment-based API key is set.
    """
    client = Together()  # Typically uses environment variable: TOGETHER_API_KEY
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    # The response structure may differ; adapt as needed:
    content = response.choices[0].message.content
    return content or ''


def get_llm_response(llm_model: LLMModel, user_prompt: str, stream: bool = False) -> str:
    """
    Main entry point to call a specific LLMModel.
    - llm_model: instance of LLMModel specifying provider, model_name, usage_method, etc.
    - user_prompt: the text to send to the LLM
    - Returns the LLM’s generated text.
    """
    provider_name = llm_model.provider.name.lower()
    model_name = llm_model.model_name

    # Decide which function to call based on the provider
    if 'ollama' in provider_name:
        full_model_name = f"{model_name}"
        if llm_model.version:
            full_model_name += f":{llm_model.version}"
        return call_ollama(full_model_name, user_prompt, stream=stream)

    elif 'together' in provider_name:
        # E.g., "deepseek-ai/DeepSeek-V3"
        full_model_name = model_name
        if llm_model.version:
            # If the version is relevant for together.ai
            full_model_name += f":{llm_model.version}"
        return call_together_ai(full_model_name, user_prompt)

    # Add more conditions for other providers (OpenAI, etc.)

    raise exceptions.LLMError(f"Provider '{llm_model.provider.name}' not supported yet.")
