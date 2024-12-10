from flask import Flask, render_template, url_for, session, flash, redirect
from forms import LoginForm, SignupForm, TravelForm, BuyForm
from models import Player, query_player_id, is_username_registered, register_player, get_all_airports_info, get_travel_time, update_player_time_left, update_player_current_airport, query_airport_coordinates, query_goods_info, query_player_inventory

app = Flask("__name__")
app.config.from_pyfile("config.py")

@app.route("/")
def index():
    return render_template("index.jinja")

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        player_id = query_player_id(form.username.data, form.password.data)

        # check if the player_id in the database
        if player_id is not None:
            player_info = Player(player_id).info
            session["player_info"] = player_info
            
            # check if the game is already over
            if player_info['time_left'] > 0:
                return redirect( url_for('info') )
            else:
                # game over
                return render_template("gameover.jinja")
        else:
            message = "Invalid Input: please try again"
            return render_template("login.jinja", message = message, form = form)
    
    return render_template("login.jinja", form = form)
    
@app.route("/signup", methods = ["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if is_username_registered(form.username.data):
            message = "This username has already been registered, please try another one."
            return render_template("signup.jinja", message = message, form = form)
        else:
            register_player(form.username.data, form.password.data)
            flash("Successfully signed up! Please log in.")
            return redirect( url_for("login") )
    elif form.confirm_password.errors:   
        error = form.confirm_password.errors
        return render_template("signup.jinja", error = error, form = form)

    return render_template("signup.jinja", form = form)

@app.route("/logout")
def logout():
    session.pop("player_info")
    return redirect( url_for("index") )

@app.route("/info")
def info():
    print(session["player_info"])
    return render_template("info.jinja")

@app.route("/travel", methods = ["GET", "POST"])
def travel():
    current_airport_ident = session["player_info"]["current_airport"]
    airports = get_all_airports_info(current_airport_ident)

    form = TravelForm()
    for airport in airports:
        if airport["ident"] == current_airport_ident:
            continue
        choice = (airport["ident"], airport["ident"])
        form.destination.choices.append(choice)

    if form.validate_on_submit():
        destination = form.destination.data
        travel_time = get_travel_time(current_airport_ident, destination)

        time_left = session["player_info"]["time_left"] - travel_time
        time_left = round(time_left, 2)

        # Update the player's time left and current_airport in the database
        update_player_time_left(session["player_info"]["id"], time_left)
        update_player_current_airport(session["player_info"]["id"], destination)
        
        if time_left > 0:
            # Update the player's time left and current airport in the session
            player_info = session["player_info"]    
            player_info["time_left"] = time_left
            player_info["current_airport"] = destination
            player_info["coordinates"] = query_airport_coordinates(destination)
            session["player_info"] = player_info

            return redirect( url_for('info') )
        else:
            # Game Over
            session.pop("player_info")
            return render_template("gameover.jinja")

    return render_template("travel.jinja", airports = airports, form = form)

@app.route("/store")
def store():
    
    player_inventory = query_player_inventory(session["player_info"]["id"], session["player_info"]["current_airport"])
    print(player_inventory)

    return render_template("store.jinja")

@app.route("/store/buy", methods=["GET", "POST"])
def buy():
    goods = query_goods_info(session["player_info"]["current_airport"])
    paired_goods_forms = []

    for item in goods:
        goods_info= {
            "id": item["goods_id"],
            "name": item["name"],
            "price": item["sell_price"],
            "stock": item["stock"]
        } 
    
        # create a buy form for each goods
        form = BuyForm(prefix=f"buy_{item['goods_id']}")
        form.goods_id.data = item["goods_id"]

        # pair the goods_info and input form together
        paired_goods_forms.append((goods_info, form))

    for goods_info, form in paired_goods_forms:
        if form.submit.data and form.validate_on_submit():
            goods_id = form.goods_id.data
            quantity = form.number.data
            
            print("Submitted!")
            print(f"Goods ID: {goods_id}, Quantity: {quantity}")

    return render_template("buy.jinja", paired_goods_forms=paired_goods_forms)

if __name__ == "__main__":
    app.run(debug=True)