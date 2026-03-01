import requests
from bs4 import BeautifulSoup
import pandas as pd


def scrape_fuelo_week(year: int, month: int):

    url = f"https://fuelo.net/calendar/week/{year}/{month:02d}?lang=bg"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("div.table-row")

    # ---- HEADER ----
    header = [col.get_text(strip=True) for col in rows[0].find_all("div")]

    data = []

    # ---- DATA ----
    for row in rows[1:]:
        cols = [col.get_text(strip=True) for col in row.find_all("div")]
        data.append(cols)

    df = pd.DataFrame(data, columns=header)

    # ---- CLEAN PRICES ----
    price_cols = df.columns[2:]  # всички ценови колони

    for col in price_cols:
        df[col] = (
            df[col]
            .str.replace("€/л", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )


    df["№"] = pd.to_numeric(df["№"], errors="coerce")
    df = df.dropna(subset=["№"])
    df["№"] = df["№"].astype(int)

    return df


all_data = []

for year in range(2020, 2026):
    for month in range(1, 13):
        try:
            df_month = scrape_fuelo_week(year, month)

            if not df_month.empty:
                all_data.append(df_month)

        except Exception as e:
            print(f"Error for {year}-{month:02d}: {e}")

# Обединяваме всичко
final_df = pd.concat(all_data, ignore_index=True)

print(final_df.head())
print(final_df.shape)

final_df.to_csv(
    "fuelo_week_prices_2020_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

print("CSV saved successfully.")