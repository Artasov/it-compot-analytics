import asyncio
from concurrent.futures import ThreadPoolExecutor

from django.core.cache import cache


class DJRediser:
    class CacheByNameNotFound(Exception):
        pass

    @staticmethod
    def clear(name: str):
        cache.delete(name)

    @staticmethod
    def cache(name, obj=None, *args, **kwargs):
        cache_key = name

        if obj is None:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            else:
                raise DJRediser.CacheByNameNotFound(f'No cache found for {name}')
        else:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            else:
                result = None
                if callable(obj):
                    if asyncio.iscoroutinefunction(obj):
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            result = loop.run_until_complete(obj(*args, **kwargs))
                        else:
                            result = asyncio.run(obj(*args, **kwargs))
                    else:
                        with ThreadPoolExecutor() as executor:
                            result = executor.submit(obj, *args, **kwargs).result()
                else:
                    result = obj

                cache.set(cache_key, result)
                return result

    @staticmethod
    async def acache(name, obj=None, *args, **kwargs):
        cache_key = name

        if obj is None:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            else:
                raise DJRediser.CacheByNameNotFound(f'No cache found for {name}')
        else:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            else:
                result = None
                if callable(obj):
                    if asyncio.iscoroutinefunction(obj):
                        result = await obj(*args, **kwargs)
                    else:
                        with ThreadPoolExecutor() as executor:
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(executor, obj, *args, **kwargs)
                else:
                    result = obj

                cache.set(cache_key, result)
                return result
