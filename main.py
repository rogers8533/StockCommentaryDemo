import streamlit as st
import openai
import yfinance as yf
from datetime import datetime
import language_tool_python

# Set your OpenAI API key here
openai.api_key = 'PRIVATE KEY HERE'

# Global variable to store the commentary
draft_commentary = ""

def generate_commentary(stock_symbol, start_date, end_date):
    stock = yf.Ticker(stock_symbol)
    stock_info = stock.info
    stock_history = stock.history(start=start_date, end=end_date, interval="1d")

    prompt = f"Provide a fund commentary for {stock_symbol}.\n\n"
    prompt += f"Date Range: {start_date} to {end_date}\n\n"
    prompt += f"Recent Performance Metrics:\n"
    prompt += f"- Open: ${stock_history['Open'][0]:.2f}\n"
    prompt += f"- Close: ${stock_history['Close'][0]:.2f}\n"
    prompt += f"- High: ${stock_history['High'][0]:.2f}\n"
    prompt += f"- Low: ${stock_history['Low'][0]:.2f}\n"
    prompt += f"- Volume: {stock_history['Volume'][0]:,}\n"

    if 'dividendRate' in stock_info and stock_info['dividendRate'] is not None:
        prompt += f"- Dividend Rate: ${stock_info['dividendRate']:.2f}\n"

    if 'trailingAnnualReturn' in stock_info and stock_info['trailingAnnualReturn'] is not None:
        prompt += f"- Trailing Annual Return: {stock_info['trailingAnnualReturn'] * 100:.2f}%\n"

    if 'cash' in stock_info and stock_info['cash'] is not None:
        prompt += f"- Cash: ${stock_info['cash']:,}\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000
    )

    return response.choices[0].text.strip()

def spelling_grammar_check(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    corrected_text = language_tool_python.correct(text, matches)
    return corrected_text

def quality_control_check(text):
    # Implement your quality control checks here
    # You can check for specific keywords, sentiments, or other criteria
    # Return a boolean indicating whether the commentary meets the quality standards
    pass


def main():
    global draft_commentary

    st.title("Public Stock Commentary Generator")

    stock_symbol = st.text_input("Enter a stock symbol:", value='AAPL')

    start_date = st.date_input("Start Date", value=datetime.today().replace(day=1))
    end_date = st.date_input("End Date", value=datetime.now())

    if st.button("Generate Commentary"):
        draft_commentary = generate_commentary(stock_symbol, start_date, end_date)
        st.write("Generated Commentary:")
        st.write(draft_commentary)

    if st.button("Edit Commentary"):
        draft_commentary = st.text_area("Edit the commentary:", value=draft_commentary, height=200)
        st.write("Commentary edited.")

    if st.button("Check Spelling & Grammar"):
        corrected_commentary = spelling_grammar_check(draft_commentary)
        st.write("Spelling & Grammar Checked:")
        st.write(corrected_commentary)

    if st.button("Quality Control Check"):
        if quality_control_check(draft_commentary):
            st.write("Commentary meets quality standards.")
        else:
            st.write("Commentary does not meet quality standards. Please revise.")

    if st.button("Commit Commentary"):
        st.write("Commentary Committed!")

    # Add a "Reject Commentary & Re-run" button
    if st.button("Reject Commentary & Re-run"):
        draft_commentary = ""  # Clear the draft commentary
        st.write("Commentary Rejected. Re-running...")

    # Display sources used to pull financial data
    st.subheader("Sources:")
    st.write("- Financial data pulled from Yahoo Finance using the yfinance library.")
    st.write("- OpenAI's GPT-3 used for generating commentary based on the provided prompts.")

if __name__ == "__main__":
    main()
