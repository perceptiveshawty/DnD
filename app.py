from flask import Flask, json, request, render_template, session, url_for, redirect, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import user
import psycopg2


app = Flask(__name__)
app.secret_key = "this_should_be_secret"


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    return login_manager


login_manager = init_login_manager(app)


@login_manager.user_loader
def load_user(user_id):
    return user.User.get(user_id)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Extract username and password from form
        username = request.form["username"]
        pw = request.form["password"]
        next = request.args.get('next')
        if (user.validate_user(username, pw)):
            uid = user.get_user(username)
            type = user.get_access_level(str(uid))
            new_user = user.User(username, uid, type)
            login_user(new_user)
            return redirect(next or url_for('dashboard'))
        else:
            return "Login Failed"
    else:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template("index.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]
        pw_confirm = request.form["re-password"]
        isDM = request.form.get("is-dm")

        if (pw != pw_confirm):
            return "Passwords do not match!"

        if (user.create_user(username, pw, isDM)):
            uid = user.get_user(username)
            type = user.get_access_level(str(uid))
            new_user = user.User(username, uid, type)
            login_user(new_user)
            return redirect(url_for('dashboard'))
    else:
        return render_template("create_account.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.isDM:
        return render_template("dm_dashboard.html")
    else:
        return render_template("p_dashboard.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/get_parties")
@login_required
def get_parties():
    if current_user.isDM:
        parties = []

        dmID = user.get_dmID(current_user.id)

        con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
        cur = con.cursor()
        get_user_sql = """SELECT "partyID", name FROM party WHERE "dmID" = (%s) """
        cur.execute(get_user_sql, (dmID,))
        party_list = cur.fetchall()

        for i in range(0, len(party_list)):
            parties.append({'partyID': party_list[i][0], 'name': party_list[i][1]})

        return jsonify(parties)
    else:
        return abort(401)


@app.route("/get_characters")
@login_required
def get_characters():
    uid = request.args.get('uid')

    # if uid == None and not current_user.isDM:
    #     uid = current_user.id
    # else:
    #     return "Must either be a user or provide a user ID"

    characters = []

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_user_sql = """SELECT "characterID", name FROM character WHERE "userID" = (%s)"""
    cur.execute(get_user_sql, (current_user.id,))
    char_list = cur.fetchall()

    for i in range(0, len(char_list)):
        characters.append({'characterID': char_list[i][0], 'name': char_list[i][1]})

    return jsonify(characters)

@app.route("/create_character", methods=["GET", "POST"])
@login_required
def create_character():
    if request.method == "POST":
        if not (current_user.isDM):
            charName = request.form["character_name"]

            con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
            cur = con.cursor()
            cur.execute("""INSERT INTO character (name, "userID") VALUES (%s, %s)""", (charName, current_user.id))
            con.commit()

            return redirect(url_for('dashboard'))
        else:
            return abort(401)
    else:
        return render_template("create_new_character.html")


@app.route("/get_all_items")
@login_required
def get_all_items():
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    cur.execute("""SELECT name,"itemID" FROM item""")
    item_list = cur.fetchall()

    items = []

    for i in range(0, len(item_list)):
        item = {
            'itemID': item_list[i][1],
            'name': item_list[i][0]
        }

        items.append(item)

    return jsonify(items)


@app.route("/get_item")
@login_required
def get_item():
    itemID = request.args.get('itemID')

    if itemID == None:
        return "An item is required"

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    cur.execute("""SELECT name,value,weight,description,category FROM item WHERE "itemID" = %s""", (itemID,))
    details = cur.fetchone()

    item = {
        'itemID': itemID,
        'name': details[0],
        'value': details[1],
        'weight': details[2],
        'description': details[3],
        'category': details[4],
    }

    return jsonify(item)


@app.route("/create_item", methods=["GET", "POST"])
@login_required
def create_item():
    if current_user.isDM:
        if request.method == "POST": 
            dmID = user.get_dmID(current_user.id)
            
            name = request.form.get('item-name')
            description = request.form.get('item-description')
            ivalue = request.form.get('item-value')
            weight = request.form.get('item-weight')
            category = request.form.get('item-category')

            print(name, description, ivalue, weight, category)

            con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
            cur = con.cursor()
            sql = """ INSERT INTO item (name, description, value, weight, category, "dmID") VALUES (%s, %s, %s, %s, %s, %s) """
            cur.execute(sql, (name, description, ivalue, weight, category, dmID))
            con.commit()

            return redirect(url_for("dashboard"))
        else:
            return render_template("create_new_item.html")
    else:
        return "Must be a DM to use this feature"


@app.route("/delete_item")
@login_required
def delete_item():
    if current_user.isDM:
        itemID = request.args.get('itemID')

        con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
        cur = con.cursor()
        sql = """ DELETE FROM item WHERE "itemID" = %s """
        cur.execute(sql, (itemID, ))
        con.commit()
    else:
        return "Must be a DM to use this feature"


@app.route("/get_custom_items")
@login_required
def get_custom_items():
    if current_user.isDM:
        dmID = user.get_dmID(current_user.id)

        con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
        cur = con.cursor()
        cur.execute("""SELECT name,"itemID" FROM item WHERE "dmID" = %s """, (dmID,))
        item_list = cur.fetchall()

        items = []

        for i in range(0, len(item_list)):
            item = {
                'itemID': item_list[i][1],
                'name': item_list[i][0]
            }

            items.append(item)

        return jsonify(items)
    else:
        return "Must be a DM to use this feature"


@app.route("/get_inventory")
@login_required
def get_inventory():
    charID = request.args.get('characterID')

    inventory = []

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_item_list_sql = """SELECT "itemID" FROM "character_carries_item" WHERE "characterID" = (%s)"""
    cur.execute(get_item_list_sql, (charID,))
    item_list = cur.fetchall()

    for i in range(0, len(item_list)):
        get_item_sql = """SELECT name, value, weight, description, category FROM item WHERE "itemID" = (%s)"""
        cur.execute(get_item_sql, (item_list[i][0],))
        item_sql = cur.fetchone()
        item = {
            'itemID': item_list[i][0],
            'name': item_sql[0],
            'value': item_sql[1],
            'weight': item_sql[2],
            'description': item_sql[3],
            'category': item_sql[4],
        }
        inventory.append(item)

    return jsonify(inventory)


@app.route("/inventory_add")
@login_required
def inventory_add():
    charID = request.args.get('characterID')
    itemID = request.args.get('itemID')

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    sql = """ INSERT INTO "character_carries_item" ("characterID","itemID") VALUES (%s, %s) """
    cur.execute(sql, (charID, itemID))
    con.commit()

    return jsonify("true")


@app.route("/get_all_users")
def get_all_users():
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    cur.execute("""SELECT username,"userID" FROM users""")
    user_list = cur.fetchall()

    users = []

    for i in range(0, len(user_list)):
        user = {
            'userID': user_list[i][1],
            'username': user_list[i][0]
        }

        users.append(user)

    return jsonify(users)

@app.route("/inventory_delete")
@login_required
def inventory_delete():
    charID = request.args.get('characterID')
    itemID = request.args.get('itemID')

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    sql = """ DELETE FROM "character_carries_item" WHERE "characterID" = %s AND "itemID" = %s """
    cur.execute(sql, (charID, itemID))
    con.commit()

    return jsonify("true")


@app.route("/get_party_list")
@login_required
def get_party_list():
    partyID = request.args.get('partyID')

    roster = []

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    sql = """SELECT "characterID" FROM "party_contains_character" WHERE "partyID" = (%s)"""
    cur.execute(sql, (partyID,))
    charID_list = cur.fetchall()

    for i in range(0, len(charID_list)):
        cur.execute("""SELECT name FROM "character" WHERE "characterID" = (%s)""", (charID_list[i][0],))
        schar = cur.fetchone()
        character = {
            'charID': charID_list[i][0],
            'name': schar[0],
        }
        roster.append(character)

    return jsonify(roster)

@app.route("/get_party_id")
@login_required
def get_party_id():
    cid = request.args.get('cid')

    if cid == None:
        return "get party id error"

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    cur.execute("""SELECT "partyID" FROM "party_contains_character" WHERE "characterID" = (%s)""", (cid,))
    details = cur.fetchone()
    return jsonify(details)

@app.route("/party_add")
@login_required
def party_add():
    charID = request.args.get('characterID')
    partyID = request.args.get('partyID')

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    sql = """ INSERT INTO "party_contains_character" ("characterID","partyID") VALUES (%s, %s) """
    cur.execute(sql, (charID, partyID))
    con.commit()

    return jsonify("success")


@app.route("/party_delete")
@login_required
def party_delete():
    charID = request.args.get('characterID')
    partyID = request.args.get('partyID')

    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    sql = """ DELETE FROM "party_contains_character" WHERE "characterID" = %s AND "partyID" = %s """
    cur.execute(sql, (charID, partyID))
    con.commit()

    return jsonify("success")


@app.route("/create_party")
@login_required
def create_party():
    if request.method == "POST":
        if (current_user.isDM):
            dmID = user.get_dmID(current_user.id)
            partyName = request.form["party_name"]

            con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
            cur = con.cursor()
            cur.execute("""INSERT INTO party (name, "dmID") VALUES (%s, %s)""", (partyName, dmID))
            con.commit()

            return redirect(url_for('dashboard'))
        else:
            return "Must be a dungeon master to use this."
    else:
        return render_template("create_new_party.html")