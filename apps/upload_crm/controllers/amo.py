from pprint import pprint

from adrf.decorators import api_view

from apps.Core.services.base import acontroller, asemaphore_handler
from service.amo.classes.amo.amo import AmoAPI


@acontroller('Выгрузка amo')
@api_view(('GET',))
@asemaphore_handler
async def upload_amo(request):
    AAPI = AmoAPI()
    # pipelines = await AAPI.get_pipelines()
    leads = await AAPI.get_leads()
    pprint(leads)
    pprint(len(leads))
