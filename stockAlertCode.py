import os
import requests
from datetime import datetime, timedelta
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Retrieve sensitive values from environment variables
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
# Split comma-separated emails into a list (and strip any extra whitespace)
SENDGRID_RECIPIENTS = [email.strip() for email in os.getenv("SENDGRID_RECIPIENTS", "").split(",")]

def send_email(subject, content):
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=SENDGRID_RECIPIENTS,
        subject=subject,
        plain_text_content=content)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def log_email(symbol):
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_entry = f"***  {symbol} {current_date}  ***\n"
    with open('emails_sent.txt', 'a') as file:
        file.write(log_entry)

def email_already_sent(symbol):
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_entry = f"***  {symbol} {current_date}  ***\n"
    try:
        with open('emails_sent.txt', 'r') as file:
            if log_entry in file.readlines():
                return True
    except FileNotFoundError:
        return False
    return False

def get_ticker_price(symbol):
    berlin_tz = pytz.timezone('Europe/Berlin')
    end_time = datetime.now(berlin_tz)
    print('\n***  ', symbol, '  ***')
    start_time = end_time - timedelta(hours=72)

    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&timezone=Europe/Berlin&start_date={start_time_str}&end_date={end_time_str}&apikey={TWELVE_DATA_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data.get('status') == 'ok':
        return data['values'], end_time, start_time
    else:
        print(f"Error fetching data for {symbol}: {data}")
        return None, None, None

def check_price_drop(ticker_data, symbol, drop_percentage, end_time, start_time):
    prices = [float(entry['close']) for entry in ticker_data]
    times = [entry['datetime'] for entry in ticker_data]
    
    latest_price = prices[0]
    max_price = max(prices)
    drop_percent = ((max_price - latest_price) / max_price) * 100
    
    if drop_percent > drop_percentage:
        max_price_index = prices.index(max_price)
        max_price_time = times[max_price_index]
        print(f"\nPrice dropped more than {drop_percentage}% from the maximum value in the last 72 hours.")
        print(f"Max Price: {max_price} at {max_price_time}, Latest Price: {latest_price}")

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Alert: {symbol} dropped more than {drop_percentage}%"
        content = (f"***  {symbol} {current_date}  ***\n"
                   f"{symbol} prices in the last 72 hours (first 3 and last 3 values):\n")
        
        for entry in ticker_data[:3]:
            timestamp = entry['datetime']
            close_price = float(entry['close'])
            content += f"{timestamp}, Price {symbol}: {close_price:.2f}\n"
        
        content += '...\n'
        
        for entry in ticker_data[-3:]:
            timestamp = entry['datetime']
            close_price = float(entry['close'])
            content += f"{timestamp}, Price {symbol}: {close_price:.2f}\n"
        
        content += (f"\nPrice dropped more than {drop_percentage}% from the maximum value in the last 72 hours.\n"
                    f"Max Price: {max_price} at {max_price_time}, Latest Price: {latest_price}")

        if not email_already_sent(symbol):
            send_email(subject, content)
            log_email(symbol)
        else:
            print(f"Not sending mail because an email has already been sent for this date and ticker: {symbol}")

if __name__ == "__main__":
    tickers_of_interest = ['BTC/USD', 'AAPL', 'TSLA', 'GOOGL', 'AMZN']
    drop_percentage = 7.5
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for symbol in tickers_of_interest:
        ticker_data, end_time, start_time = get_ticker_price(symbol)
        if ticker_data:
            print(f"\nLooking for a drop of {drop_percentage}% (Now: {current_time_str})...")
            print(f"\n{symbol} prices in the last 72 hours (first 3 and last 3 values):")
            
            for entry in ticker_data[:3]:
                timestamp = entry['datetime']
                close_price = float(entry['close'])
                print(f"Time: {timestamp}, {symbol} Price: {close_price:.2f}")
            
            print('...')
            
            for entry in ticker_data[-3:]:
                timestamp = entry['datetime']
                close_price = float(entry['close'])
                print(f"Time: {timestamp}, {symbol} Price: {close_price:.2f}")

            check_price_drop(ticker_data, symbol, drop_percentage=drop_percentage, end_time=end_time, start_time=start_time)
