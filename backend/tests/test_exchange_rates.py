from datetime import date
from decimal import Decimal

import httpx
import pytest

import app.exchange_rates as exchange_rates
from app.exchange_rates import ExchangeRateError, ExchangeRateQuote, fetch_ecb_rate, fetch_frankfurter_rate


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Exchange-rate parser tests do not require a database connection."""
    yield


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_frankfurter_hkd_to_cny_rate():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/rate/HKD/CNY"
        return httpx.Response(
            200,
            json={"date": "2026-08-07", "base": "HKD", "quote": "CNY", "rate": 0.85929},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_frankfurter_rate("hkd", "cny", client=client)

    assert result.rate == Decimal("0.85929")
    assert result.rate_date == date(2026, 8, 7)
    assert result.source == "frankfurter"


@pytest.mark.anyio
async def test_ecb_cross_rate_hkd_to_cny():
    csv_payload = """KEY,FREQ,CURRENCY,CURRENCY_DENOM,EXR_TYPE,EXR_SUFFIX,TIME_PERIOD,OBS_VALUE
EXR.D.CNY.EUR.SP00.A,D,CNY,EUR,SP00,A,2026-08-07,7.8000
EXR.D.HKD.EUR.SP00.A,D,HKD,EUR,SP00,A,2026-08-07,9.1000
"""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/D.HKD+CNY.EUR.SP00.A")
        assert request.url.params["lastNObservations"] == "1"
        return httpx.Response(200, text=csv_payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_ecb_rate("HKD", "CNY", client=client)

    assert result.rate == Decimal("7.8000") / Decimal("9.1000")
    assert result.rate_date == date(2026, 8, 7)
    assert result.source == "ecb"


@pytest.mark.anyio
async def test_exchange_rate_falls_back_to_ecb(monkeypatch):
    async def unavailable(*args, **kwargs):
        raise ExchangeRateError("Frankfurter unavailable")

    async def ecb_result(base, quote, *, client):
        return ExchangeRateQuote(
            base=base,
            quote=quote,
            rate=Decimal("0.86"),
            rate_date=date(2026, 8, 7),
            source="ecb",
        )

    monkeypatch.setattr(exchange_rates, "fetch_frankfurter_rate", unavailable)
    monkeypatch.setattr(exchange_rates, "fetch_ecb_rate", ecb_result)

    result = await exchange_rates.fetch_exchange_rate("HKD", "CNY")

    assert result.rate == Decimal("0.86")
    assert result.source == "ecb"
