import configparser
import logging
import os
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, status
from pydantic import BaseModel, model_validator

from kami_pricing_analytics.data_storage.storage_factory import (
    StorageModeOptions,
)
from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research import PricingResearch

research_app = FastAPI(
    title='KAMI-Pricing Analytics API',
    description="API to conduct pricing research over a product's URL.",
    version='0.2.1',
)
api_router = APIRouter()

settings_path = os.path.join('config', 'settings.cfg')
settings = configparser.ConfigParser()
settings.read(settings_path)
storage_mode = StorageModeOptions(settings.getint('storage', 'MODE'))


class ResearchRequest(BaseModel):
    product_url: str = None
    marketplace: str = None
    marketplace_id: str = None
    research_strategy: int = StrategyOptions.WEB_SCRAPING.value

    @model_validator(mode='after')
    def check_input_required_fields(self):
        if not self.product_url and (
            not self.marketplace or not self.marketplace_id
        ):
            raise ValueError(
                'Either Product URL or marketplace and marketplace_id is required to conduct research.'
            )
        return self


@research_app.post(
    '/research',
    response_model=Dict[str, List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
)
async def research(
    product_data: ResearchRequest, background_tasks: BackgroundTasks
):
    try:
        if product_data.product_url:
            pricing_research = PricingResearch(url=product_data.product_url)
        else:
            pricing_research = PricingResearch(
                marketplace=product_data.marketplace,
                marketplace_id=product_data.marketplace_id,
            )
        pricing_research.set_strategy(product_data.research_strategy)
        pricing_research.set_storage(mode_option=storage_mode)

        await pricing_research.conduct_research()

        background_tasks.add_task(pricing_research.store_research)

        return pricing_research.result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logging.error(f'Unexpected error: {str(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while scraping the product.',
        )


research_app.include_router(api_router, prefix='/api')
app = FastAPI()
app.mount('/api', research_app)
