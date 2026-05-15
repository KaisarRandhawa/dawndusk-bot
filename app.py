import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─────────────────────────────────────────────
#  CONFIGURATION  ← paste your values here
# ─────────────────────────────────────────────
VERIFY_TOKEN        = "dawndusk2024"          # any secret word you choose
ACCESS_TOKEN        = "EAFZCiA0m9wuIBRSWNIeAhV7ggLDVeGjXyBwDoQ2sDYHrMzRzXXy5QycQqh1hbkgGGELTVeErFv0uENo9YkiZBgLXYyN3jN3dr1KPMcd6vbGAbyk4p0zRVf705lxDZBiBek6tzZA1ZA52QeLmanZC4EvN3AnNgFZBvVqmWJmzUwvb3hi1FOFgyxtfC6vfCo7RBZBJVzeCITvrWsIhV2487TddMNdOZCI9FZBf7TGsrxk594qZB9C3NR6VWkH4QoYmhVnR10vfJxQyzoXX4ZCcZAA9yKKHBLXAXXCMqrW4dFBYS3QZDZD"
PHONE_NUMBER_ID     = "1114973351698514"
RESTAURANT_NUMBERS  = ["923210111994", "923006637232"]   # both owners
API_URL             = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
# ─────────────────────────────────────────────

# ══════════════════════════════════════════════
#  FULL MENU
# ══════════════════════════════════════════════
MENU = {
    "1": {
        "name": "Appetizers",
        "items": {
            "1": ("Momos (6 pcs)",                   399),
            "2": ("Chicken Strips (6 pcs)",           450),
            "3": ("Chicken Wings (6 pcs)",            450),
            "4": ("Nachos",                           599),
            "5": ("Chicken Cheese Balls (2 pcs)",     499),
            "6": ("Cheese Strips (4 pcs)",            499),
            "7": ("Peri Peri Bites (4 pcs)",          399),
            "8": ("Dynamite Chicken Poppers",         499),
            "9": ("Loaded Fries",                     599),
            "10": ("Mayo Fries",                      350),
            "11": ("Salted Fries",                    200),
        }
    },
    "2": {
        "name": "Steak Studio",
        "items": {
            "1": ("Tarragon Steak",       1150),
            "2": ("Mushroom Steak",       1150),
            "3": ("Moroccan Steak",       1150),
            "4": ("D&D Special Steak",    1299),
        }
    },
    "3": {
        "name": "Stuffed Chicken",
        "items": {
            "1": ("Cordon Bleu",                      1350),
            "2": ("Napoleon Stuffed Chicken",         1250),
            "3": ("Maskawa Stuff Chicken",            1250),
            "4": ("Chicken Parmesan Stuff Chicken",   1290),
            "5": ("D&D Special Stuff Chicken",        1390),
        }
    },
    "4": {
        "name": "Chinese Corner",
        "items": {
            "1": ("Chicken Manchurian",   750),
            "2": ("Kung Pao Chicken",     850),
            "3": ("Oyster Chicken",       750),
            "4": ("Chicken Chili Dry",    750),
            "5": ("Chicken Chow Mein",    650),
            "6": ("Chinese Combo",       1000),
        }
    },
    "5": {
        "name": "Burgers",
        "items": {
            "1": ("Patty Burger",             360),
            "2": ("Grilled Steak Burger",     499),
            "3": ("Chilli Bomb Burger",       550),
            "4": ("Mouthful Crunchy Burger",  370),
            "5": ("Chicken Cheetos Burger",   699),
            "6": ("Stuffed Burger",           750),
            "7": ("Beef Smash Burger",        799),
        }
    },
    "6": {
        "name": "Pasta & Sandwich",
        "items": {
            "1": ("Alfredo Pasta",          850),
            "2": ("D&D Special Pasta",     1050),
            "3": ("Grilled Sandwich",       599),
            "4": ("Panini Sandwich",        699),
            "5": ("Mexican Sandwich",       599),
            "6": ("D&D Special Sandwich",   650),
        }
    },
    "7": {
        "name": "Beverages",
        "items": {
            "1": ("Fresh Lime",          150),
            "2": ("Lemonade",            150),
            "3": ("Mint Margarita",      250),
            "4": ("Peach Sparkler",      300),
            "5": ("Regular Soft Drink",  110),
            "6": ("Water (small/large)", 70),
        }
    },
}

# ══════════════════════════════════════════════
#  SESSION STORE  (in-memory, resets on restart)
# ══════════════════════════════════════════════
sessions = {}

def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {"state": "home", "cart": [], "name": ""}
    return sessions[phone]

