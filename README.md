# Stock Alert System

This project is a Python-based stock alert system that monitors the price of specified stock tickers and sends email notifications when a significant price drop occurs. It leverages the Twelve Data API for stock data and SendGrid for email delivery.

## Features

*   **Price Drop Monitoring:**  Continuously monitors the price of specified stocks (e.g., BTC/USD, AAPL, TSLA, GOOGL, AMZN).
*   **Email Notifications:** Sends email alerts via SendGrid when the price of a stock drops by a defined percentage within a 72-hour window.
*   **Email Logging:** Tracks which alerts have already been sent for a given day to avoid redundant notifications.
*   **Scheduled Execution:** Runs automatically using GitHub Actions.
*   **Environment Variable Configuration:** Uses environment variables for sensitive information like API keys and email credentials.

## Prerequisites

*   **Twelve Data API Key:**  You'll need an API key from [Twelve Data](https://twelvedata.com/).  Sign up for an account and obtain your API key.
*   **SendGrid API Key:**  You'll need an API key from [SendGrid](https://sendgrid.com/).  Sign up for an account and obtain your API key.
*   **GitHub Account:** Required to host the repository and set up GitHub Actions.

## Setup and Installation

1.  **Clone the Repository:**

    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <YOUR_REPOSITORY_DIRECTORY>
    ```

2.  **Install Dependencies:**

    ```bash
    pip install requests pytz sendgrid
    ```

3.  **Configure Environment Variables:**

    You need to set the following environment variables:

    *   `TWELVE_DATA_API_KEY`: Your Twelve Data API key.
    *   `SENDGRID_API_KEY`: Your SendGrid API key.
    *   `SENDGRID_FROM_EMAIL`: The email address you'll use to send the alerts from (must be a verified sender in SendGrid).
    *   `SENDGRID_RECIPIENTS`: A comma-separated list of email addresses that will receive the alerts.

    **Important:** For a public GitHub repository, *do not* hardcode these values directly into the `stockAlertCode.py` file. Instead, configure them as GitHub Actions secrets (see "GitHub Actions Setup" below).

4.  **GitHub Actions Setup:**

    *   Go to your repository on GitHub.
    *   Navigate to "Settings" -> "Secrets" -> "Actions".
    *   Add the following secrets, using the names exactly as shown:
        *   `TWELVE_DATA_API_KEY`:  Set this to your Twelve Data API key.
        *   `SENDGRID_API_KEY`: Set this to your SendGrid API key.
        *   `SENDGRID_FROM_EMAIL`: Set this to your SendGrid "from" email address.
        *   `SENDGRID_RECIPIENTS`: Set this to the comma-separated list of recipient email addresses.
        *   `GITHUB_TOKEN`: GitHub automatically provides this, so you don't need to create it.  It's used for committing changes to the repository.

5.  **Configure the Tickers and Drop Percentage (Optional):**

    You can modify the `tickers_of_interest` list and `drop_percentage` variable in the `stockAlertCode.py` file to customize the stocks being monitored and the threshold for price drop alerts.

    ```python
    tickers_of_interest = ['BTC/USD', 'AAPL', 'TSLA', 'GOOGL', 'AMZN']
    drop_percentage = 7.5
    ```

## Running the Script

The script is designed to be run automatically using GitHub Actions.  The provided `.github/workflows/main.yml` file defines a workflow that:

*   Checks out the repository.
*   Sets up Python.
*   Installs the required dependencies.
*   Runs the `stockAlertCode.py` script.
*   Commits any changes to the `emails_sent.txt` file (to track sent alerts) and pushes them back to the repository.

The workflow is triggered by:

*   A scheduled cron job (currently set to run every 10 minutes).
*   Manual triggering via the "Workflow dispatch" option in the GitHub Actions tab.

## File Descriptions

*   `stockAlertCode.py`: The main Python script that fetches stock data, checks for price drops, and sends email alerts.
*   `emails_sent.txt`:  A log file that records the dates and tickers for which email alerts have already been sent.  This prevents duplicate alerts.
*   `.github/workflows/main.yml`:  The GitHub Actions workflow configuration file that defines the automated execution schedule and steps.

## Customization

*   **Tickers:**  Modify the `tickers_of_interest` list in `stockAlertCode.py` to monitor different stocks.
*   **Drop Percentage:**  Adjust the `drop_percentage` variable in `stockAlertCode.py` to change the sensitivity of the price drop alerts.
*   **Schedule:**  Modify the `cron` expression in `.github/workflows/main.yml` to change the frequency of the scheduled execution.  See [Crontab Guru](https://crontab.guru/) for help with cron syntax.
*   **Timezone:** The script is set to Berlin timezone. If you are in a different timezone, make sure to configure this where the timezone is set.

## Important Considerations

*   **Rate Limiting:** Be mindful of the API usage limits of the Twelve Data API.  Excessive requests may result in your API key being temporarily blocked.  Adjust the schedule accordingly.
*   **Error Handling:**  The script includes basic error handling, but you may want to add more robust error handling and logging for production use.
*   **Security:**  Protect your API keys and other sensitive information.  Never commit them directly to the repository.  Always use environment variables or secrets management.
*   **Email Sending Limits:** Be aware of the sending limits imposed by SendGrid.

## Disclaimer

This project is for informational and educational purposes only.  It is not financial advice.  Stock prices can be volatile, and you should consult with a qualified financial advisor before making any investment decisions.
