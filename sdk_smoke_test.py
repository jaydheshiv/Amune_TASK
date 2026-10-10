import os
import sys

# Ensure generated SDK package is accessible when running from project root
sys.path.insert(0, os.path.abspath("finance_sdk"))

import time
import threading
import uvicorn
from finance_sdk import ApiClient, Configuration
from finance_sdk.api.transactions_api import TransactionsApi
from finance_sdk.models.transaction_create import TransactionCreate
from finance_sdk.models.reclassify_request import ReclassifyRequest
from backend.main import app


def run_smoke_test():
    """Run full CRUD cycle using the generated SDK against the FastAPI backend."""
    # Configure SDK with target host
    config = Configuration(host="http://localhost:8000")

    with ApiClient(config) as client:
        api = TransactionsApi(client)

        print("[1/5] Listing existing transactions via SDK...")
        transactions = api.list_transactions()
        print(f"      Fetched {len(transactions)} existing transactions.")

        print("[2/5] Creating new transaction via SDK...")
        new_tx_data = TransactionCreate(
            description="Starbucks SDK Test Coffee",
            amount=5.75,
            transaction_type="expense",
        )
        created = api.create_transaction(new_tx_data)
        print(f"      Created transaction ID: {created.id}, Category: {created.category}, Amount: ${created.amount}")
        assert created.category == "Food"
        assert created.auto_tagged is True

        print("[3/5] Reclassifying transaction via SDK...")
        reclassify_payload = ReclassifyRequest(category="Beverages")
        updated = api.reclassify_transaction(
            transaction_id=created.id,
            reclassify_request=reclassify_payload,
        )
        print(f"      Reclassified transaction ID: {updated.id}, New Category: {updated.category}")
        assert updated.category == "Beverages"
        assert updated.auto_tagged is False

        print("[4/5] Fetching monthly category summary via SDK...")
        summary = api.get_summary()
        print(f"      Retrieved {len(summary)} monthly category summary rows.")
        assert len(summary) > 0

        print("[5/5] Deleting transaction via SDK...")
        api.delete_transaction(transaction_id=created.id)
        print("      Transaction deleted successfully.")

        print("\nAll SDK smoke test assertions passed successfully!")


if __name__ == "__main__":
    # Ensure a local test server is running if not already started
    server_thread = None
    server = None
    try:
        # Quick check if server already running
        import urllib.request
        urllib.request.urlopen("http://localhost:8000/health", timeout=1)
        print("Existing backend server detected on http://localhost:8000.")
    except Exception:
        print("Starting embedded Uvicorn server for smoke test...")
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        time.sleep(1.5)

    try:
        run_smoke_test()
    finally:
        if server:
            server.should_exit = True
