import json
import uuid
import os
import functools
import hmac
import azure.functions as func
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize the Azure Function App with anonymous HTTP authentication
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# In-memory database for burgers
burgers_db = {
    "1": {
        "id": "1",
        "name": "The Truffle Bacon Beast",
        "category": "Beef",
        "price": 14.99,
        "ingredients": ["Wagyu Beef", "Black Truffle Mayo", "Crispy Bacon", "Gruyere"],
        "isSpicy": False
    }
}

# Helper function to create HTTP responses with JSON content
def make_response(body, status_code=200):
    if not isinstance(body, str):
        body = json.dumps(body)
    return func.HttpResponse(
        body,
        status_code=status_code,
        mimetype="application/json"
    )

# Decorator to handle exceptions and return appropriate HTTP responses
def handle_exceptions(func_to_wrap):
    @functools.wraps(func_to_wrap)
    def wrapper(*args, **kwargs):
        try:
            return func_to_wrap(*args, **kwargs)
        except ValueError:
            logging.warning("Bad request payload error.")
            return make_response({"error": "Bad Request: Malformed or invalid JSON payload."}, 400)
        except Exception:
            logging.exception("Internal server error.")
            return make_response({"error": "Internal Server Error."}, 500)
    return wrapper

# Authorizing requests using an API key stored in Azure Key Vault
@functools.lru_cache(maxsize=1)
def get_expected_api_key() -> str:
    vault_url = os.environ.get("KEY_VAULT_URL")
    secret_name = os.environ.get("API_KEY_SECRET_NAME")
    if not vault_url or not secret_name:
        raise RuntimeError(
            "KEY_VAULT_URL and API_KEY_SECRET_NAME must be configured."
        )

    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    secret_value = secret_client.get_secret(secret_name).value
    if not secret_value:
        raise RuntimeError("The configured API key secret is empty.")
    return secret_value


def authorize_request(req: func.HttpRequest) -> bool:
    client_key = req.headers.get("x-api-key")
    if not client_key:
        return False
    return hmac.compare_digest(client_key, get_expected_api_key())

# Route for managing burgers with GET, POST, PUT, DELETE methods
@app.route(route="burgers", methods=["GET", "POST", "PUT", "DELETE"])
@handle_exceptions
def manage_burgers(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Burger Shop API processing request.')

    if not authorize_request(req):
        return make_response({"error": "Unauthorized: Missing or invalid API key in 'x-api-key' header."}, 401)

    method = req.method
    burger_id = req.params.get("id")

    if method == "GET":
        if burger_id:
            burger = burgers_db.get(burger_id)
            if burger is None:
                return make_response({"error": "Not Found: Burger ID does not exist."}, 404)
            return make_response(burger, 200)
        return make_response(list(burgers_db.values()), 200)

    elif method == "POST":
        req_body = req.get_json()
        
        if not req_body or "name" not in req_body or "price" not in req_body:
            return make_response({"error": "Bad Request: 'name' and 'price' are required fields."}, 400)

        new_id = str(uuid.uuid4())
        new_burger = {
            "id": new_id,
            "name": req_body.get("name"),
            "category": req_body.get("category", "Classic"),
            "price": float(req_body.get("price")),
            "ingredients": req_body.get("ingredients", []),
            "isSpicy": req_body.get("isSpicy", False)
        }
        
        burgers_db[new_id] = new_burger
        return make_response(new_burger, 201)

    elif method == "PUT":
        if not burger_id:
            return make_response({"error": "Bad Request: Missing 'id' query parameter (e.g., /api/burgers?id=1)."}, 400)
        
        if burger_id not in burgers_db:
            return make_response({"error": "Not Found: Burger ID does not exist."}, 404)

        req_body = req.get_json()
        existing = burgers_db[burger_id]
        
        existing["name"] = req_body.get("name", existing["name"])
        existing["category"] = req_body.get("category", existing["category"])
        existing["price"] = float(req_body.get("price", existing["price"]))
        existing["ingredients"] = req_body.get("ingredients", existing["ingredients"])
        existing["isSpicy"] = req_body.get("isSpicy", existing["isSpicy"])

        burgers_db[burger_id] = existing
        return make_response(existing, 200)

    elif method == "DELETE":
        if not burger_id:
            return make_response({"error": "Bad Request: Missing 'id' query parameter for deletion."}, 400)
        
        if burger_id not in burgers_db:
            return make_response({"error": "Not Found: Burger ID does not exist."}, 404)

        deleted_burger = burgers_db.pop(burger_id)
        return make_response({"message": "Burger successfully deleted", "burger": deleted_burger}, 200)

    return make_response("Method not allowed", 405)