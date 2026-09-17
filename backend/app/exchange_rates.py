from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

import httpx


FRANKFURTER_BASE_URL = "https://api.frankfurter.dev"
ECB_DATA_URL = "https://data-api.ecb.europa.eu/service/data/EXR"
_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


class ExchangeRateError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExchangeRateQuote:
    base: str
    quote: str
    rate: Decimal
    rate_date: date
    source: str


def _currency_code(value: str) -> str:
    code = str(value or "").strip().upper()
    if not _CURRENCY_PATTERN.fullmatch(code):
        raise ExchangeRateError(f"不支持的币种代码：{value}")
    return code


def _positive_decimal(value: object) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ExchangeRateError("汇率服务返回了无效数值") from exc
    if not number.is_finite() or number <= 0:
        raise ExchangeRateError("汇率服务返回了非正数汇率")
    return number


async def fetch_frankfurter_rate(
    base: str,
    quote: str = "CNY",
    *,
    client: httpx.AsyncClient,
) -> ExchangeRateQuote:
    base_code = _currency_code(base)
    quote_code = _currency_code(quote)
    if base_code == quote_code:
        return ExchangeRateQuote(base_code, quote_code, Decimal("1"), date.today(), "identity")

    response = await client.get(f"{FRANKFURTER_BASE_URL}/v2/rate/{base_code}/{quote_code}")
    response.raise_for_status()
    try:
        payload = response.json()
        rate_date = date.fromisoformat(str(payload["date"]))
        rate = _positive_decimal(payload["rate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ExchangeRateError("Frankfurter 返回数据格式异常") from exc
    return ExchangeRateQuote(base_code, quote_code, rate, rate_date, "frankfurter")


async def fetch_ecb_rate(
    base: str,
    quote: str = "CNY",
    *,
    client: httpx.AsyncClient,
) -> ExchangeRateQuote:
    base_code = _currency_code(base)
    quote_code = _currency_code(quote)
    if base_code == quote_code:
        return ExchangeRateQuote(base_code, quote_code, Decimal("1"), date.today(), "identity")

    requested = [code for code in (base_code, quote_code) if code != "EUR"]
    series = "+".join(dict.fromkeys(requested))
    response = await client.get(
        f"{ECB_DATA_URL}/D.{series}.EUR.SP00.A",
        params={"lastNObservations": 1, "format": "csvdata"},
    )
    response.raise_for_status()

    observations: dict[str, tuple[date, Decimal]] = {}
    for row in csv.DictReader(io.StringIO(response.text)):
        currency = str(row.get("CURRENCY") or "").upper()
        if currency not in requested:
            continue
        try:
            observations[currency] = (
                date.fromisoformat(str(row["TIME_PERIOD"])),
                _positive_decimal(row["OBS_VALUE"]),
            )
        except (KeyError, ValueError) as exc:
            raise ExchangeRateError("ECB 返回数据格式异常") from exc

    missing = [code for code in requested if code not in observations]
    if missing:
        raise ExchangeRateError(f"ECB 暂无币种数据：{', '.join(missing)}")

    base_per_eur = Decimal("1") if base_code == "EUR" else observations[base_code][1]
    quote_per_eur = Decimal("1") if quote_code == "EUR" else observations[quote_code][1]
    rate_date = min(
        [observations[code][0] for code in requested],
        default=date.today(),
    )
    return ExchangeRateQuote(
        base_code,
        quote_code,
        quote_per_eur / base_per_eur,
        rate_date,
        "ecb",
    )


async def fetch_exchange_rate(base: str, quote: str = "CNY") -> ExchangeRateQuote:
    errors: list[str] = []
    timeout = httpx.Timeout(8.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for provider in (fetch_frankfurter_rate, fetch_ecb_rate):
            try:
                return await provider(base, quote, client=client)
            except (ExchangeRateError, httpx.HTTPError) as exc:
                errors.append(f"{provider.__name__}: {exc}")
    raise ExchangeRateError("；".join(errors) or "汇率服务暂时不可用")
