import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import streamlit as st

def extract_price(text):
    match = re.search(r'\$?([0-9,.]+)([KkMm]?)', text)
    if match:
        value = float(match.group(1).replace(',', ''))
        if match.group(2).lower() == 'k':
            value *= 1_000
        elif match.group(2).lower() == 'm':
            value *= 1_000_000
        return value
    return None

def scrape_boat_prices(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    prices = []
    for price_tag in soup.find_all(class_="price-class"):
        price = extract_price(price_tag.text)
        if price is not None:
            prices.append(price)
    return prices

def categorize_prices(price_list, price_bands):
    counts = {band: 0 for band in price_bands.keys()}
    for price in price_list:
        for band, (low, high) in price_bands.items():
            if low <= price < high:
                counts[band] += 1
                break
    return counts

def main():
    st.title("Boat Price Analyzer")
    
    url = st.text_input("Enter boat listing URL:")
    
    price_bands = {
        "Under $10K": (0, 10_000),
        "$10K-$25K": (10_000, 25_000),
        "$25K-$50K": (25_000, 50_000),
        "$50K-$75K": (50_000, 75_000),
        "$75K-$100K": (75_000, 100_000),
        "$100K-$250K": (100_000, 250_000),
        "$250K-$500K": (250_000, 500_000),
        "$500K-$1M": (500_000, 1_000_000),
        "$1M+": (1_000_000, float('inf'))
    }
    
    if url:
        prices = scrape_boat_prices(url)
        counts = categorize_prices(prices, price_bands)
        
        df = pd.DataFrame(list(counts.items()), columns=["Price Band", "Number of Boats"])
        
        st.write("### Price Breakdown")
        st.dataframe(df)
    
if __name__ == "__main__":
    main()
