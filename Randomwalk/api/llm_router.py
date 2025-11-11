import os
from litellm import completion

def call_llm(model_name: str, system_prompt: str, user_prompt: str) -> str:
    """
    Unified LLM caller.
    Supported examples:
      - "gpt-4o" / "gpt-5" (via OPENAI_API_KEY)
      - "claude-3-5-sonnet" (via ANTHROPIC_API_KEY)
      - "gemini-1.5-pro" (via GOOGLE_API_KEY)
    Make sure the corresponding API keys are set in the environment.
    """
    response = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"]

