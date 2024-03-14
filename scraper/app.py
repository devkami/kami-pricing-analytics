from typing import Dict, List

from fastapi import APIRouter, FastAPI, HTTPException

from .scraper import ScraperFactory

scraper_app = FastAPI(
    title="KAMI-Pricing Scraper API",
    description="API to scrap prices from competitors' products on especific marketplace.",
    version="0.1.0",
)
api_router = APIRouter()


@scraper_app.post('/scrap/', response_model=List[Dict])
async def scrap_product(product_url: str):
    try:

        scraper = ScraperFactory.get_scraper(product_url)
        sellers_list = await scraper.scrap_product()
        return sellers_list
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail='An error occurred while scraping the product.',
        )


scraper_app.include_router(api_router, prefix='/api')
app = FastAPI()

app.mount("/api", scraper_app)