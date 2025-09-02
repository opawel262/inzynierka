from typing import List, Optional, Literal, Dict

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate

from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings
from app.domain.portfolio.repositories.stock_repository import StockRepository
from app.domain.portfolio.services.stock_service import StockService
from app.domain.portfolio.services.crypto_service import CryptoService
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.repositories.currency_repository import (
    CurrencyPairRateRepository,
)
from app.domain.portfolio.services.currency_service import (
    CurrencyService,
)

from app.domain.portfolio.schemas.currency_schemas import CurrencyPairRateSchema
from app.domain.portfolio.schemas.stock_schemas import (
    StockSymbolSchema,
    StockBasicSchema,
    StockSearchSchema,
    StockPricePerformanceSchema,
)
from app.domain.portfolio.schemas.crypto_schemas import (
    CryptoSymbolSchema,
    CryptoBasicSchema,
    CryptoSearchSchema,
    CryptoPricePerformanceSchema,
)
from app.domain.portfolio.schemas.crypto_historical_schemas import (
    CryptoHistoricalPriceSchema,
)
from app.domain.portfolio.schemas.stock_historical_schemas import (
    StockHistoricalPriceSchema,
)
from app.domain.portfolio.schemas.global_schemas import GlobalMarketPerformanceSchema
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/assets",
    tags=["Assets Data"],
)


@router.get("/stocks", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_stocks_data(
    request: Request,
    search: Optional[str] = Query(
        None, description="Search term for stock names by ticker or name"
    ),
    db: Session = Depends(get_db),
) -> Page[StockSearchSchema]:
    """
    Return stock data from GPW.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)

    stocks_data = stock_service.search_stocks(search=search)

    return paginate(stocks_data)


@router.get("/stocks/symbols", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_stocks_symbols(
    request: Request,
    db: Session = Depends(get_db),
) -> List[StockSymbolSchema]:
    """
    Return stock symbols from GPW.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)

    stocks_data = stock_service.search_stocks(search=None)

    return stocks_data


