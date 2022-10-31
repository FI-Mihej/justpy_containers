__all__ = [
 'justpy', 'init_scheduler', 'init_thread_pool_executor']
import asyncio
from concurrent.futures import ProcessPoolExecutor
from cengal.parallel_execution.coroutines.coro_scheduler import CoroScheduler
from cengal.parallel_execution.coroutines.coro_standard_services.loop_yield import eagly, CoroPriority
from functools import partial
from typing import Optional, Callable
from cengal.data_manipulation.serialization import *
serializer = best_serializer({DataFormats.json,
 Tags.decode_str_as_str,
 Tags.decode_list_as_list,
 Tags.superficial,
 Tags.current_platform,
 Tags.multi_platform}, test_data_factory(TestDataType.deep_large), 0.1)
print(serializer.serializer)
from cengal.parallel_execution.coroutines.coro_tools.low_latency.json import adump, adumps, aload, aloads
import justpy

class AsyncJustPyJson(justpy.low_latency.AsyncJustPyJsonMixin):

    def __init__(self, cs):
        self.cs = cs
        super().__init__()

    async def dump(self, *args, **kwargs):
        return await adump(self.cs, *args, **kwargs)

    async def dumps(self, *args, **kwargs):
        return await adumps(self.cs, *args, **kwargs)

    async def load(self, *args, **kwargs):
        return await aload(self.cs, *args, **kwargs)

    async def loads(self, *args, **kwargs):
        return await aloads(self.cs, *args, **kwargs)


justpy.low_latency.set_just_py_json(justpy.low_latency.JustPyJson(serializer.dump, serializer.dumps, serializer.load, serializer.loads))

def init_scheduler(default_priority: CoroPriority, coro_scheduler: Optional[CoroScheduler]=None, asyncio_loop: Optional[asyncio.AbstractEventLoop]=None):
    scheduler = partial(eagly, default_priority, coro_scheduler, asyncio_loop)
    justpy.low_latency.set_scheduler(scheduler)
    if coro_scheduler is not None:
        justpy.low_latency.set_just_py_ajson(AsyncJustPyJson(coro_scheduler))


class Executor:

    def __init__(self, loop: asyncio.AbstractEventLoop, processes_num: int=3) -> None:
        self.loop = loop
        self.executor = ProcessPoolExecutor(max_workers=processes_num)

    async def __call__(self, loop: Optional[asyncio.AbstractEventLoop], worker: Callable, *args, **kwargs) -> Any:
        worker_with_args = partial(worker, *args, **kwargs)
        return await loop.run_in_executor(self.executor, worker_with_args)


def init_thread_pool_executor(loop: asyncio.AbstractEventLoop, processes_num: int=3):
    justpy.low_latency.set_thread_pool_executor(Executor(loop, processes_num))