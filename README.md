# Gourmet Burger Shop REST API

A robust, serverless RESTful API built using **Azure Functions (Python v2 model)** for the Cloud Computing Midterm project. This application manages a gourmet burger inventory entirely in application memory and enforces secure API key authentication via HTTP request headers.

---

## Features & Requirements Met

- **In-Memory Repository:** Uses a volatile Python dictionary structure to handle fast data storage and management without requiring a permanent database for the midterm phase.
- **Full CRUD Operations:** Supports creating, reading, updating, and deleting burger resources.
- **API Key Authentication:** Secures endpoints by inspecting the incoming `x-api-key` header against configuration settings.
- **Robust Error Handling:** Features a custom exception-driven pattern wrapped in a Python decorator (`@handle_exceptions`) to cleanly catch malformed JSON payloads and unexpected server errors, returning proper HTTP status codes (`200`, `201`, `400`, `401`, `404`, `405`, `500`).
- **Cloud-Ready:** Designed to run locally using Azure Functions Core Tools and Azurite storage emulation, with seamless deployment capability to Microsoft Azure.

---

## Tech Stack

- **Language:** Python 3.x
- **Framework:** Azure Functions (v2 Programming Model)
- **Local Emulator:** Azurite (Storage Emulator required by runtime)
- **API Testing Tool:** Thunder Client / Postman

---

## Project Structure

```text
burger-api/
│
├── function_app.py        # Main application logic, routes, and decorators
├── local.settings.json    # Local environment variables and API keys
├── requirements.txt       # Python package dependencies
└── host.json              # Azure Functions host configuration
```

---

## Getting Started Locally

### Prerequisites
Make sure you have the following installed on your machine:
- Python (version 3.8 or higher)
- Visual Studio Code with the Azure Functions extension
- Azure Functions Core Tools (`func`)

### 1. Configure Local Settings
Create a file named `local.settings.json` in your project root folder to hold your local environment secrets (be sure to use your own secure placeholder/key):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "API_KEY": "your-secure-api-key-here"
  }
}
```

### 2. Run the Function Locally
1. Open your project folder in VS Code.
2. Press **F5** or run the following command in your terminal:
   ```bash
   func start
   ```
3. Note the local endpoint URL output in your terminal (typically `http://localhost:7071/api/burgers`).

---

## API Endpoints & Reference

Every request sent to the API **must** include your API key header:
- **Header Name:** `x-api-key`
- **Header Value:** `your-secure-api-key-here` (Matching your `local.settings.json`)

| HTTP Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/burgers` | Retrieve all burgers in memory | **200 OK**, **401 Unauthorized** |
| **POST** | `/api/burgers` | Create a new burger | **201 Created**, **400 Bad Request**, **401** |
| **PUT** | `/api/burgers?id={id}` | Update an existing burger by ID | **200 OK**, **400**, **404 Not Found**, **401** |
| **DELETE** | `/api/burgers?id={id}` | Remove a burger by ID | **200 OK**, **400**, **404 Not Found**, **401** |

---

## How to Use and Structure Requests

When testing your API using REST clients like Thunder Client or Postman, structure your requests according to the guidelines below.

### 1. Required Header for All Requests
In your HTTP client, navigate to the **Headers** tab and include your authentication key:
- `x-api-key`: `your-secure-api-key-here`

For requests that send data (like `POST` and `PUT`), also include:
- `Content-Type`: `application/json`

---

### 2. GET Request (Read All Burgers)
- **Method:** `GET`
- **URL:** `http://localhost:7071/api/burgers`
- **Body:** None

---

### 3. POST Request (Create a Burger)
- **Method:** `POST`
- **URL:** `http://localhost:7071/api/burgers`
- **Body (JSON):** Must include at least `name` and `price`.
  ```json
  {
    "name": "Volcano Jalapeno Crunch",
    "category": "Spicy",
    "price": 12.50,
    "ingredients": ["Beef", "Pepper Jack", "Jalapenos", "Spicy Aioli"],
    "isSpicy": true
  }
  ```

---

### 4. PUT Request (Update an Existing Burger)
- **Method:** `PUT`
- **URL:** `http://localhost:7071/api/burgers?id=<INSERT_BURGER_UUID_HERE>`
- **Body (JSON):** Include the fields you want to update (all fields are optional; unpassed fields remain unchanged).
  ```json
  {
    "price": 14.00,
    "category": "Ultra Spicy"
  }
  ```

---

### 5. DELETE Request (Remove a Burger)
- **Method:** `DELETE`
- **URL:** `http://localhost:7071/api/burgers?id=<INSERT_BURGER_UUID_HERE>`
- **Body:** None