import json

from pydantic import BaseModel


def invoke_structured(llm, schema: type[BaseModel], prompt: str):
    """
    Invoke a Groq chat model with structured output.

    Some Groq models return valid JSON instead of making the tool call expected by
    function_calling mode. Prefer Groq's structured-output API when available and
    fall back to JSON mode for that case.
    """

    model_name = getattr(llm, "model_name", "")

    if "openai/gpt-oss" in model_name:
        methods = ("json_schema", "json_mode", "function_calling")
    else:
        methods = ("function_calling", "json_mode")

    schema_prompt = (
        f"{prompt}\n\n"
        "Return ONLY valid JSON. Do not include markdown, explanations, or code fences.\n"
        f"The JSON must match this schema:\n{json.dumps(schema.model_json_schema())}"
    )

    last_error = None
    for method in methods:
        try:
            structured_llm = llm.with_structured_output(schema, method=method)
            if method == "json_mode":
                return structured_llm.invoke(schema_prompt)
            return structured_llm.invoke(prompt)
        except Exception as exc:
            last_error = exc

    raise last_error
