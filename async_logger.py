import asyncio
import logging
from asyncio import Task
from time import sleep
from typing import List


class AsyncLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__queue = asyncio.Queue()
        self.__workers: List[Task] = []
        self.__concurrency = 3

    async def __consumer_worker(self):
        while True:
            try:
                message = await self.__queue.get()
                await self.__log_message(message)
                self.__queue.task_done()
            except asyncio.CancelledError:
                await self.__log_message("Cancelled")
                break
            # except Exception:
            #     raise

    async def __log_message(self, message):
        await asyncio.sleep(3)
        # sleep(1)
        self.logger.warning(message)

    def get_queue(self):
        return self.__queue

    async def run_loop(self):
        for _ in range(self.__concurrency):
            await self.__log_message("Created task")
            self.__workers.append(
                asyncio.create_task(self.__consumer_worker())
            )
        await asyncio.gather(*self.__workers)

    async def finish_loop(self):
        await self.__queue.join()
        for task in self.__workers:
            task.cancel()


async_logger = AsyncLogger()
logger_queue = async_logger.get_queue()


def system_log(message):
    logger_queue.put_nowait(message)