@router.get("/global-performance", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_market_global_performance(
    request: Request,
    db: Session = Depends(get_db),
) -> GlobalMarketPerformanceSchema:
    """
    Return global performance data for stocks from GPW and crypto.
    Includes: total 24h volume, total market capitalization,
    top 3 gainers/losers by price change in 24h.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)

    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)

    # Calculate total 24h volume and market cap
    global_crypto_data = crypto_service.get_global_performance_data()
    global_stock_data = stock_service.get_global_performance_data()

    return {
        "global_crypto_data": global_crypto_data,
        "global_stock_data": global_stock_data,
    }


@router.get("/stocks/fields-metadata", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_stocks_fields_metadata(
    request: Request,
    lang: Literal["pl", "en"] = Query("pl", description="Language for field metadata"),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Return metadata for stock fields (PL / EN).
    """

    FIELDS_METADATA = {
        "symbol": {
            "pl": "Symbol giełdowy (ticker) spółki. Na GPW tickery mają końcówkę .WA (np. PKN.WA dla Orlenu). Jest to unikalny identyfikator akcji.",
            "en": "Stock ticker symbol of the company. On the Warsaw Stock Exchange tickers end with .WA (e.g. PKN.WA for Orlen). This is a unique share identifier.",
        },
        "name": {
            "pl": "Pełna lub skrócona nazwa spółki, np. KGHM Polska Miedź S.A.",
            "en": "Full or short company name, e.g. KGHM Polska Miedź S.A.",
        },
        "sector": {
            "pl": "Sektor gospodarki, w którym działa spółka (np. bankowość, energetyka, surowce). Pozwala grupować i porównywać spółki z podobnych branż.",
            "en": "Economic sector in which the company operates (e.g. banking, energy, resources). Allows grouping and comparison of companies in similar industries.",
        },
        "price": {
            "pl": "Aktualna cena rynkowa jednej akcji spółki w danej chwili. Wartość zmienia się dynamicznie w trakcie sesji giełdowej.",
            "en": "Current market price of a single company share at a given moment. This value changes dynamically during the trading session.",
        },
        "currency": {
            "pl": "Waluta, w której notowana jest akcja. Na GPW zazwyczaj PLN (złoty polski).",
            "en": "Currency in which the stock is traded. On the WSE usually PLN (Polish zloty).",
        },
        "volume_24h": {
            "pl": "Łączny wolumen obrotu akcjami w ciągu ostatnich 24 godzin (liczba akcji, które zmieniły właściciela). Pokazuje płynność rynku.",
            "en": "Total trading volume of shares in the last 24 hours (number of shares traded). Indicates market liquidity.",
        },
        "market_cap": {
            "pl": "Kapitalizacja rynkowa spółki = aktualna cena akcji × liczba akcji w obiegu. Pokazuje łączną wartość spółki według rynku.",
            "en": "Market capitalization = current share price × number of shares outstanding. Represents the total market value of the company.",
        },
        "market_state": {
            "pl": "Aktualny stan rynku: OPEN (otwarty), CLOSED (zamknięty), PRE (przed otwarciem), POST (po zamknięciu).",
            "en": "Current market state: OPEN, CLOSED, PRE (pre-market), POST (after hours).",
        },
        "description": {
            "pl": "Opis działalności spółki: czym się zajmuje, jakie ma produkty, usługi i rynki docelowe.",
            "en": "Description of the company's business: its products, services, and target markets.",
        },
        "debt_to_equity": {
            "pl": "Wskaźnik D/E (dług/kapitał własny). Pokazuje, w jakim stopniu spółka finansuje się długiem względem kapitału akcjonariuszy.",
            "en": "Debt-to-equity (D/E) ratio. Indicates the extent to which a company is financing itself with debt compared to shareholder equity.",
        },
        "trailing_annual_dividend_yield": {
            "pl": "Stopa dywidendy z ostatnich 12 miesięcy. Wyrażona w %, pokazuje jaki procent wartości akcji inwestor otrzymał w dywidendach.",
            "en": "Dividend yield from the last 12 months. Expressed as %, showing what percentage of stock value investors received in dividends.",
        },
        "return_on_equity": {
            "pl": "ROE (zwrot z kapitału własnego). Mierzy, ile zysku netto przypada na jednostkę kapitału akcjonariuszy.",
            "en": "ROE (return on equity). Measures how much net profit is generated per unit of shareholder equity.",
        },
        "free_cashflow": {
            "pl": "Wolne przepływy pieniężne (Free Cash Flow, FCF). To gotówka, która zostaje spółce po pokryciu kosztów operacyjnych i inwestycji.",
            "en": "Free Cash Flow (FCF). The cash a company generates after covering operating costs and investments.",
        },
        "payout_ratio": {
            "pl": "Procent zysku netto przeznaczony na dywidendy. Niski = firma zatrzymuje zyski, wysoki = większość trafia do akcjonariuszy.",
            "en": "Percentage of net income paid out as dividends. Low = company retains profits, high = most profits go to shareholders.",
        },
        "price_to_book": {
            "pl": "Wskaźnik P/B (Price/Book). Porównuje cenę akcji do wartości księgowej przypadającej na akcję.",
            "en": "P/B ratio (Price/Book). Compares stock price to book value per share.",
        },
        "price_to_sales": {
            "pl": "Wskaźnik P/S (Price/Sales). Kapitalizacja rynkowa podzielona przez roczne przychody spółki.",
            "en": "P/S ratio (Price/Sales). Market capitalization divided by annual revenue.",
        },
        "eps_trailing_twelve_months": {
            "pl": "EPS (Earnings Per Share) – zysk na akcję z ostatnich 12 miesięcy. Obliczany jako zysk netto / liczba akcji.",
            "en": "EPS (Earnings Per Share) over the last 12 months. Calculated as net income / number of shares.",
        },
        "beta": {
            "pl": "Wskaźnik beta mierzy ryzyko rynkowe. Beta > 1 oznacza większą zmienność niż rynek, Beta < 1 mniejszą, Beta = 1 podobną.",
            "en": "Beta measures market risk. Beta > 1 means higher volatility than the market, Beta < 1 lower, Beta = 1 similar.",
        },
        "pe_ratio": {
            "pl": "Wskaźnik P/E (Price/Earnings). Cena akcji podzielona przez zysk na akcję. Niski = potencjalnie tania akcja, wysoki = potencjalnie droga.",
            "en": "P/E ratio (Price/Earnings). Share price divided by earnings per share. Low = potentially undervalued, high = potentially overvalued.",
        },
        "average_volume_10d": {
            "pl": "Średni dzienny wolumen obrotu w ciągu ostatnich 10 dni. Pokazuje aktywność i płynność handlu akcją.",
            "en": "Average daily trading volume over the last 10 days. Shows trading activity and liquidity of the stock.",
        },
        "employees": {
            "pl": "Liczba pracowników zatrudnionych w spółce. Świadczy o skali działalności.",
            "en": "Number of employees working at the company. Indicates scale of operations.",
        },
        "price_change_percentage_1h": {
            "pl": "Procentowa zmiana ceny akcji w ciągu 1 godziny. Pokazuje krótkoterminową zmienność kursu.",
            "en": "Percentage change in stock price over the last 1 hour. Shows short-term volatility.",
        },
        "price_change_percentage_24h": {
            "pl": "Procentowa zmiana ceny akcji w ciągu 24 godzin. Użyteczne do oceny jednodniowych trendów.",
            "en": "Percentage change in stock price over the last 24 hours. Useful for assessing one-day trends.",
        },
        "price_change_percentage_7d": {
            "pl": "Procentowa zmiana ceny akcji w ciągu ostatnich 7 dni. Pokazuje tygodniowy trend kursu.",
            "en": "Percentage change in stock price over the last 7 days. Shows weekly price trend.",
        },
        "price_change_percentage_30d": {
            "pl": "Procentowa zmiana ceny akcji w ciągu ostatnich 30 dni. Pokazuje miesięczny trend kursu.",
            "en": "Percentage change in stock price over the last 30 days. Shows monthly price trend.",
        },
        "price_change_percentage_1y": {
            "pl": "Procentowa zmiana ceny akcji w ciągu ostatnich 1 roku. Pokazuje roczny trend kursu.",
            "en": "Percentage change in stock price over the last 1 year. Shows yearly price trend.",
        },
        "price_change_percentage_max": {
            "pl": "Procentowa zmiana ceny akcji w ciągu całej historii. Pokazuje maksymalny trend kursu.",
            "en": "Percentage change in stock price over the entire history. Shows maximum price trend.",
        },
        "circulating_supply": {
            "pl": "Liczba akcji w obiegu (shares outstanding). To faktyczna liczba akcji dostępnych na rynku.",
            "en": "Number of shares outstanding (circulating supply). The actual number of shares available on the market.",
        },
    }

    return {field: desc[lang] for field, desc in FIELDS_METADATA.items()}


@router.get("/stocks/{symbol}/general", status_code=status.HTTP_200_OK)
def get_stock_general_details(
    symbol: str, db: Session = Depends(get_db)
) -> StockBasicSchema:
    """
    Return detailed information about a specific stock by its symbol.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)
    stock = stock_service.get_stock_by_symbol(symbol=symbol)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spółka z symbolem '{symbol}' nie została znaleziona.",
        )

    return stock


@router.get("/stocks/{symbol}/price-performance", status_code=status.HTTP_200_OK)
def get_stock_performance_details(
    symbol: str, db: Session = Depends(get_db)
) -> StockPricePerformanceSchema:
    """
    Return detailed information about a specific stock by its symbol.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)
    stock = stock_service.get_stock_by_symbol(symbol=symbol)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spółka z symbolem '{symbol}' nie została znaleziona.",
        )

    return stock


