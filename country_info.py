# country_info.py
from zeep import Client, helpers
from flask import Flask, jsonify
import re

# ------------------------------------------------------------------
# 1️⃣ Define the WSDL URL – this is the contract that describes the API.
WSDL_URL = "https://footballpool.dataaccess.eu/info.wso?WSDL"

# 2️⃣ Create a Zeep client. Internally it parses the WSDL and builds stubs.
client = Client(wsdl=WSDL_URL)


# ------------------------------------------------------------------
def validate_player_name(player_name):
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("Player name must be a non-empty string.")

    player_name = player_name.strip()

    if len(player_name) < 2 or len(player_name) > 50:
        raise ValueError("Player name must be between 2 and 50 characters long.")

    if not re.fullmatch(r"[A-Za-z\s\-]+", player_name):
        raise ValueError("Player name can only contain letters, spaces, and hyphens.")

    return player_name


def get_player_details(player_name):
    """
    Calls the Football Pool SOAP operation
    and returns the results.
    """
    # Validate the player name
    player_name = validate_player_name(player_name)

    # Call the SOAP operation – Zeep returns a custom object.
    player_results = client.service.Players(player_name)

    # Convert the Zeep object into a plain dict for easier use.
    player_data = helpers.serialize_object(player_results)

    return player_data


# Create a Flask app
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Football Pool SOAP API is running. Use the /player/<name> endpoint to get player details."


# GET route
@app.route("/players", methods=["GET"])
def get_players():
    """
    GET route to retrieve player details.
    Expects a query parameter 'name' for the player's name.
    """
    from flask import request

    player_name = request.args.get("name")
    if not player_name:
        return jsonify({"error": "Missing 'name' query parameter."}), 400

    try:
        player_data = get_player_details(player_name)
        return jsonify(player_data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as exc:
        return jsonify({"error": f"Something went wrong: {exc}"}), 500


# POST route
@app.route("/players", methods=["POST"])
def post_players():
    """
    POST route to retrieve player details.
    Expects a JSON body with a 'name' field for the player's name.
    """
    from flask import request

    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing 'name' in JSON body."}), 400

    player_name = data["name"]

    try:
        player_data = get_player_details(player_name)
        return jsonify(player_data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as exc:
        return jsonify({"error": f"Something went wrong: {exc}"}), 500


# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
