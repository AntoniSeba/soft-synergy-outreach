#!/usr/bin/env python3
"""mark.py <ID> <status> [wynik]
Blokada duplikatow: odmawia zmiany, jesli akcja ma juz status 'wyslane'.
Uzycie: python3 mark.py T1-DM wyslane "potwierdzone w watku" """
import json, sys, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "state.json")


def load():
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def save(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 3:
        print("uzycie: mark.py <ID> <status> [wynik]"); sys.exit(2)
    aid, status = sys.argv[1], sys.argv[2]
    wynik = sys.argv[3] if len(sys.argv) > 3 else ""
    st = load()
    akcja = next((a for a in st["akcje"] if a["id"] == aid), None)
    if not akcja:
        print(f"BLAD: nie ma akcji {aid}"); sys.exit(1)

    if akcja["status"] == "wyslane" and status != "wyslane":
        print(f"STOP: {aid} juz wyslane — nie zmieniam na '{status}'"); sys.exit(3)
    if akcja["status"] == "wyslane" and status == "wyslane":
        print(f"STOP: {aid} juz oznaczone jako wyslane — pomijam (blokada duplikatu)"); sys.exit(3)

    teraz = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    akcja["status"] = status
    akcja["czas"] = teraz
    if wynik:
        akcja["wynik"] = wynik
    st["dziennik"].append({
        "czas": teraz, "id": aid, "opis": f"{akcja['osoba']} / {akcja['typ']} -> {status}" + (f" ({wynik})" if wynik else "")
    })
    save(st)
    print(f"OK: {aid} = {status}")


if __name__ == "__main__":
    main()
