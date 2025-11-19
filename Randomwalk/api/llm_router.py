import os
from litellm import completion

def call_llm(model_name: str, system_prompt: str, user_prompt: str) -> str:
    """
    Unified LLM caller.
    ...
    """
    # *** CRITICAL FIX: Explicitly pass the Google API Key ***
    # We retrieve the key from the environment variable GOOGLE_API_KEY
    # This prevents confusion with other cached keys (like the invalid OpenAI key).
    
    # Set the key source based on the model being called (assuming Gemini models use GOOGLE_API_KEY)
    if "gemini" in model_name:
        api_key_to_use = os.getenv("GOOGLE_API_KEY")
        # For litellm to connect to Google API, it checks GOOGLE_API_KEY, 
        # or we pass it directly via the 'api_key' parameter.
    else:
        # Fallback for other models if needed, typically litellm handles this
        api_key_to_use = None
    
    # Ensure the Google API Key is available
    if "gemini" in model_name and not api_key_to_use:
        raise ValueError("GOOGLE_API_KEY environment variable is not set. Cannot call Gemini model.")

    response = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        # Pass the key directly as a parameter
        api_key=api_key_to_use, 
    )
    return response["choices"][0]["message"]["content"]
