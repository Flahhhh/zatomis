from views import index_view, test_view, account_view, status_view, profile_view, balance_view, payment_view, transfer_view

routes = {
    "services/": index_view,
    "services/account": account_view,
    "services/test": test_view,
    "services/status": status_view,
    "services/profile": profile_view,
    "banking/balance": balance_view,
    "banking/payment": payment_view,
    "banking/transfer": transfer_view,
}
