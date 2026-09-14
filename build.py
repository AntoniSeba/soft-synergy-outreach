#!/usr/bin/env python3
"""Generuje dashboard (index.html) ze state.json.
Zrodlem prawdy jest WYLACZNIE state.json — dashboard jest tylko widokiem."""
import json, html, datetime, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "state.json")

KOLOR = {
    "oczekuje": ("#8d95ad", "#1b1f2b"),
    "wyslane":  ("#22d3a6", "rgba(34,211,166,.13)"),
    "blad":     ("#ff6b6b", "rgba(255,107,107,.13)"),
    "pominiete": ("#f5b544", "rgba(245,181,68,.13)"),
}
TYP_IKONA = {"komentarz": "💬", "dm": "✉️"}


def esc(s):
    return html.escape(str(s if s is not None else ""))


def main():
    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    akcje = st["akcje"]
    dziennik = st.get("dziennik", [])

    grupy = {}
    for a in akcje:
        grupy.setdefault(a["cel"], []).append(a)

    total = len(akcje)
    wyslane = sum(1 for a in akcje if a["status"] == "wyslane")
    bledy = sum(1 for a in akcje if a["status"] == "blad")
    czeka = total - wyslane - bledy

    # --- karty celów ---
    karty = []
    for cel in sorted(grupy, key=lambda x: int(x[1:])):
        poz = grupy[cel]
        h = poz[0]
        zrobione = sum(1 for a in poz if a["status"] == "wyslane")
        karty.append(f"""
    <div class="card">
      <div class="chead">
        <div>
          <h3>{esc(h['osoba'])}</h3>
          <p class="muted small">{esc(h['firma'])}{' · ' if h['firma'] != '—' else ''}{esc(h['grupa'])}</p>
          <p class="temat">{esc(h['temat'])}</p>
        </div>
        <div class="licznik">{zrobione}/{len(poz)}</div>
      </div>
      <a class="post" href="{esc(h['post'])}" target="_blank" rel="noopener">zobacz post ↗</a>
      <div class="akcje">""")
        for a in poz:
            fg, bg = KOLOR.get(a["status"], KOLOR["oczekuje"])
            ikona = TYP_IKONA.get(a["typ"], "•")
            czas = f" · {esc(a['czas'])}" if a.get("czas") else ""
            wynik = f"<div class='wynik'>{esc(a['wynik'])}</div>" if a.get("wynik") else ""
            karty.append(f"""
        <div class="akcja">
          <div class="arow">
            <span class="typ">{ikona} {esc(a['typ'])}</span>
            <span class="badge" style="color:{fg};border-color:{fg};background:{bg}">{esc(a['status'])}{czas}</span>
          </div>
          <div class="tresc">{esc(a['tresc'])}</div>
          {wynik}
          <div class="mono">{esc(a['id'])}</div>
        </div>""")
        karty.append("</div></div>")

    # --- dziennik ---
    if dziennik:
        wpisy = "".join(
            f"<div class='log'><span class='mono'>{esc(w.get('czas'))}</span> "
            f"<b>{esc(w.get('id'))}</b> — {esc(w.get('opis'))}</div>"
            for w in reversed(dziennik))
    else:
        wpisy = "<span class='muted'>brak wpisów</span>"

    html_out = f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Soft Synergy — kontakt do zleceń</title>
<style>
  :root{{--bg:#0d0f14;--panel:#151822;--panel2:#1b1f2b;--line:#272c3a;--text:#e9ecf5;
        --muted:#8d95ad;--brand:#3ea6ff;--ok:#22d3a6;--warn:#f5b544;--danger:#ff6b6b}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,system-ui,sans-serif;padding:26px 18px 70px}}
  .wrap{{max-width:1000px;margin:0 auto}}
  h1{{font-size:24px;letter-spacing:-.02em}}
  h2{{font-size:17px;margin:34px 0 12px}}
  .muted{{color:var(--muted)}} .small{{font-size:13px}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px;color:var(--muted)}}
  .kpi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0 8px}}
  .k{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
  .k .l{{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600}}
  .k .v{{font-size:27px;font-weight:700;margin-top:5px}}
  .k.ok .v{{color:var(--ok)}} .k.warn .v{{color:var(--warn)}} .k.bad .v{{color:var(--danger)}}
  .zasada{{background:rgba(62,166,255,.08);border:1px solid rgba(62,166,255,.3);border-left:3px solid var(--brand);
          border-radius:10px;padding:13px 16px;font-size:14px;margin:18px 0}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:14px}}
  .chead{{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}}
  .chead h3{{font-size:17px}}
  .temat{{color:var(--brand);font-size:14px;margin-top:5px}}
  .licznik{{font-size:19px;font-weight:700;color:var(--muted);white-space:nowrap}}
  .post{{display:inline-block;margin-top:9px;font-size:13px;color:var(--brand);text-decoration:none}}
  .post:hover{{text-decoration:underline}}
  .akcje{{margin-top:14px;display:grid;gap:10px}}
  .akcja{{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}
  .arow{{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}}
  .typ{{font-size:13px;font-weight:600}}
  .badge{{font-size:11.5px;font-weight:600;padding:3px 9px;border-radius:99px;border:1px solid;white-space:nowrap}}
  .tresc{{font-size:13.5px;color:var(--muted);margin-top:8px;white-space:pre-wrap}}
  .wynik{{font-size:13px;color:var(--ok);margin-top:6px}}
  .log{{font-size:13.5px;padding:7px 0;border-bottom:1px solid var(--line)}}
  footer{{margin-top:34px;color:var(--muted);font-size:13px}}
</style></head><body><div class="wrap">
  <h1>Soft Synergy — kontakt do zleceń z Facebooka</h1>
  <p class="muted small">{esc(st['meta']['projekt'])} · stan na {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}</p>

  <div class="kpi">
    <div class="k"><div class="l">Akcje razem</div><div class="v">{total}</div></div>
    <div class="k ok"><div class="l">Wysłane</div><div class="v">{wyslane}</div></div>
    <div class="k warn"><div class="l">Oczekuje</div><div class="v">{czeka}</div></div>
    <div class="k bad"><div class="l">Błędy</div><div class="v">{bledy}</div></div>
  </div>

  <div class="zasada">
    <b>Blokada duplikatów.</b> Każda akcja ma unikalny klucz i status. Akcja oznaczona jako
    <b>wyslane</b> nie zostanie wysłana ponownie — wysyłka jest pomijana, nie powtarzana.
    Źródłem prawdy jest <span class="mono">state.json</span>, ten panel to tylko widok.
  </div>

  <h2>Cele i akcje</h2>
  {''.join(karty)}

  <h2>Dziennik wysyłki</h2>
  <div class="card">{wpisy}</div>

  <footer>Wygenerowane automatycznie z state.json · {len(akcje)} akcji, {len(dziennik)} wpisów w dzienniku</footer>
</div></body></html>"""

    out = os.path.join(BASE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"OK: {out} | akcje={total} wyslane={wyslane} czeka={czeka} bledy={bledy}")


if __name__ == "__main__":
    main()
