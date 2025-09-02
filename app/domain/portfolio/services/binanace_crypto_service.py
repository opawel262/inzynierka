from typing import List, Dict, Any
from app.domain.portfolio.fetchers.crypto_fetchers import BinanaceCryptoFetcher
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.schemas.crypto_historical_schemas import (
    CryptoHistoricalPriceSchema,
)

from app.domain.portfolio.repositories.currency_repository import (
    CurrencyPairRateRepository,
)


class BinanaceCryptoService:
    def __init__(
        self,
        fetcher: BinanaceCryptoFetcher,
        repository: CryptoRepository,
        pair_rate_repository: CurrencyPairRateRepository,
    ):
        self.fetcher = fetcher
        self.pair_rate_repository = pair_rate_repository
        self.repository = repository

    def fetch_and_save_historical_crypto_data(self):
        cryptos = self.repository.get_all_cryptos()
        historical_data_list = []
        usd_to_pln = self.pair_rate_repository.get_currency_pair_rate_by_quote_and_base(
            "PLN", "USD"
        )
        for crypto in cryptos:
            historical_data = self.fetcher.fetch_historical_crypto_data(
                crypto.symbol, usd_to_pln.rate
            )
            historical_data_list.append(historical_data)
            percentaged_calculated_1m = False
            percentaged_calculated_1y = False
            percentaged_calculated_max = False
            if not historical_data:
                continue
            price_change_percentage_dict = {"symbol": crypto.symbol}
            for i, data_point in enumerate(historical_data, start=1):

                validated_data = CryptoHistoricalPriceSchema(**data_point).model_dump()

                if not percentaged_calculated_1m and validated_data["period"] == "1m":
                    price_change_percentage = self.calculate_percentage_price_change(
                        old_price=validated_data["open_price"], new_price=crypto.price
                    )

                    price_change_percentage_dict["price_change_percentage_30d"] = (
                        price_change_percentage
                    )
                    percentaged_calculated_1m = True
                elif not percentaged_calculated_1y and validated_data["period"] == "1y":
                    price_change_percentage = self.calculate_percentage_price_change(
                        old_price=validated_data["open_price"], new_price=crypto.price
                    )
                    price_change_percentage_dict["price_change_percentage_1y"] = (
                        price_change_percentage
                    )
                    percentaged_calculated_1y = True
                elif (
                    not percentaged_calculated_max and validated_data["period"] == "max"
                ):
                    price_change_percentage = self.calculate_percentage_price_change(
                        old_price=validated_data["open_price"], new_price=crypto.price
                    )
                    price_change_percentage_dict["price_change_percentage_max"] = (
                        price_change_percentage
                    )
                    percentaged_calculated_max = True

                if self.repository.get_crypto_historical_prices_by_symbol_period_date(
                    symbol=crypto.symbol,
                    period=validated_data["period"],
                    date=validated_data["date"],
                ):
                    continue
                self.repository.create_crypto_historical_price(crypto, validated_data)

            self.repository.update_crypto(price_change_percentage_dict)

        return {}

    @staticmethod
    def calculate_percentage_price_change(old_price: float, new_price: float) -> float:
        """
        Calculate the percentage change between the old and new price.
        """
        if old_price == 0:
            return 0
        return ((new_price - old_price) / old_price) * 100