@router.get("/stocks/{symbol}/historical", status_code=status.HTTP_200_OK)
def get_stock_historical_data(
    symbol: str,
    period: Literal["1d", "1w", "1m", "1y", "max"] = Query(
        "1w",
        description="Period for historical data.",
    ),
    db: Session = Depends(get_db),
) -> List[StockHistoricalPriceSchema]:
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol jest wymagany.",
        )

    if period not in ["1d", "1w", "1m", "1y", "max"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy okres. Dostępne okresy to 1w, 1m, 1y, max.",
        )

    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)
    if period == "max":
        historical_data = (
            stock_service.get_stock_historical_by_symbol_data_from_last_max(
                symbol=symbol
            )
        )
    else:
        historical_data = (
            stock_service.get_stock_historical_by_symbol_period_data_from_last(
                symbol=symbol, period=period
            )
        )

    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brak danych historycznych dla spółki z symbolem '{symbol}' w okresie '{period}'.",
        )

    return historical_data


@router.get("/cryptos", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_cryptos_data(
    request: Request,
    search: Optional[str] = Query(
        None, description="Search term for crypto names by ticker or name"
    ),
    db: Session = Depends(get_db),
) -> Page[CryptoSearchSchema]:
    """
    Return crypto data from exchanges.
    """
    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)

    cryptos_data = crypto_service.search_cryptos(search=search)

    return paginate(cryptos_data)


