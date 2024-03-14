from typing import Dict, List

from fastapi import FastAPI, HTTPException

from .scraper import ScraperFactory

app = FastAPI()


@app.post('/scrap/', response_model=List[Dict])
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
