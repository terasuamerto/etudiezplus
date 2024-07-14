# Define error code dictionary for PAYIN
PAYIN_ERROR_CODES = {
    "00": "No error",
    "01": "There is an error",
    "Echec (Code00)": "Token Authentication error",
    "Echec (Code01)": "Application Authentication error",
    "Echec (Code02)": "Incorrect amount. (The amount must be between min and max)",
    "Echec (Code03)": "IP Denied",
    "Echec (Code04)": "An error occurred while processing request",
    # Add more error codes as needed
}

# Define error code dictionary for PAYOUT TO LIGDICASH WALLET
PAYOUT_ERROR_CODES = {
    "00": "No error",
    "01": "There is an error",
    "Echec (Code00)": "Authentication failure",
    "Echec (Code01)": "Merchant Payout not activated",
    "Echec (Code02)": "Customer not registered on the platform",
    "Echec (Code03)": "No merchant account on the specified network",
    "Echec (Code03a)": "Pending/Processed payout within the last 24 hours",
    "Echec (Code03b)": "No deposit within the last 3 months",
    "Echec (Code04)": "Merchant balance Low",
    "Echec (Code05)": "Request amount out of range [100;1000000]",
    "Echec (Code06)": "IP denied",
    "Echec (Code07)": "Transaction_id already exists",
    "Echec (Code08)": "An error occurred while processing",
    "Echec (Code09)": "Data Input error",
    # Add more error codes as needed
}