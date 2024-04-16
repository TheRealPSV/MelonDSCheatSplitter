import asyncio


class FlushingTaskQueue:
    """A coroutine task queue that queues up tasks and performs them concurrently when the queue fills.
    Remember to call the `flush()` function explicitly once you know new tasks will not be added to the queue.
    """

    _queue = []

    def __init__(self, queuesize: int | None = None):
        """Create a `FlushingTaskQueue` with the given queue size.

        Args:
            queuesize (int | None, optional): the size of the queue before it flushes. If None or unspecified, this will never flush automatically, behaving similarly to a standard `asyncio.TaskGroup`.
        """

        self.queuesize = queuesize

    async def flush(self):
        """Process the queue. Make sure to call this explicitly once new tasks are no longer being added."""

        tempqueue = self._queue
        self._queue = []
        async with asyncio.TaskGroup() as tg:
            for x in tempqueue:
                tg.create_task(x)

    async def push(self, coro: any):
        """Push a coroutine task onto the queue. If a queuesize is specified for this FlushingTaskQueue, and the queue is full, process the queue.

        Args:
            coro (any): A coroutine task to be performed.
        """

        self._queue.append(coro)
        if self.queuesize and len(self._queue) >= self.queuesize:
            await self.flush()
