import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from app.core.config import settings


class TrendsError(Exception):
    pass


COUNTRIES = {
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
}


class GoogleTrendsService:
    def __init__(self) -> None:
        self.worker = (
            Path(__file__).resolve()
            .parents[2]
            / "trends_worker"
            / "trends.mjs"
        )

    async def get_country_topics(
        self,
        country: str,
        category: str,
        hours: int = 24,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._run_worker,
            country,
            category,
            hours,
            limit,
        )

    def _get_node_command(self) -> str:
        command = getattr(settings, "node_command", None)

        if command:
            return str(command)

        command = os.getenv("NODE_COMMAND")

        if command:
            return command

        return "node"

    def _run_worker(
        self,
        country: str,
        category: str,
        hours: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        if not self.worker.exists():
            raise TrendsError(
                f"Trend worker not found: {self.worker}"
            )

        node_command = self._get_node_command()

        command = [
            node_command,
            str(self.worker),
            "--geo",
            country,
            "--category",
            category,
            "--hours",
            str(hours),
            "--limit",
            str(limit),
        ]

        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.worker.parent),
            )

        except FileNotFoundError as exc:
            raise TrendsError(
                f"Node.js was not found using command '{node_command}'. "
                "Install Node.js and make sure 'node' is available "
                "in the backend process PATH."
            ) from exc

        except subprocess.TimeoutExpired as exc:
            raise TrendsError(
                "Google Trends request timed out after 60 seconds."
            ) from exc

        except Exception as exc:
            raise TrendsError(
                f"Unable to execute Google Trends worker: {exc}"
            ) from exc

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode != 0:
            error_text = (
                stderr
                or stdout
                or f"Google Trends worker exited with code {process.returncode}."
            )

            lines = error_text.splitlines()

            if lines:
                last_line = lines[-1]

                try:
                    parsed_error = json.loads(last_line)

                    if isinstance(parsed_error, dict):
                        error_text = parsed_error.get(
                            "error",
                            parsed_error.get(
                                "message",
                                error_text,
                            ),
                        )
                except Exception:
                    pass

            raise TrendsError(error_text)

        if not stdout:
            raise TrendsError(
                "Google Trends worker returned no data."
            )

        try:
            data = json.loads(stdout)

        except json.JSONDecodeError as exc:
            raise TrendsError(
                "Invalid JSON returned by Google Trends worker: "
                f"{stdout[:500]}"
            ) from exc

        if not isinstance(data, dict):
            raise TrendsError(
                "Google Trends worker returned an invalid response."
            )

        if not data.get("success"):
            raise TrendsError(
                str(
                    data.get(
                        "error",
                        "Google Trends returned an error.",
                    )
                )
            )

        results: list[dict[str, Any]] = []

        items = data.get("items", [])

        if not isinstance(items, list):
            raise TrendsError(
                "Google Trends worker returned invalid items data."
            )

        for item in items:
            if not isinstance(item, dict):
                continue

            results.append(
                {
                    **item,
                    "country_code": country,
                    "country_name": COUNTRIES.get(
                        country,
                        country,
                    ),
                }
            )

        return results

    async def get_all_countries(
        self,
        category: str,
        hours: int = 24,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        tasks = [
            self.get_country_topics(
                country=country,
                category=category,
                hours=hours,
                limit=limit,
            )
            for country in COUNTRIES
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        combined: list[dict[str, Any]] = []
        failures: list[dict[str, str]] = []

        for country, result in zip(COUNTRIES, results):
            if isinstance(result, Exception):
                failures.append(
                    {
                        "country": country,
                        "error": str(result),
                    }
                )
                continue

            combined.extend(result)

        if not combined and failures:
            error_summary = "; ".join(
                f"{failure['country']}: {failure['error']}"
                for failure in failures
            )

            raise TrendsError(
                "All country requests failed: "
                f"{error_summary}"
            )

        return combined