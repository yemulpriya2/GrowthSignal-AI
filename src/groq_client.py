import json
from groq import Groq

class GroqService:
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model



    def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=6000
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("The model returned an empty response.")
        return content.strip()


    

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict | list:
        raw = self.complete(
            system_prompt + "\nReturn ONLY valid JSON. Do not wrap it in markdown fences.",
            user_prompt,
            temperature=0.1
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start_obj, end_obj = raw.find("{"), raw.rfind("}")
            start_arr, end_arr = raw.find("["), raw.rfind("]")
            if start_arr >= 0 and end_arr > start_arr and (start_obj < 0 or start_arr < start_obj):
                return json.loads(raw[start_arr:end_arr+1])
            if start_obj >= 0 and end_obj > start_obj:
                return json.loads(raw[start_obj:end_obj+1])
            raise ValueError("The AI response was not valid JSON. Please retry.")
