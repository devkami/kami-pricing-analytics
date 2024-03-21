from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel

from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research import PricingResearch

research_app = FastAPI(
    title='KAMI-Pricing Analytics API',
    description="API to conduct pricing research over a product's URL.",
    version='0.1.0',
)
api_router = APIRouter()


class ResearchRequest(BaseModel):
    product_url: str
    research_strategy: int = StrategyOptions.WEB_SCRAPING.value


@research_app.post(
    '/research',
    response_model=Dict[str, List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
)
async def research(product_data: ResearchRequest):
    try:
        pricing_research = PricingResearch(url=product_data.product_url)
        pricing_research.set_strategy(product_data.research_strategy)

        await pricing_research.conduct_research()

        return pricing_research.result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while scraping the product.',
        )


research_app.include_router(api_router, prefix='/api')
app = FastAPI()
app.mount('/api', research_app)
