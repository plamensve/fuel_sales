import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def scrape_fuelo_week(year: int, month: int):

    url = f"https://fuelo.net/calendar/week/{year}/{month:02d}?lang=bg"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("div.table-row")

    if not rows:
        return pd.DataFrame()

    header = [col.get_text(strip=True) for col in rows[0].find_all("div")]

    data = []

    for row in rows[1:]:
        cols = [col.get_text(strip=True) for col in row.find_all("div")]

        if cols and cols[0].isdigit():
            data.append(cols)

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=header)

    price_cols = df.columns[2:]

    for col in price_cols:
        df[col] = (
            df[col]
            .str.replace("€/л", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

    df["№"] = df["№"].astype(int)

    return df


all_data = []

start_year = 2020
current_year = datetime.now().year

for year in range(start_year, current_year + 1):
    for month in range(1, 13):

        df_month = scrape_fuelo_week(year, month)

        if df_month.empty:
            if year == current_year:
                break
            continue

        all_data.append(df_month)


final_df = pd.concat(all_data, ignore_index=True)

final_df.to_csv(
    "fuelo_week_prices_all.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Saved. Shape:", final_df.shape)