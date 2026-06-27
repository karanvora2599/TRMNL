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
        acct = self.get_account(acct_id=default_id)
        assert acct is not None
        return acct

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

    # ── Budgets ──────────────────────────────────────────────────

    def get_budgets(self) -> list[dict]:
        return self._data.get("budgets", [])

    # ── Institutions ─────────────────────────────────────────────

    def get_institutions(self) -> list[dict]:
        return self._data.get("institutions", [])

    def get_institution(self, inst_id: str) -> dict | None:
        for i in self._data.get("institutions", []):
            if i["id"] == inst_id:
                return i
        return None

    def get_accounts_by_category(self, category: str) -> list[dict]:
        return [a for a in self._data["accounts"] if a.get("account_category") == category]

    def get_accounts_by_institution(self, inst_id: str) -> list[dict]:
        return [a for a in self._data["accounts"] if a.get("institution_id") == inst_id]

    def find_account(self, query: str) -> dict | None:
        q = query.lower().strip()
        for a in self._data["accounts"]:
            if a["id"] == query:
                return a
            if a.get("type", "").lower() == q:
                return a
            if a.get("last4", "") == q:
                return a
            nick = a.get("nickname", "").lower()
            if q in nick or nick in q:
                return a
            inst = self.get_institution(a.get("institution_id", ""))
            if inst:
                short = inst.get("short_name", "").lower()
                if q in short or short in q:
                    return a
        return None

    # ── Holdings & Quotes ────────────────────────────────────────

    def get_holdings(self, account_id: str | None = None) -> list[dict]:
        holdings = self._data.get("holdings", [])
        if account_id:
            holdings = [h for h in holdings if h["account_id"] == account_id]
        return holdings

    def get_quote(self, ticker: str) -> dict | None:
        for q in self._data.get("quotes", []):
            if q["ticker"].upper() == ticker.upper():
                return q
        return None

    def get_all_quotes(self) -> list[dict]:
        return self._data.get("quotes", [])

    def compute_holding_value(self, holding: dict) -> float:
        q = self.get_quote(holding["ticker"])
        if not q:
            return 0.0
        return round(holding["shares"] * q["current_price"], 2)

    def compute_holding_gain(self, holding: dict) -> tuple[float, float]:
        value = self.compute_holding_value(holding)
        cost = round(holding["shares"] * holding["cost_basis_per_share"], 2)
        gain = round(value - cost, 2)
        pct = gain / cost if cost else 0.0
        return gain, pct

    def compute_account_market_value(self, account_id: str) -> float:
        holdings = self.get_holdings(account_id=account_id)
        return round(sum(self.compute_holding_value(h) for h in holdings), 2)

    def compute_net_worth(self) -> dict:
        depository = sum(
            a["balance"] for a in self.get_accounts_by_category("depository")
        )
        investments = sum(
            self.compute_account_market_value(a["id"])
            for a in self.get_accounts_by_category("investment")
        )
        credit_owed = sum(
            a.get("balance_owed", 0.0) for a in self.get_accounts_by_category("credit")
        )
        loans = sum(
            a.get("current_balance", 0.0) for a in self.get_accounts_by_category("loan")
        )
        assets = round(depository + investments, 2)
        liabilities = round(credit_owed + loans, 2)
        return {
            "assets": assets,
            "liabilities": liabilities,
            "net_worth": round(assets - liabilities, 2),
            "depository": round(depository, 2),
            "investments": round(investments, 2),
            "credit_owed": round(credit_owed, 2),
            "loans": round(loans, 2),
        }

    # ── History ──────────────────────────────────────────────────

    def get_balance_history(self, account_id: str | None = None) -> list[dict]:
        raw = self._data.get("balance_history", [])
        target_id = account_id or self._data["user"]["default_account_id"]
        for entry in raw:
            if entry.get("account_id") == target_id:
                return entry.get("snapshots", [])
        return []

    def get_net_worth_history(self) -> list[dict]:
        return self._data.get("net_worth_history", [])

    def get_monthly_spend_history(self) -> list[dict]:
        return self._data.get("monthly_spend_history", [])
