import asyncio
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.services.automation_service import (
    AutomationService,
)


class AutomationScheduler:
    def __init__(
        self,
        service: AutomationService,
    ) -> None:
        self.service = service
        self.task: asyncio.Task | None = None

    async def start(self) -> None:
        if self.task and not self.task.done():
            return

        self.service.start()

        self.task = asyncio.create_task(
            self._loop()
        )

    async def stop(self) -> None:
        self.service.stop()

        if self.task:
            self.task.cancel()

            try:
                await self.task
            except asyncio.CancelledError:
                pass

            self.task = None

    async def _loop(self) -> None:
        while self.service.running:
            await self.service.run_cycle()

            if not self.service.running:
                break

            next_time = (
                datetime.now(
                    timezone.utc
                )
                + timedelta(
                    minutes=settings.cycle_cooldown_minutes
                )
            )

            self.service.next_cycle_at = (
                next_time.isoformat()
            )

            try:
                await asyncio.sleep(
                    settings.cycle_cooldown_minutes
                    * 60
                )
            except asyncio.CancelledError:
                break

            self.service.next_cycle_at = None