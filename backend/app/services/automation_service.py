import asyncio
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.pipeline.pipeline import (
    BlogAutomationPipeline,
)


class AutomationService:
    def __init__(self) -> None:
        self.running = False
        self.cycle_running = False
        self.last_result: dict[str, Any] | None = None
        self.last_error: str | None = None
        self.last_started_at: str | None = None
        self.last_finished_at: str | None = None
        self.next_cycle_at: str | None = None

        self._lock = asyncio.Lock()

    async def run_cycle(
        self,
    ) -> dict[str, Any]:
        if self.cycle_running:
            return {
                "success": False,
                "message": (
                    "A cycle is already running."
                ),
            }

        async with self._lock:
            self.cycle_running = True
            self.last_started_at = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
            self.last_error = None

            try:
                pipeline = (
                    BlogAutomationPipeline()
                )

                result = await asyncio.wait_for(
                    pipeline.run(),
                    timeout=(
                        settings.cycle_timeout_minutes
                        * 60
                    ),
                )

                self.last_result = result
                self.last_finished_at = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )

                return result

            except asyncio.TimeoutError:
                error = (
                    "Automation cycle exceeded "
                    f"{settings.cycle_timeout_minutes} "
                    "minutes and was stopped."
                )

                self.last_error = error

                result = {
                    "success": False,
                    "error": error,
                }

                self.last_result = result

                return result

            except Exception as exc:
                error = str(exc)

                self.last_error = error

                result = {
                    "success": False,
                    "error": error,
                }

                self.last_result = result

                return result

            finally:
                self.cycle_running = False
                self.last_finished_at = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "cycle_running": self.cycle_running,
            "cycle_timeout_minutes": (
                settings.cycle_timeout_minutes
            ),
            "cycle_cooldown_minutes": (
                settings.cycle_cooldown_minutes
            ),
            "last_started_at": (
                self.last_started_at
            ),
            "last_finished_at": (
                self.last_finished_at
            ),
            "next_cycle_at": (
                self.next_cycle_at
            ),
            "last_error": self.last_error,
            "last_result": self.last_result,
        }