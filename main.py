from flask import Flask, jsonify, request
from flask_caching import Cache
import db

db.init_db()
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route("/")
def test():
    return "Service is up!"

# Retrieves all flags
@app.route("/flags")
def get_all_flags():
    return jsonify(db.get_all_feature_flags())

'''
# Allow creation of feature flags (e.g., name, description, default state)
Body format example : 
{
    "name": "flag_api_test_111", -- string
    "default_state": "enable", -- string, either 'enable' or 'disable'
    "enabled_users": [ 2 ] -- list of int
}
'''
@app.route("/flags", methods=['POST'])
def create_flag():
    data = request.get_json()
    print("Create flag: ", request.get_json())
    # Create flag and get its ID
    flag_id = db.add_feature_flag(data["name"])
    default_state = data["default_state"]

    errors = []
    if default_state == "enable":
        db.add_feature_flag_enabled_user(flag_id, -1)
    if len(data['enabled_users']) > 0:
        for user_id in data['enabled_users']:
            # TODO: validate user is real or add foreign key relation
            print(user_id)
            db.add_feature_flag_enabled_user(flag_id, user_id)

    return errors

'''
Allow enabling or disabling a feature for: All users (global default)
''' 
@app.route("/flag/<int:flag_id>/toggle/<state>", methods=['POST'])
def toggle_flag_global(flag_id, state):
    if state not in ["enable", "disable"]:
        return "error"

    if state == "disable":
        db.delete_feature_flag_enabled_user(flag_id, -1)
    else:
        db.add_feature_flag_enabled_user(flag_id, -1)
    print("Toggle flag global: ", flag_id, request.form)
    return ""

'''
Allow enabling or disabling a feature for: A specific user
''' 
@app.route("/flag/<flag_id>/toggle/<user_id>/<state>", methods=['POST'])
def toggle_flag_user(flag_id, user_id, state):
    if state not in ["enable", "disable"]:
        return "error"

    if state == "disable":
        db.delete_feature_flag_enabled_user(flag_id, user_id)
    else:
        db.add_feature_flag_enabled_user(flag_id, user_id)

    print("Toggle flag user: ", flag_id, request.form)
    return ""

# Evaluate whether a feature is enabled for a given user
@app.route("/flag/<int:flag_id>/evaluate/<int:user_id>")
@cache.cached(timeout=60) 
def evaluate_flag(flag_id, user_id):
    print("Evaluate ", flag_id, " for user ", user_id)
    flag = db.get_feature_flag_by_id(flag_id)

    evaluation = False
    if user_id in flag['enabled_users'] or flag["default_state"] == True:
        evaluation = True

    return jsonify({
        "evaluation": evaluation
    })
