from unittest.mock import AsyncMock

import pytest

from scraper.scraper import (
    BelezaNaWebScraper,
    ScraperException,
    ScraperFactory,
)


@pytest.mark.asyncio
async def test_belezanaweb_fetch_content_success(mocker):
    expected_url = 'https://www.belezanaweb.com.br/some-product'
    expected_response = '<html></html>'

    mocker.patch(
        'scraper.scraper.BelezaNaWebScraper._get_crawl_delay_async',
        return_value=AsyncMock(return_value=0),
    )

    mocker.patch(
        'httpx.AsyncClient.get', return_value=AsyncMock(text=expected_response)
    )

    scraper = BelezaNaWebScraper(product_url=expected_url)
    content = await scraper.fetch_content()

    assert (
        content == expected_response
    ), 'The fetch_content method should return the expected HTML content.'


@pytest.mark.asyncio
async def test_belezanaweb_scrap_product_success(mocker):
    expected_url = 'https://www.belezanaweb.com.br/some-product'
    fake_html_content = """<html><a class="js-add-to-cart" data-sku='[{"sku":"123", "brand":"Test Brand", "category":"Test Category", "name":"Test Name", "price":"100", "seller":{"name":"Test Seller"}}]'></a></html>"""

    mocker.patch.object(
        BelezaNaWebScraper,
        'fetch_content',
        new=AsyncMock(return_value=fake_html_content),
    )

    scraper = BelezaNaWebScraper(product_url=expected_url)
    products = await scraper.scrap_product()

    assert (
        len(products) == 1
    ), 'scrap_product should return a list with one product.'
    assert (
        products[0]['sku'] == '123'
    ), 'The product SKU should be parsed correctly.'


def test_scraper_factory_returns_correct_scraper_for_belezanaweb():
    product_url = 'https://www.belezanaweb.com.br/some-product'
    scraper = ScraperFactory.get_scraper(product_url=product_url)
    assert isinstance(
        scraper, BelezaNaWebScraper
    ), 'ScraperFactory should return an instance of BelezaNaWebScraper for a BelezaNaWeb URL.'


def test_scraper_factory_raises_error_for_unsupported_marketplace():
    product_url = 'https://www.unsupportedmarketplace.com/some-product'
    with pytest.raises(ScraperException) as exc_info:
        ScraperFactory.get_scraper(product_url=product_url)
    assert 'Marketplace not supported' in str(
        exc_info.value
    ), 'ScraperFactory should raise ScraperException for unsupported marketplaces.'
