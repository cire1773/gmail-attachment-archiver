# Gmail to Drive Archiver

A configurable ETL (Extract, Transform, Load) automation tool built with Python. It interfaces with Gmail and Google Drive APIs to query emails based on specific timeframes and file types, extracting attachments and organizing them into cloud storage automatically.

## Features

* **Smart Filtering:** Download attachments based on file extensions (PDF, JPG, PNG, etc.) defined in your configuration.
* **Duplicate Prevention:** Checks if a file already exists in the destination folder before uploading.
* **Secure:** Uses OAuth 2.0 for authentication and environment variables to keep credentials safe.
* **Cross-Platform:** Works on Windows, macOS, and Linux.

## Prerequisites

* Python 3.8 or higher
* A Google Cloud Platform project with Gmail and Drive APIs enabled.

## Installation

1.  **Clone the repository**
    Choose your preferred method:

    * **Option A: HTTPS (Recommended for most users)**
        ```bash
        git clone [https://github.com/cire1773/gmail-attachment-archiver.git](https://github.com/cire1773/gmail-attachment-archiver.git)
        ```

    * **Option B: SSH (For users with SSH keys configured)**
        ```bash
        git clone git@github.com:cire1773/gmail-attachment-archiver.git
        ```

    Then, navigate into the project folder:
    ```bash
    cd gmail-attachment-archiver
    ```

2.  **Create a Virtual Environment**
    It is recommended to use a virtual environment to isolate dependencies.

    * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Google Cloud Credentials**
    To run this script, you need a `client_secret.json` file from Google.
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  Create a new project.
    3.  **Enable APIs:** Go to "APIs & Services" > "Library" and enable **Gmail API** and **Google Drive API**.
    4.  **Consent Screen:** Go to "OAuth consent screen", choose "External", and create. Add your own email as a "Test User".
    5.  **Create Credentials:** Go to "Credentials" > "Create Credentials" > "OAuth client ID".
    6.  Choose "Desktop app" as the application type.
    7.  Download the JSON file, rename it to `client_secret.json`, and place it in a secure folder on your computer.

2.  **Environment Variables**
    Create a file named `.env` in the project root. Add the following configuration, adjusting the paths for your operating system:

    **Windows Example:**
    ```properties
    # Path to the credentials file you just downloaded
    CLIENT_SECRET_PATH=C:/Users/YourName/Documents/client_secret.json
    
    # Path where the script will save the generated token (files will be created automatically)
    GMAIL_CREDENTIALS_PATH=C:/Users/YourName/Documents/gmail_token.json

    # Search query for emails (follows standard Gmail search operators)
    GMAIL_SEARCH_QUERY=has:attachment after:2024/01/01 before:2024/02/01

    # Allowed file extensions (comma-separated, case-insensitive)
    ALLOWED_EXTENSIONS=.pdf,.jpg,.jpeg,.png
    ```

    **macOS / Linux Example:**
    ```properties
    CLIENT_SECRET_PATH=/Users/yourname/Documents/client_secret.json
    GMAIL_CREDENTIALS_PATH=/Users/yourname/Documents/gmail_token.json
    GMAIL_SEARCH_QUERY=has:attachment after:2024/01/01 before:2024/02/01
    ALLOWED_EXTENSIONS=.pdf,.jpg,.png
    ```

## Usage

Run the script from your terminal:

```bash
python script.py