@router.get("/cryptos/symbols", status_code=status.HTTP_200_OK)
@limiter.limit("50/minutes")
def get_crypto_symbols(
    request: Request,
    db: Session = Depends(get_db),
) -> List[CryptoSymbolSchema]:
    """
    Return all crypto symbols from exchanges.
    """
    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)

    cryptos_data = crypto_service.search_cryptos(search=None)

    return cryptos_data


@router.get("/cryptos/{symbol}/general", status_code=status.HTTP_200_OK)
@limiter.limit("50/minutes")
def get_crypto_general_details(
    request: Request, symbol: str, db: Session = Depends(get_db)
) -> CryptoBasicSchema:
    """
    Return detailed information about a specific crypto by its symbol.
    """
    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)
    crypto = crypto_service.get_crypto_by_symbol(symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Krypto z symbolem '{symbol}' nie zostało znalezione.",
        )

    return crypto


@router.get("/crypto/{symbol}/price-performance", status_code=status.HTTP_200_OK)
@limiter.limit("50/minutes")
def get_crypto_performance_details(
    symbol: str, request: Request, db: Session = Depends(get_db)
) -> CryptoPricePerformanceSchema:
    """
    Return price performance information about a specific crypto by its symbol.
    """
    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)
    crypto = crypto_service.get_crypto_by_symbol(symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Krypto z symbolem '{symbol}' nie zostało znalezione.",
        )

    return crypto


@router.get("/cryptos/{symbol}/historical", status_code=status.HTTP_200_OK)
@limiter.limit("50/minutes")
def get_crypto_historical_data(
    symbol: str,
    request: Request,
    period: Literal["1h", "1d", "1w", "1m", "1y", "max"] = Query(
        "1w",
        description="Period for historical data.",
    ),
    db: Session = Depends(get_db),
) -> List[CryptoHistoricalPriceSchema]:
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol jest wymagany.",
        )
    if period not in [
        "1h",
        "1d",
        "1w",
        "1m",
        "1y",
        "max",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy okres. Dostępne okresy to 1h, 1d, 1w, 1m, 1y, max,",
        )

    crypto_repository = CryptoRepository(db_session=db)
    crypto_service = CryptoService(repository=crypto_repository)
    if period == "max":
        historical_data = (
            crypto_service.get_crypto_historical_by_symbol_data_from_last_max(
                symbol=symbol
            )
        )
    else:
        historical_data = (
            crypto_service.get_crypto_historical_by_symbol_period_data_from_last(
                symbol=symbol, period=period
            )
        )

    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brak danych historycznych dla kryptowaluty z symbolem '{symbol}' w okresie '{period}'.",
        )

    return historical_data


@router.get("/currencies/pair-rates", status_code=status.HTTP_200_OK)
@limiter.limit("50/minutes")
def get_currency_pair_rate(
    request: Request,
    db: Session = Depends(get_db),
) -> List[CurrencyPairRateSchema]:
    """
    Return current exchange rates for multiple currency pairs.
    """
    currency_repository = CurrencyPairRateRepository(db_session=db)
    currency_service = CurrencyService(repository=currency_repository)

    pair_rate = currency_service.get_currency_pair_rates()

    if pair_rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nie znaleziono kursów wymiany dla podanych par walut.",
        )

    return pair_rate
