from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from kami_pricing_analytics.data_collector import CollectorOptions
from kami_pricing_analytics.interface.api import PricingResearchRequest

# API application instance
research_app = FastAPI(
    title='KAMI-Pricing Analytics API',
    description="API to conduct pricing research over a product's URL.",
    version='0.6.1',
)

# Router for managing API endpoints
api_router = APIRouter()


class PricingResearchPayload(BaseModel):
    """
    Data model for receiving pricing research requests.

    Fields:
        url (Optional[str]): URL of the product on the marketplace.
        marketplace (Optional[str]): Name of the marketplace.
        marketplace_id (Optional[str]): ID of the product on the marketplace.
        collector_option (int): Strategy to be used to collect the data, defaulting to web scraping.
        store_result (bool): Whether to store the results in a database.
    """

    url: Optional[str] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    collector_option: int = Field(default=CollectorOptions.WEB_SCRAPING.value)
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
async def post_research(payload: PricingResearchPayload) -> Dict[str, Any]:
    """
    Endpoint to initiate pricing research and return the results.

    Args:
        payload (PricingResearchPayload): The payload containing research parameters.

    Returns:
        Dict[str, Any]: A dictionary containing the research results.
    """
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


@research_app.get(
    '/research',
    response_model=Dict[str, List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
    summary='Retrieve the results of a pricing research.',
    description="""
    Retrieve the results of a pricing research for a given product. The results is a list of sellers and their prices for this product.
    Query Parameters:
    - `marketplace`: Name of the marketplace.
      Marketplaces supported: 
        - beleza_na_web: Beleza na Web
        - amazon: Amazon 
        - mercado_livre: Mercado Livre
    - `marketplace_id`: ID of the product on the marketplace.
    """,
)
async def get_research(
    marketplace: str, marketplace_id: str
) -> Dict[str, Any]:
    """
    Endpoint to retrieve stored results of pricing research for a specified marketplace and product ID.

    Args:
        marketplace (str): The marketplace name.
        marketplace_id (str): The product ID on the marketplace.

    Returns:
        Dict[str, Any]: A dictionary containing the research results.
    """
    try:
        payload = PricingResearchPayload(
            marketplace=marketplace, marketplace_id=marketplace_id
        )
        request = PricingResearchRequest(**payload.model_dump())
        return await request.get()
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
async def handle_value_error(request, exc) -> JSONResponse:
    """
    Global exception handler for ValueError, returning a formatted JSON response.

    Args:
        request: The request object.
        exc (ValueError): The caught ValueError exception.

    Returns:
        JSONResponse: A JSON response indicating the error.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'message': str(exc)},
    )


# Mounting the research app on the main FastAPI app
research_app.include_router(api_router, prefix='/api')
app = FastAPI()
app.mount('/api', research_app)
