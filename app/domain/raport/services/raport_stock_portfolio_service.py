import pandas as pd
import plotly.express as px
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import base64
from io import BytesIO
from datetime import datetime


class RaportStockPortfolioService:
    def __init__(
        self,
        user_id: str = None,
        stock_portfolio_service=None,
    ):
        self.user_id = user_id
        self.stock_portfolio_service = stock_portfolio_service
        self.months_en_pl = {
            "January": "sty",
            "February": "lut",
            "March": "mar",
            "April": "kwi",
            "May": "maj",
            "June": "cze",
            "July": "lip",
            "August": "sie",
            "September": "wrz",
            "October": "paź",
            "November": "lis",
            "December": "gru",
        }

    def get_portfolio_summary(self):
        return self.stock_portfolio_service.get_portfolios_summary()

    def get_all_portfolios(self):
        return self.stock_portfolio_service.get_all_portfolios()

    def prepare_dataframe(self, data):
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["date", "value"])
        df["date"] = pd.to_datetime(df["date"])
        df["date"] = df["date"].dt.strftime("%d %B")
        for en, pl in self.months_en_pl.items():
            df["date"] = df["date"].str.replace(en, pl)
        return df

    @staticmethod
    def make_plot(df, title):
        fig = px.line(
            df,
            x="date",
            y="value",
            title=title,
            template="plotly_white",
            labels={"date": "Data", "value": "Wartość (PLN)"},
        )
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        fig.update_xaxes(nticks=10)
        fig.update_traces(line_color="#3c37ff")  # neon green
        img_bytes = fig.to_image(format="png", scale=2)
        return base64.b64encode(img_bytes).decode()

    def generate_report_pdf(self):
        portfolios = self.get_all_portfolios()
        positive_transactions = 0
        negative_transactions = 0
        positive_watched_stock = 0
        negative_watched_stock = 0
        watched_stocks = {}
        transactions = []
        for portfolio in portfolios:
            for tx in portfolio.stock_transactions:
                if tx.transaction_type == "sell":
                    continue
                transactions.append(tx)

                if tx.profit_loss >= 0:
                    positive_transactions += 1
                else:
                    negative_transactions += 1
            for stock in portfolio.watched_stocks:
                symbol = stock.stock.symbol
                if symbol in watched_stocks:
                    existing = watched_stocks[symbol]
                    existing["profit_loss"] = (
                        existing.get("profit_loss", 0) + stock.profit_loss
                    )
                else:
                    watched_stocks[symbol] = {"profit_loss": stock.profit_loss}

        for stock in watched_stocks.values():
            if stock.get("profit_loss", 0) >= 0:
                positive_watched_stock += 1
            else:
                negative_watched_stock += 1

        portfolio_summary = self.get_portfolio_summary()
        historical_value_7d = portfolio_summary.get("historical_value_7d", [])
        historical_value_1m = portfolio_summary.get("historical_value_1m", [])
        historical_value_1y = portfolio_summary.get("historical_value_1y", [])

        # Zamiana angielskich nazw miesięcy na polskie

        df_7d = self.prepare_dataframe(historical_value_7d)
        df_1m = self.prepare_dataframe(historical_value_1m)
        df_1y = self.prepare_dataframe(historical_value_1y)

        # --- Generowanie obrazków ---
        img_base64_7d = self.make_plot(
            df_7d, "Wartość portfela w ciągu ostatnich 7 dni"
        )
        img_base64_1m = self.make_plot(
            df_1m, "Wartość portfela w ciągu ostatniego miesiąca"
        )
        img_base64_1y = self.make_plot(
            df_1y, "Wartość portfela w ciągu ostatniego roku"
        )

        # 3️⃣ HTML z Jinja2
        holdings_percentage = list(
            portfolio_summary.get("holdings_percentage", {}).items()
        )
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("app/templates/raport/raport_stock_portfolio.html")
        html_content = template.render(
            now_data=datetime.now().strftime("%d %B %Y, %H:%M"),
            portfolio_value="15,200 PLN",
            chart_image_7d=f"data:image/png;base64,{img_base64_7d}",
            chart_image_1m=f"data:image/png;base64,{img_base64_1m}",
            chart_image_1y=f"data:image/png;base64,{img_base64_1y}",
            total_investment=portfolio_summary.get("total_investment", "0 PLN"),
            total_value=portfolio_summary.get("total_value", "0 PLN"),
            total_percentage_profit_loss_24h=portfolio_summary.get(
                "total_percentage_profit_loss_24h", "0%"
            ),
            total_profit_loss_24h=portfolio_summary.get(
                "total_profit_loss_24h", "0 PLN"
            ),
            total_profit_loss_percentage=portfolio_summary.get(
                "total_profit_loss_percentage", "0%"
            ),
            total_profit_loss=portfolio_summary.get("total_profit_loss", "0 PLN"),
            total_portfolios=portfolio_summary.get("total_portfolios", 0),
            total_transactions=portfolio_summary.get("total_transactions", 0),
            positive_transactions=positive_transactions,
            negative_transactions=negative_transactions,
            positive_watched_stock=positive_watched_stock,
            negative_watched_stock=negative_watched_stock,
            holdings_percentage=holdings_percentage,  # lista (nazwa, procent)
        )
        # 4️⃣ PDF do pamięci (in-memory)
        pdf_io = BytesIO()
        HTML(string=html_content).write_pdf(pdf_io)
        pdf_io.seek(0)
        return pdf_io
