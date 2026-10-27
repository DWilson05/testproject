import json
import uuid
import os
import functools
import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

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

def handle_exceptions(func_to_wrap):
    @functools.wraps(func_to_wrap)
    def wrapper(*args, **kwargs):
        try:
            return func_to_wrap(*args, **kwargs)
        except ValueError as e:
            logging.warning(f"Bad request payload error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Bad Request: Malformed or invalid JSON payload."}),
                status_code=400,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Internal server error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": f"Internal Server Error: {str(e)}"}),
                status_code=500,
                mimetype="application/json"
            )
    return wrapper

def authorize_request(req: func.HttpRequest) -> bool:
    expected_key = os.environ.get("API_KEY", "fallback-default-key")
    client_key = req.headers.get("x-api-key")
    return client_key == expected_key

@app.route(route="burgers", methods=["GET", "POST", "PUT", "DELETE"])
@handle_exceptions
def manage_burgers(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Burger Shop API processing request.')

    if not authorize_request(req):
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized: Missing or invalid API key in 'x-api-key' header."}),
            status_code=401,
            mimetype="application/json"
        )

    method = req.method
    burger_id = req.params.get("id")

    if method == "GET":
        return func.HttpResponse(
            json.dumps(list(burgers_db.values())),
            status_code=200,
            mimetype="application/json"
        )

    elif method == "POST":
        req_body = req.get_json()
        
        if not req_body or "name" not in req_body or "price" not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Bad Request: 'name' and 'price' are required fields."}),
                status_code=400,
                mimetype="application/json"
            )

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
        return func.HttpResponse(
            json.dumps(new_burger),
            status_code=201,
            mimetype="application/json"
        )

    elif method == "PUT":
        if not burger_id:
            return func.HttpResponse(
                json.dumps({"error": "Bad Request: Missing 'id' query parameter (e.g., /api/burgers?id=1)."}),
                status_code=400,
                mimetype="application/json"
            )
        
        if burger_id not in burgers_db:
            return func.HttpResponse(
                json.dumps({"error": "Not Found: Burger ID does not exist."}),
                status_code=404,
                mimetype="application/json"
            )

        req_body = req.get_json()
        existing = burgers_db[burger_id]
        
        existing["name"] = req_body.get("name", existing["name"])
        existing["category"] = req_body.get("category", existing["category"])
        existing["price"] = float(req_body.get("price", existing["price"]))
        existing["ingredients"] = req_body.get("ingredients", existing["ingredients"])
        existing["isSpicy"] = req_body.get("isSpicy", existing["isSpicy"])

        burgers_db[burger_id] = existing
        return func.HttpResponse(
            json.dumps(existing),
            status_code=200,
            mimetype="application/json"
        )

    elif method == "DELETE":
        if not burger_id:
            return func.HttpResponse(
                json.dumps({"error": "Bad Request: Missing 'id' query parameter for deletion."}),
                status_code=400,
                mimetype="application/json"
            )
        
        if burger_id not in burgers_db:
            return func.HttpResponse(
                json.dumps({"error": "Not Found: Burger ID does not exist."}),
                status_code=404,
                mimetype="application/json"
            )

        deleted_burger = burgers_db.pop(burger_id)
        return func.HttpResponse(
            json.dumps({"message": "Burger successfully deleted", "burger": deleted_burger}),
            status_code=200,
            mimetype="application/json"
        )

    return func.HttpResponse("Method not allowed", status_code=405)