import asyncio
import math
from datetime import datetime
from urllib.parse import urlencode

import aiohttp
from django.conf import settings


class AmoAPIBase:
    def __init__(self, subdomain: str = settings.AMO_SUBDOMAIN, access_token: str = settings.AMO_TOKEN):
        if not all((subdomain, access_token)):
            raise ValueError('subdomain and access_token required')
        self.subdomain = subdomain
        self.access_token = access_token
        self.rate_limit = 7
        self.request_count = 0
        self.start_time = datetime.now()

    async def fetch(self, session, url, headers, current, total):
        await self._wait_if_needed()
        print(f"Request {current}/{total}")
        async with session.get(url, headers=headers) as response:
            self.request_count += 1
            if response.status == 200:
                result = await response.json()
                return result
            else:
                return {'status': response.status, 'message': await response.text()}

    async def fetch_all(self, url, headers, params, maxTake=300000, batchSize=250):
        async with aiohttp.ClientSession() as session:
            total_pages = math.ceil(maxTake / batchSize)
            for page in range(1, total_pages + 1):
                batch_params = params.copy()
                batch_params['page'] = page
                batch_params['limit'] = batchSize
                batch_url = f"{url}?{urlencode(batch_params, safe='/', encoding='utf-8')}"

                result = await self.fetch(session, batch_url, headers, page, total_pages)
                if not result or len(result) == 0:
                    break

                yield result

    async def api_call_pagination(self, endpoint, maxTake=300000, batchSize=250, **kwargs):
        url = f"https://{self.subdomain}.amocrm.ru/api/v4/{endpoint}"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        results = []
        async for result in self.fetch_all(url, headers, kwargs, maxTake=maxTake, batchSize=batchSize):
            results.extend(result)
        return results

    async def api_call(self, endpoint, **params):
        url = f"https://{self.subdomain}.amocrm.ru/api/v4/{endpoint}"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        async with aiohttp.ClientSession() as session:
            response = await self.fetch(session, f"{url}?{urlencode(params)}", headers, 1, 1)
            return response

    async def post_fetch(self, session, url, data, headers):
        await self._wait_if_needed()
        print(f"Post request to {url}")
        async with session.post(url, json=data, headers=headers) as response:
            self.request_count += 1
            json = await response.json()
            if response.status == 200:
                return {'success': True}
            else:
                print(json)
                return {'success': False}

    async def api_post_call(self, endpoint, **params):
        url = f"https://{self.subdomain}.amocrm.ru/api/v4/{endpoint}"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        async with aiohttp.ClientSession() as session:
            response = await self.post_fetch(session, url, data=params, headers=headers)
            return response

    async def _wait_if_needed(self):
        if self.request_count >= self.rate_limit:
            now = datetime.now()
            time_passed = (now - self.start_time).total_seconds()
            if time_passed < 1:
                await asyncio.sleep(1 - time_passed)
            self.start_time = datetime.now()
            self.request_count = 0


class AmoAPI(AmoAPIBase):
    async def get_leads(self, maxTake=300000, batchSize=250, **kwargs):
        return await self.api_call_pagination('leads', maxTake=maxTake, batchSize=batchSize, **kwargs)

    async def get_lead_by_id(self, lead_id):
        return await self.api_call(f'leads/{lead_id}')

    async def add_leads(self, **kwargs):
        return await self.api_post_call('leads', **kwargs)

    async def update_leads(self, **kwargs):
        return await self.api_post_call('leads', **kwargs)

    async def get_pipelines(self, **kwargs):
        return await self.api_call('leads/pipelines', **kwargs)

    async def get_pipeline_by_id(self, pipeline_id):
        return await self.api_call(f'leads/pipelines/{pipeline_id}')

    async def get_contacts(self, maxTake=10000, batchSize=250, **kwargs):
        return await self.api_call_pagination('contacts', maxTake=maxTake, batchSize=batchSize, **kwargs)

    async def get_contact_by_id(self, contact_id):
        return await self.api_call(f'contacts/{contact_id}')
