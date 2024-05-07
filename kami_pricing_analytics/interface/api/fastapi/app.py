from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research_request import (
    PricingResearchRequest,
)

research_app = FastAPI(
    title='KAMI-Pricing Analytics API',
    description="API to conduct pricing research over a product's URL.",
    version='0.6.1',
)
api_router = APIRouter()


class PricingResearchPayload(BaseModel):
    url: Optional[str] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    strategy_option: int = Field(default=StrategyOptions.WEB_SCRAPING.value)
    store_result: bool = Field(default=False)


@research_app.post(
    '/research',
    response_model=Dict[str, List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
    summary='Conduct a pricing research over a product.',
    description="""
    Conduct a pricing research over a product for a given URL on marketplace. or The Market Place Name and the Marketplace ID for that product. The results is a list of sellers and their prices for this product. It's also allows to store the results in a database. and choose the strategy to be used to collect the data. 
    
    Payload
    - `url`: URL of the product on the marketplace.
    - `marketplace`: Name of the marketplace.
      Marketplaces supported: 
        - beleza_na_web: Beleza na Web
        - amazon: Amazon 
        - mercado_livre: Mercado Livre 
    - `marketplace_id`: ID of the product on the marketplace.
    - `strategy`: Strategy to be used to collect the data.
      Strategies supported:
        - 0: Web Scraping
    - `store_result`: Store the results in a database.
    """,
)
async def research(payload: PricingResearchPayload):
    try:

        request = PricingResearchRequest(**payload.model_dump())
        sellers = await request.post()
        return {'result': sellers}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error occurred: {str(e)}',
        )


@research_app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'message': str(exc)},
    )


research_app.include_router(api_router, prefix='/api')
app = FastAPI()
app.mount('/api', research_app)
