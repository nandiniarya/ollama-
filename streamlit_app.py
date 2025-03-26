import streamlit as st

st.title("Streamlit App")




pip install yfinance


!pip install yfinance


import yfinance as yf
import pandas as pd
import numpy as np

from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PagedCSVReader
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore


!pip install llama-index pandas numpy yfinance chromadb


import yfinance as yf

def get_financial_ratios(ticker):
    try:
        stock = yf.Ticker(ticker)

        # Fetch financial statements
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow

        # Debugging: Print available keys
        print("Available financials keys:", financials.index)
        print("Available balance sheet keys:", balance_sheet.index)
        print("Available cash flow keys:", cashflow.index)

        # Function to safely retrieve values
        def get_value(df, key):
            if key in df.index:
                return df.loc[key].iloc[0]  # Use .iloc[0] to get the latest value
            return None

        # Extract required values safely
        revenue = get_value(financials, "Total Revenue")
        net_income = get_value(financials, "Net Income")
        total_assets = get_value(balance_sheet, "Total Assets")
        total_liabilities = get_value(balance_sheet, "Total Liabilities Net Minority Interest")
        stockholders_equity = get_value(balance_sheet, "Stockholders Equity")  # ✅ FIXED KEY
        invested_capital = get_value(balance_sheet, "Invested Capital")  # ✅ FIXED KEY
        ebit = get_value(financials, "EBIT")
        operating_cashflow = get_value(cashflow, "Operating Cash Flow")  # ✅ FIXED KEY
        total_debt = get_value(balance_sheet, "Total Debt")  # ✅ FIXED KEY
        current_assets = get_value(balance_sheet, "Current Assets")
        current_liabilities = get_value(balance_sheet, "Current Liabilities")

        # Compute new ratios with fallbacks
        ratios = {
            "ROIC (%)": (net_income / invested_capital) * 100 if net_income and invested_capital else "Data Unavailable",
            "ROA (%)": (net_income / total_assets) * 100 if net_income and total_assets else "Data Unavailable",
            "Debt-to-Equity": total_liabilities / stockholders_equity if total_liabilities and stockholders_equity else "Data Unavailable",
            "Current Ratio": current_assets / current_liabilities if current_assets and current_liabilities else "Data Unavailable",
            "EBIT Margin (%)": (ebit / revenue) * 100 if ebit and revenue else "Data Unavailable",
            "Operating Cash Flow to Debt": operating_cashflow / total_debt if operating_cashflow and total_debt else "Data Unavailable"
        }

        return ratios

    except Exception as e:
        return {"Error": str(e)}

# Example usage
ticker = input("Enter the stock ticker (e.g., AAPL, TSLA): ")
print("\nFetching financial data...\n")
ratios = get_financial_ratios(ticker)
print("\nFinancial Ratios:")
for key, value in ratios.items():
    print(f"{key}: {value}")


def analyze_ratios_with_llm(ratios):
    prompt = f"""
    Given the following financial ratios, analyze the company's financial health and provide an investment recommendation:
    
    - ROIC: {ratios.get("ROIC (%)", "N/A")}%
    - ROA: {ratios.get("ROA (%)", "N/A")}%
    - Debt-to-Equity: {ratios.get("Debt-to-Equity", "N/A")}
    - Current Ratio: {ratios.get("Current Ratio", "N/A")}
    - EBIT Margin: {ratios.get("EBIT Margin (%)", "N/A")}%
    - Operating Cash Flow to Debt: {ratios.get("Operating Cash Flow to Debt", "N/A")}

    Based on these metrics, should an investor consider buying, holding, or selling this stock? Provide a short justification.
    """

    # Configure the LLM
    llm = Ollama(model="mistral")

    try:
        response = llm.complete(prompt)
        return response
    except Exception as e:
        return f"Error generating analysis: {str(e)}"


def main():
    ticker = input("Enter the stock ticker (e.g., AAPL, TSLA): ").strip().upper()
    
    print("\nFetching financial data...")
    ratios = get_financial_ratios(ticker)
    
    if "Error" in ratios:
        print("Error fetching data:", ratios["Error"])
        return

    print("\nFinancial Ratios:")
    for key, value in ratios.items():
        print(f"{key}: {value}")

    print("\nAnalyzing investment potential using LLM...")
    recommendation = analyze_ratios_with_llm(ratios)

    print("\nInvestment Recommendation:")
    print(recommendation)


if __name__ == "__main__":
    main()












