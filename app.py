from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS 
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt



app= Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ""

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    
    

    def __init__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "firstname", "lastname", "username", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    ingredients = db.Column(db.String(), nullable=False)
    preperation = db.Column(db.String(), nullable=False)
    
    
    def __init__(self, title, ingredients, preperation):
        self.title = title
        self.ingredients = ingredients
        self.preperation = preperation
        
        
class RecipeSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "ingredients", "preperation")    

recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    firstname = post_data.get("firstname")
    lastname = post_data.get("lastname")
    username = post_data.get("username")
    password = post_data.get("password")

    username_check = db.session.query(User.username).filter(User.username == username).first()
    if username_check is not None:
        return jsonify("Username Taken")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

    record = User(firstname, lastname, username, hashed_password)
    db.session.add(record)
    db.session.commit()

    return jsonify("User Created Successfully")

@app.route("/user/get", methods=["GET"])
def get_users():
    users = db.session.query(User).all()
    return jsonify(users_schema.dump(users))

@app.route("/user/verified", methods=["POST"])
def verify_user():
    print(request.content_type)
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    stored_password = db.session.query(User.password).filter(User.username == username).all()
    

    if stored_password is None:
        return jsonify("User NOT Verified")

    return jsonify("User Verified")

@app.route("/recipe/add", methods=["POST"])
def add_recipe():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    title = post_data.get("title")
    ingredients = post_data.get("ingredients")
    preperation = post_data.get("preperation")

    

    new_recipe = Recipe(title, ingredients, preperation)
    db.session.add(new_recipe)
    db.session.commit()

    return jsonify("Recipe added successfully")


@app.route("/recipe/get", methods=["GET"])
def get_recipes():
    recipes = db.session.query(Recipe).all()
    return jsonify(recipes_schema.dump(recipes))

@app.route("/recipe/get/<username>", methods=["GET"])
def get_recipes_by_username(username):
    user = db.session.query(User).filter(User.username == username).first()
    recipes = db.session.query(Recipe).filter(Recipe.user == user).all()
    return jsonify(recipes_schema.dump(recipes))



    




    








if __name__ == "__main__":
    app.run(debug=True)