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
    stock_info_list = []
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
                    print(symbol)
                    stock_info = yf.Ticker(symbol).info

                    stock_info['Org'] = org_name
                    stock_info['Symbol'] = symbol
                    stock_info_list.append(stock_info)
                else:
                    # If name can't be found pass.
                    pass
            except:
                # Don't raise an error.
                pass

    output_df = pd.DataFrame(stock_info_list)
    return output_df


# Add input field input field
user_input = st.text_input(
    "Add rss link here", "https://www.investing.com/rss/news.rss")

# Get financial headlines
fin_headings = extract_rss(user_input)


output_df = stock_info(fin_headings)

output_df = output_df[['Org', 'Symbol', 'currentPrice',
                       'dayHigh', 'dayLow', 'forwardPE', 'dividendYield']]
output_df.drop_duplicates(inplace=True, subset='Symbol')
st.dataframe(output_df)


with st.expander("Expand for stocks news"):
    for heading in fin_headings:
        heading = heading.text
        if type(heading) == str:
            st.markdown("* " + heading)
