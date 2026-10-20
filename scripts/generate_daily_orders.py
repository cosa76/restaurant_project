"""Simule de nouvelles commandes journalières et les ajoute au seed.

Le script lit seeds/restaurant_orders.csv, s'inspire des données
existantes (plats, catégories, fourchettes de prix, moyens de paiement,
clients) et ajoute des commandes pour les jours qui suivent la dernière
date présente. Aucune dépendance hors bibliothèque standard.

Exemples :
    python scripts/generate_daily_orders.py              # 1 jour après la dernière date
    python scripts/generate_daily_orders.py --days 7     # une semaine
    python scripts/generate_daily_orders.py --date 2025-09-01 --orders 20
    python scripts/generate_daily_orders.py --dry-run    # affiche sans écrire
"""

import argparse
import csv
import random
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

SEED_FILE = Path(__file__).resolve().parent.parent / "seeds" / "restaurant_orders.csv"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Lucas", "Mia", "Ethan",
    "Sophia", "Mason", "Chloe", "Leo", "Zoe", "Hugo", "Lina", "Adam",
]
LAST_NAMES = [
    "Martin", "Bernard", "Smith", "Johnson", "Garcia", "Dubois", "Lopez",
    "Moreau", "Brown", "Petit", "Wilson", "Leroy", "Davis", "Roux",
]

# Poids par heure : pics au déjeuner (12-14 h) et au dîner (19-21 h).
HOUR_WEIGHTS = {h: 1 for h in range(24)}
HOUR_WEIGHTS.update({11: 3, 12: 6, 13: 6, 14: 3, 18: 3, 19: 6, 20: 6, 21: 3})


def detect_line_end(path):
    # On écrit avec la même fin de ligne que le fichier (LF ou CRLF selon
    # git sous Windows). Un mélange des deux empêche DuckDB de lire le seed.
    with path.open("rb") as f:
        return "\r\n" if b"\r\n" in f.readline() else "\n"


def load_orders(path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def build_profile(rows):
    """Extrait des données existantes ce qu'il faut pour simuler."""
    item_category = {}
    item_prices = defaultdict(list)
    for r in rows:
        item_category[r["Food Item"]] = r["Category"]
        item_prices[r["Food Item"]].append(float(r["Price"]))
    return {
        "item_category": item_category,
        "price_range": {i: (min(p), max(p)) for i, p in item_prices.items()},
        "payment_methods": sorted({r["Payment Method"] for r in rows}),
        "customers": sorted({r["Customer Name"] for r in rows}),
        "used_ids": {int(r["Order ID"]) for r in rows},
        "last_date": max(datetime.strptime(r["Order Time"], TIME_FORMAT) for r in rows).date(),
    }


def new_order_id(used_ids, rng):
    # Les ids existants sont aléatoires sur 4 chiffres : on en tire un libre,
    # puis on passe à 5 chiffres si la plage est saturée.
    for low, high in ((1000, 9999), (10000, 99999)):
        free = high - low + 1 - sum(low <= i <= high for i in used_ids)
        if free > 0:
            while True:
                candidate = rng.randint(low, high)
                if candidate not in used_ids:
                    used_ids.add(candidate)
                    return candidate
    raise RuntimeError("Plus d'identifiant de commande disponible.")


def pick_customer(profile, rng, returning_rate):
    if rng.random() < returning_rate:
        return rng.choice(profile["customers"])
    name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
    profile["customers"].append(name)
    return name


def simulate_day(day, n_orders, profile, rng, returning_rate):
    hours, weights = zip(*HOUR_WEIGHTS.items())
    items = sorted(profile["item_category"])
    rows = []
    for _ in range(n_orders):
        item = rng.choice(items)
        low, high = profile["price_range"][item]
        ordered_at = datetime.combine(day, datetime.min.time()) + timedelta(
            hours=rng.choices(hours, weights)[0],
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59),
        )
        rows.append({
            "Order ID": new_order_id(profile["used_ids"], rng),
            "Customer Name": pick_customer(profile, rng, returning_rate),
            "Food Item": item,
            "Category": profile["item_category"][item],
            "Quantity": rng.randint(1, 5),
            "Price": round(rng.uniform(low, high), 2),
            "Payment Method": rng.choice(profile["payment_methods"]),
            "Order Time": ordered_at.strftime(TIME_FORMAT),
        })
    return sorted(rows, key=lambda r: r["Order Time"])


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", type=date.fromisoformat,
                   help="Premier jour à simuler (AAAA-MM-JJ). Défaut : lendemain de la dernière date du CSV.")
    p.add_argument("--days", type=int, default=1, help="Nombre de jours à simuler (défaut 1).")
    p.add_argument("--orders", type=int,
                   help="Commandes par jour. Défaut : aléatoire entre --min-orders et --max-orders.")
    p.add_argument("--min-orders", type=int, default=5)
    p.add_argument("--max-orders", type=int, default=15)
    p.add_argument("--returning-rate", type=float, default=0.3,
                   help="Part des commandes passées par un client déjà connu (défaut 0.3).")
    p.add_argument("--seed", type=int, help="Graine aléatoire, pour rejouer exactement la même simulation.")
    p.add_argument("--file", type=Path, default=SEED_FILE, help="CSV à compléter.")
    p.add_argument("--dry-run", action="store_true", help="Affiche les lignes sans modifier le CSV.")
    return p.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    fieldnames, rows = load_orders(args.file)
    line_end = detect_line_end(args.file)
    profile = build_profile(rows)

    start = args.date or profile["last_date"] + timedelta(days=1)
    new_rows = []
    for offset in range(args.days):
        day = start + timedelta(days=offset)
        n = args.orders or rng.randint(args.min_orders, args.max_orders)
        new_rows += simulate_day(day, n, profile, rng, args.returning_rate)
        print(f"{day} : {n} commandes simulées")

    if args.dry_run:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator=line_end)
        writer.writeheader()
        writer.writerows(new_rows)
        return

    with args.file.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fieldnames, lineterminator=line_end).writerows(new_rows)
    print(f"{len(new_rows)} lignes ajoutées à {args.file}")


if __name__ == "__main__":
    main()
