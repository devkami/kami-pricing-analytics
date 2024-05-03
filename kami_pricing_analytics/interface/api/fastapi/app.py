from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from kami_pricing_analytics.interface.api.pricing_research_request import (
    PricingResearchRequest,
)

research_app = FastAPI(
    title='KAMI-Pricing Analytics API',
    description="API to conduct pricing research over a product's URL.",
    version='0.6.0',
)
api_router = APIRouter()


@research_app.post(
    '/research',
    response_model=Dict[str, List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
)
async def research(request: PricingResearchRequest):
    try:

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
