import json
from typing import Any

import httpx

from app.core.config import settings


class AIError(Exception):
    pass


class AIClient:
    def __init__(self) -> None:
        if not settings.ai_api_key:
            raise AIError("AI_API_KEY is not configured.")

        if not settings.ai_base_url:
            raise AIError("AI_BASE_URL is not configured.")

        if not settings.ai_model:
            raise AIError("AI_MODEL is not configured.")

        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.ai_model

        self.headers = {
            "Authorization": (
                f"Bearer {settings.ai_api_key}"
            ),
            "Content-Type": "application/json",
        }

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        try:
            async with httpx.AsyncClient(
                timeout=90
            ) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )

        except httpx.HTTPError as exc:
            raise AIError(
                f"AI request failed: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise AIError(
                f"AI provider returned "
                f"{response.status_code}: "
                f"{response.text[:1000]}"
            )

        try:
            data = response.json()
        except Exception as exc:
            raise AIError(
                "AI provider returned invalid JSON."
            ) from exc

        try:
            content = data["choices"][0][
                "message"
            ]["content"]
        except (
            KeyError,
            IndexError,
            TypeError,
        ) as exc:
            raise AIError(
                "AI response did not contain "
                "choices[0].message.content."
            ) from exc

        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )

        if not isinstance(content, str):
            raise AIError(
                "AI content was not a string."
            )

        content = content.strip()

        content = self._remove_code_fences(
            content
        )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIError(
                "AI returned invalid JSON:\n"
                + content[:2000]
            ) from exc

        if not isinstance(parsed, dict):
            raise AIError(
                "AI JSON response must be an object."
            )

        return parsed

    @staticmethod
    def _remove_code_fences(
        content: str,
    ) -> str:
        if content.startswith("```"):
            lines = content.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            return "\n".join(lines).strip()

        return content