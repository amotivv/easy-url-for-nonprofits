# Nonprofit QR Shortener

This is a Flask-based web application that allows nonprofit organizations to register and generate shortened URLs and QR codes for their donation pages. The app also logs redirection events for future analysis.

The app uses an external service called CharityAPI.org (https://www.charityapi.org/) to validate the non-profit EINs. Get your API key and plug it into the .env file.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [/register](#register)
  - [/login](#login)
  - [/<short_url>](#short_url)
- [Todo](#todo)

## Installation

1. Clone the repository
2. Create a virtual environment for the app using `python -m venv venv`
3. Activate the virtual environment using `source venv/bin/activate` on Unix/MacOS or `venv\Scripts\activate` on Windows.
4. Install the required packages using `pip install -r requirements.txt`
5. Set up your `.env` file with the required configuration variables (example provided in the `.env.example` file)
6. Run the Flask app using `flask run`


## Usage

Use the provided API endpoints to register nonprofits, generate short URLs and QR codes, and redirect users to the long URLs.

## API Endpoints

### /register

- Method: POST
- Description: Register a new nonprofit organization
- Sample cURL command:

  ```bash
  curl -X POST "http://localhost:5000/register" -H "Content-Type: application/json" -d '{"name": "Test Nonprofit", "email": "test@example.com", "password": "test_password", "long_url": "https://example.com/donate", "ein": "12-3456789"}'
  ```

### /login

- Method: POST
- Description: Authenticate the nonprofit and return a JWT token (Not implemented yet)

### /<short_url>

- Method: GET
- Description: Redirects the user to the long URL associated with the short URL
- Sample cURL command:

  ```bash
  curl -X GET "http://localhost:5000/abcdefgh"
  ```

### Todo
- Implement the /login endpoint for user authentication and JWT token generation.

