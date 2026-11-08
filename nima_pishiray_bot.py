import os, json, random, time, threading
from urllib.request import Request, urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ["BOT_TOKEN"]
_raw = os.environ.get("CHANNEL", "@bugunnimapishiray).strip()
CHANNEL = "@" + _raw.split("t.me/")[-1].lstrip("@").strip("/")  # havola yozilsa ham ishlaydi
print("Kanal:", CHANNEL, flush=True)
API = f"https://api.telegram.org/bot{TOKEN}/"

RECIPES = [
    # (id, kategoriya, nomi, ingredientlar, tayyorlash)
    ("mastava", "Shorvalar", "Mastava",
     "Go'sht 300 g, guruch 1 stakan, kartoshka 2 ta, sabzi 1 ta, piyoz 1 ta, pomidor 2 ta, yog', tuz, zira",
     "1) Go'shtni piyoz bilan qovuring. 2) Sabzi, pomidorni qo'shib dimlang. 3) Suv quying, qaynagach kartoshka soling. 4) 15 daqiqadan so'ng guruchni qo'shing. 5) Guruch yumshagach, ko'katlar bilan torting."),
    ("shurpa", "Shorvalar", "Sho'rva",
     "Mol go'shti 500 g, kartoshka 3 ta, sabzi 2 ta, piyoz 2 ta, bulg'or qalampiri 1 ta, ko'kat, tuz",
     "1) Go'shtni suvda 1 soat qaynating, ko'pigini oling. 2) Sabzi, piyozni yirik to'g'rab soling. 3) 30 daqiqadan so'ng kartoshka, qalampir qo'shing. 4) Tuz, ko'kat bilan torting."),
    ("lagmon", "Shorvalar", "Lag'mon (oddiy)",
     "Lag'mon xamiri 400 g, go'sht 300 g, sabzi, bulg'or qalampiri, piyoz, pomidor pastasi 2 osh qoshiq, sarimsoq",
     "1) Go'shtni piyoz bilan qovuring. 2) Sabzi, qalampir, pomidor pastasini soling. 3) Suv quyib 30 daqiqa qaynating. 4) Xamirni alohida pishirib, ustiga qaynatma quying."),
    ("osh", "Asosiy taomlar", "Osh (palov)",
     "Guruch 1 kg, go'sht 700 g, sabzi 1 kg, piyoz 3 ta, yog' 250 ml, zira, zirvak uchun tuz",
     "1) Qozonda yog'ni qizdirib, go'shtni qovuring. 2) Piyoz, sabzini ketma-ket qo'shing. 3) Suv quyib 40 daqiqa zirvak qiling. 4) Yuvilgan guruchni tekis yoying, ustidan suv quying. 5) Suv tortilgach, damlab 25 daqiqa qo'ying."),
    ("manti", "Asosiy taomlar", "Manti",
     "Un 500 g, suv 200 ml, tuz; ichiga: go'sht 500 g, piyoz 4 ta, qora murch, zira",
     "1) Qattiq xamir qorib, 30 daqiqa dam bering. 2) Go'sht va piyozni mayda to'g'rab, ziravor soling. 3) Xamirni yoyib kvadrat kesing, ichiga soling, buklang. 4) Mantikashda 45 daqiqa bug'da pishiring."),
    ("dimlama", "Asosiy taomlar", "Dimlama",
     "Go'sht 500 g, kartoshka 4 ta, sabzi 2 ta, piyoz 2 ta, karam, pomidor 2 ta, tuz, murch",
     "1) Qozonga qatlam-qatlam: go'sht, piyoz, sabzi, karam, kartoshka, pomidor soling. 2) Tuz, murch seping. 3) Qopqog'ini yoping, past olovda 1.5 soat dimlang. Aralashtirmang."),
    ("achichuk", "Salatlar", "Achchiq-chuchuk",
     "Pomidor 4 ta, piyoz 1 ta, achchiq qalampir, ko'kat, tuz",
     "1) Pomidor va piyozni yupqa to'g'rang. 2) Piyozni tuz bilan ezib, achchig'ini chiqaring. 3) Hammasini aralashtirib, ko'kat seping."),
    ("olivye", "Salatlar", "Olivye",
     "Kartoshka 3 ta, sabzi 2 ta, tuxum 4 ta, bodring tuzlangan 3 ta, kolbasa 200 g, no'xat 1 banka, mayonez",
     "1) Kartoshka, sabzi, tuxumni qaynating. 2) Hammasini bir xil kubik qilib to'g'rang. 3) No'xat, mayonez, tuz qo'shib aralashtiring. 4) Sovutib torting."),
    ("karam", "Salatlar", "Karam salati",
     "Oq karam 300 g, sabzi 1 ta, sirka 1 choy qoshiq, o'simlik yog'i, tuz, shakar",
     "1) Karamni mayda to'g'rab tuz bilan ezing. 2) Sabzini ishqalab qo'shing. 3) Sirka, yog', bir chimdim shakar solib aralashtiring."),
    ("chakchak", "Shirinliklar", "Chak-chak",
     "Un 500 g, tuxum 4 ta, tuz; sirop: asal 200 g, shakar 100 g",
     "1) Tuxum va un bilan qattiq xamir qoring. 2) Ingichka cho'pchalar qilib kesib, yog'da qizartiring. 3) Asal va shakarni qaynatib sirop qiling. 4) Cho'pchalarni sirop bilan aralashtirib, shakl bering."),
    ("blin", "Shirinliklar", "Blin (krep)",
     "Sut 500 ml, un 200 g, tuxum 2 ta, shakar 2 osh qoshiq, tuz, yog' 2 osh qoshiq",
     "1) Tuxum, shakar, tuzni aralashtiring. 2) Sut va unni qo'shib, quyuq bo'lmagan xamir qiling. 3) Yog' soling. 4) Tova'da ikki tomonini qizartiring."),
    ("pishme", "Shirinliklar", "Pishme",
     "Un 500 g, sut 200 ml, yog' 100 g, tuxum 1 ta, xamirturush 1 choy qoshiq, shakar 1 osh qoshiq, tuz; qovurish uchun yog'",
     "1) Hamma narsani qorib, 1 soat dam bering. 2) Yoyib, kichik to'rtburchak qilib kesing. 3) Qaynoq yog'da qizartiring. 4) Choy yoki asal bilan torting."),
    ("somsa", "Asosiy taomlar", "Somsa (tez variant)",
     "Qatlama xamir 500 g, go'sht 400 g, piyoz 3 ta, tuz, zira, tuxum sarig'i",
     "1) Go'sht va piyozni mayda to'g'rab, ziravor soling. 2) Xamirni kvadrat kesib ichiga soling, uchburchak buklang. 3) Ustiga sarig' surting. 4) 200°C da 30-35 daqiqa pishiring."),
]
BY_ID = {r[0]: r for r in RECIPES}
CATS = ["Shorvalar", "Asosiy taomlar", "Salatlar", "Shirinliklar"]
CAT_ICON = {"Shorvalar": "🍲", "Asosiy taomlar": "🍛", "Salatlar": "🥗", "Shirinliklar": "🍰"}


def call(method, **params):
    req = Request(API + method, json.dumps(params).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=60) as r:
            return json.load(r)
    except Exception as e:
        print("API xato:", method, e)
        return {"ok": False}


def subscribed(uid):
    r = call("getChatMember", chat_id=CHANNEL, user_id=uid)
    return r.get("ok") and r["result"]["status"] in ("member", "administrator", "creator")


def kb(rows):
    return {"inline_keyboard": rows}


def menu_kb():
    rows = [[{"text": "🎲 Tasodifiy retsept", "callback_data": "rand"}]]
    rows += [[{"text": f"{CAT_ICON[c]} {c}", "callback_data": f"cat:{c}"}] for c in CATS]
    return kb(rows)


def send(chat, text, markup=None):
    call("sendMessage", chat_id=chat, text=text, reply_markup=markup)


def show_gate(chat):
    send(chat, "Botdan foydalanish uchun kanalimizga obuna bo'ling 👇", kb([
        [{"text": "📢 Kanalga o'tish", "url": f"https://t.me/{CHANNEL.lstrip('@')}"}],
        [{"text": "✅ Tekshirish", "callback_data": "check"}],
    ]))


def show_menu(chat):
    send(chat, "Nima pishiramiz? 😋", menu_kb())


def show_recipe(chat, rid):
    _, cat, name, ing, how = BY_ID[rid]
    text = f"{CAT_ICON[cat]} {name}\n\n🛒 Masalliqlar:\n{ing}\n\n👩‍🍳 Tayyorlash:\n{how}\n\nYoqimli ishtaha! 🤲"
    send(chat, text, kb([
        [{"text": "🎲 Yana retsept", "callback_data": "rand"}],
        [{"text": "🏠 Menyu", "callback_data": "menu"}],
    ]))


def show_cat(chat, cat):
    rows = [[{"text": r[2], "callback_data": f"r:{r[0]}"}] for r in RECIPES if r[1] == cat]
    rows.append([{"text": "🏠 Menyu", "callback_data": "menu"}])
    send(chat, f"{CAT_ICON[cat]} {cat}:", kb(rows))


def handle_message(m):
    chat, uid = m["chat"]["id"], m["from"]["id"]
    if not subscribed(uid):
        return show_gate(chat)
    show_menu(chat)


def handle_callback(cq):
    call("answerCallbackQuery", callback_query_id=cq["id"])
    chat, uid, data = cq["message"]["chat"]["id"], cq["from"]["id"], cq["data"]
    if not subscribed(uid):
        return show_gate(chat)
    if data in ("check", "menu"):
        show_menu(chat)
    elif data == "rand":
        show_recipe(chat, random.choice(RECIPES)[0])
    elif data.startswith("cat:"):
        show_cat(chat, data[4:])
    elif data.startswith("r:") and data[2:] in BY_ID:
        show_recipe(chat, data[2:])


def poll():
    offset = 0
    while True:
        r = call("getUpdates", offset=offset, timeout=30, allowed_updates=["message", "callback_query"])
        if not r.get("ok"):
            time.sleep(5)
            continue
        for u in r["result"]:
            offset = u["update_id"] + 1
            try:
                if "message" in u:
                    handle_message(u["message"])
                elif "callback_query" in u:
                    handle_callback(u["callback_query"])
            except Exception as e:
                print("Xato:", e)


class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=poll, daemon=True).start()
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), Ping).serve_forever()