def clear_session(phone):
    sessions[phone] = {"state": "home", "cart": [], "name": ""}

# ══════════════════════════════════════════════
#  SEND MESSAGE HELPER
# ══════════════════════════════════════════════
def send_msg(to, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    requests.post(API_URL, headers=headers, json=payload)

# ══════════════════════════════════════════════
#  MESSAGE BUILDERS
# ══════════════════════════════════════════════
def welcome_msg():
    return (
        "🌅 *Welcome to Dawn & Dusk!*\n"
        "Chinese & Continental Fusion\n"
        "📍 87-A Small D-Ground, Near Student Inn Academy, Faisalabad\n\n"
        "Please reply with your *name* to get started 😊"
    )

def main_menu_msg(name):
    return (
        f"Hello *{name}*! 👋 What would you like to do?\n\n"
        "1️⃣  Browse Menu\n"
        "2️⃣  View Cart\n"
        "3️⃣  Place Order\n"
        "4️⃣  Clear Cart\n"
        "0️⃣  Contact Us\n\n"
        "_Reply with a number_"
    )

def categories_msg():
    msg = "📋 *Our Menu Categories:*\n\n"
    for k, v in MENU.items():
        msg += f"{k}️⃣  {v['name']}\n"
    msg += "\n0️⃣  Back to Main Menu\n\n_Reply with a number_"
    return msg

def items_msg(cat_key):
    cat = MENU[cat_key]
    msg = f"🍽️ *{cat['name']}*\n\n"
    for k, (name, price) in cat["items"].items():
        msg += f"{k}. {name} — Rs. {price}\n"
    msg += "\n_Reply with item number to add to cart_\n0️⃣  Back to categories"
    return msg

def cart_msg(cart):
    if not cart:
        return "🛒 Your cart is empty!\n\nReply *1* to browse menu."
    msg = "🛒 *Your Cart:*\n\n"
    total = 0
    for i, item in enumerate(cart, 1):
        subtotal = item["price"] * item["qty"]
        msg += f"{i}. {item['name']} x{item['qty']} = Rs. {subtotal}\n"
        total += subtotal
    msg += f"\n💰 *Total: Rs. {total}*\n\n"
    msg += "Reply *3* to Place Order\nReply *1* to Add More Items\nReply *4* to Clear Cart"
    return msg

def order_summary(name, cart, order_type):
    total = sum(i["price"] * i["qty"] for i in cart)
    msg = f"🎉 *New Order — Dawn & Dusk*\n\n"
    msg += f"👤 Customer: {name}\n"
    msg += f"📦 Type: {order_type}\n\n"
    msg += "📝 *Items:*\n"
    for item in cart:
        msg += f"• {item['name']} x{item['qty']} = Rs. {item['price'] * item['qty']}\n"
    msg += f"\n💰 *Total: Rs. {total}*"
    return msg

# ══════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════
def handle_message(phone, text):
    text = text.strip()
    sess = get_session(phone)
    state = sess["state"]

    # ── No name yet ──────────────────────────
    if state == "home" and not sess["name"]:
        sess["name"] = text.title()
        sess["state"] = "main_menu"
        send_msg(phone, main_menu_msg(sess["name"]))
        return

    # ── Main menu ────────────────────────────
    if state == "main_menu":
        if text == "1":
            sess["state"] = "categories"
            send_msg(phone, categories_msg())
        elif text == "2":
            send_msg(phone, cart_msg(sess["cart"]))
        elif text == "3":
            if not sess["cart"]:
                send_msg(phone, "🛒 Your cart is empty! Reply *1* to browse menu.")
            else:
                sess["state"] = "order_type"
                send_msg(phone,
                    "📦 *How would you like your order?*\n\n"
                    "1️⃣  Dine-in\n"
                    "2️⃣  Takeaway\n"
                    "3️⃣  Delivery\n\n"
                    "_Reply with a number_"
                )
        elif text == "4":
            sess["cart"] = []
            send_msg(phone, "🗑️ Cart cleared!\n\n" + main_menu_msg(sess["name"]))
        elif text == "0":
            send_msg(phone,
                "📞 *Dawn & Dusk*\n"
                "87-A, Small D-Ground\n"
                "Near Student Inn Academy, Faisalabad\n\n"
                "☎️ 0321-0111994\n"
                "☎️ 0300-6637232"
            )
        else:
            send_msg(phone, main_menu_msg(sess["name"]))
        return

    # ── Categories ───────────────────────────
    if state == "categories":
        if text == "0":
            sess["state"] = "main_menu"
            send_msg(phone, main_menu_msg(sess["name"]))
        elif text in MENU:
            sess["state"] = f"items_{text}"
            send_msg(phone, items_msg(text))
        else:
            send_msg(phone, categories_msg())
        return

    # ── Items ────────────────────────────────
    if state.startswith("items_"):
        cat_key = state.split("_")[1]
        if text == "0":
            sess["state"] = "categories"
            send_msg(phone, categories_msg())
        elif text in MENU[cat_key]["items"]:
            item_name, item_price = MENU[cat_key]["items"][text]
            # check if already in cart
            for c in sess["cart"]:
                if c["name"] == item_name:
                    c["qty"] += 1
                    break
            else:
                sess["cart"].append({"name": item_name, "price": item_price, "qty": 1})
            total = sum(i["price"] * i["qty"] for i in sess["cart"])
            send_msg(phone,
                f"✅ *{item_name}* added!\n\n"
                f"Cart: {sum(i['qty'] for i in sess['cart'])} item(s) — Rs. {total}\n\n"
                "Reply with another item number to add more\n"
                "0️⃣  Back to categories\n"
                "Reply *3* to place order"
            )
            # check if user replies 3 from item screen
            sess["state"] = f"items_{cat_key}"
        elif text == "3":
            if not sess["cart"]:
                send_msg(phone, "🛒 Cart is empty! Add items first.")
            else:
                sess["state"] = "order_type"
                send_msg(phone,
                    "📦 *How would you like your order?*\n\n"
                    "1️⃣  Dine-in\n"
                    "2️⃣  Takeaway\n"
                    "3️⃣  Delivery\n\n"
                    "_Reply with a number_"
                )
        else:
            send_msg(phone, items_msg(cat_key))
        return

    # ── Order type ───────────────────────────
    if state == "order_type":
        types = {"1": "Dine-in", "2": "Takeaway", "3": "Delivery"}
        if text in types:
            sess["order_type"] = types[text]
            if text == "3":
                sess["state"] = "delivery_address"
                send_msg(phone, "📍 Please share your *delivery address*:")
            else:
                sess["state"] = "confirm_order"
                send_msg(phone,
                    cart_msg(sess["cart"]) + f"\n\n📦 Type: *{types[text]}*\n\n"
                    "Reply *YES* to confirm order\nReply *NO* to cancel"
                )
        else:
            send_msg(phone,
                "Please reply 1, 2, or 3:\n\n"
                "1️⃣  Dine-in\n2️⃣  Takeaway\n3️⃣  Delivery"
            )
        return

    # ── Delivery address ─────────────────────
    if state == "delivery_address":
        sess["address"] = text
        sess["state"] = "confirm_order"
        send_msg(phone,
            cart_msg(sess["cart"]) +
            f"\n\n📦 Type: *Delivery*\n📍 Address: {text}\n\n"
            "Reply *YES* to confirm order\nReply *NO* to cancel"
        )
        return

    # ── Confirm order ─────────────────────────
    if state == "confirm_order":
        if text.upper() == "YES":
            order_type = sess.get("order_type", "Dine-in")
            if order_type == "Delivery":
                order_type += f" — {sess.get('address', '')}"
            summary = order_summary(sess["name"], sess["cart"], order_type)
            # Send to both restaurant numbers
            for num in RESTAURANT_NUMBERS:
                send_msg(num, summary)
            # Confirm to customer
            total = sum(i["price"] * i["qty"] for i in sess["cart"])
            send_msg(phone,
                f"🎉 *Order Confirmed!*\n\n"
                f"Thank you *{sess['name']}*!\n"
                f"💰 Total: Rs. {total}\n"
                f"⏱️ Estimated time: 20-30 mins\n\n"
                f"We'll contact you shortly on this number.\n\n"
                f"📞 Questions? Call 0321-0111994\n\n"
                f"Thank you for choosing *Dawn & Dusk!* 🌅"
            )
            clear_session(phone)
        elif text.upper() == "NO":
            sess["state"] = "main_menu"
            send_msg(phone, "Order cancelled.\n\n" + main_menu_msg(sess["name"]))
        else:
            send_msg(phone, "Please reply *YES* to confirm or *NO* to cancel.")
        return

    # ── Fallback ─────────────────────────────
    clear_session(phone)
    send_msg(phone, welcome_msg())

# ══════════════════════════════════════════════
#  FLASK ROUTES
# ══════════════════════════════════════════════
@app.route("/webhook", methods=["GET"])
def verify():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "text":
                        phone = msg["from"]
                        text  = msg["text"]["body"]
                        handle_message(phone, text)
    except Exception as e:
        print("Error:", e)
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return "Dawn & Dusk WhatsApp Bot is running! 🌅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
