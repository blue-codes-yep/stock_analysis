import requests
import spacy
import pandas as pd
import yfinance as yf
import streamlit as st
from bs4 import BeautifulSoup


st.title("Fire stocks :fire:")
nlp = spacy.load("en_core_web_sm")


def extract_rss(rss_link):
    # Parses xml, and extracts the headings.
    headings = []
    response1 = requests.get(
        "http://feeds.marketwatch.com/marketwatch/marketpulse/")
    response2 = requests.get(rss_link)
    parse1 = BeautifulSoup(response1.content, features="xml")
    parse2 = BeautifulSoup(response2.content, features="xml")
    headings1 = parse1.findAll('title')
    headings2 = parse2.findAll('title')
    headings = headings1 + headings2
    return headings


def stock_info(headings):
    # Get the entities from each heading, link it with nasdaq data // if possible, and Extract market data with yfinance.
    stock_dict = {
        'Org': [],
        'Symbol': [],
        'currentPrice': [],
        'dayHigh': [],
        'dayLow': [],
        'forwardPE': [],
        'dividendYield': []
    }
    stocks_df = pd.read_csv("./data/nasdaq_screener_1658383327100.csv")
    for title in headings:
        doc = nlp(title.text)
        for ent in doc.ents:
            try:
                if stocks_df['Name'].str.contains(ent.text).sum():
                    symbol = stocks_df[stocks_df['Name'].str.contains(
                        ent.text)]['Symbol'].values[0]
                    org_name = stocks_df[stocks_df['Name'].str.contains(
                        ent.text)]['Name'].values[0]

                    # Recieve info from yfinance
                    stock_info = yf.Ticker(symbol).info
                    print(symbol)
                    stock_dict['Org'].append(org_name)
                    stock_dict['Symbol'].append(symbol)

                    stock_dict['currentPrice'].append(
                        stock_info['currentPrice'])
                    stock_dict['dayHigh'].append(stock_info['dayHigh'])
                    stock_dict['dayLow'].append(stock_info['dayLow'])
                    stock_dict['forwardPE'].append(stock_info['forwardPE'])
                    stock_dict['dividendYield'].append(
                        stock_info['dividendYield'])
                else:
                    # If name can't be found pass.
                    pass
            except:
                # Don't raise an error.
                pass

    output_df = pd.DataFrame.from_dict(stock_dict, orient='index')
    output_df = output_df.transpose()
    return output_df


# Add input field input field
user_input = st.text_input(
    "Add rss link here", "https://www.investing.com/rss/news.rss")

# Get financial headlines
fin_headings = extract_rss(user_input)

print(fin_headings)
# Output financial info
output_df = stock_info(fin_headings)
output_df.drop_duplicates(inplace=True, subset='Symbol')
st.dataframe(output_df)

with st.expander("Expand for stocks news"):
    for heading in fin_headings:
        if heading == str:
            st.markdown("* " + heading)
        else:
            pass
