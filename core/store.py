import json
import os
from datetime import datetime

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db.json")


class Store:
    def __init__(self, path: str = _DB_PATH):
        self._path = os.path.abspath(path)
        self._load()

    def _load(self):
        with open(self._path, encoding="utf-8") as f:
            self._data = json.load(f)

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # ── User ────────────────────────────────────────────────────

    def get_user(self) -> dict:
        return self._data["user"]

    # ── Accounts ─────────────────────────────────────────────────

    def get_accounts(self) -> list[dict]:
        return self._data["accounts"]

    def get_account(self, acct_type: str | None = None, acct_id: str | None = None) -> dict | None:
        for a in self._data["accounts"]:
            if acct_id and a["id"] == acct_id:
                return a
            if acct_type and a["type"].lower() == acct_type.lower():
                return a
        return None

    def get_default_account(self) -> dict:
        default_id = self._data["user"]["default_account_id"]
        return self.get_account(acct_id=default_id)

    def update_balance(self, acct_id: str, delta: float):
        for a in self._data["accounts"]:
            if a["id"] == acct_id:
                a["balance"] = round(a["balance"] + delta, 2)
                a["available_balance"] = round(a["available_balance"] + delta, 2)
        self._save()

    # ── Transactions ─────────────────────────────────────────────

    def get_transactions(
        self,
        account_id: str | None = None,
        limit: int | None = None,
        month: int | None = None,
        year: int | None = None,
    ) -> list[dict]:
        txns = self._data["transactions"]
        if account_id:
            txns = [t for t in txns if t["account_id"] == account_id]
        if month and year:
            txns = [
                t for t in txns
                if datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).month == month
                and datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).year == year
            ]
        txns = sorted(txns, key=lambda t: t["created_at"], reverse=True)
        if limit:
            txns = txns[:limit]
        return txns

    def add_transaction(self, txn: dict):
        self._data["transactions"].insert(0, txn)
        self._save()

    # ── Contacts ─────────────────────────────────────────────────

    def get_contacts(self) -> list[dict]:
        return self._data["contacts"]

    def get_contact(self, username: str) -> dict | None:
        username = username.lstrip("@")
        for c in self._data["contacts"]:
            if c["username"].lower() == username.lower():
                return c
        return None

    # ── Cards ────────────────────────────────────────────────────

    def get_cards(self) -> list[dict]:
        return self._data["cards"]

    def set_card_status(self, card_id: str, status: str):
        for c in self._data["cards"]:
            if c["id"] == card_id:
                c["status"] = status
        self._save()

    # ── Recurring ────────────────────────────────────────────────

    def get_recurring(self) -> list[dict]:
        return self._data["recurring_payments"]

    def add_recurring(self, rec: dict):
        self._data["recurring_payments"].append(rec)
        self._save()
