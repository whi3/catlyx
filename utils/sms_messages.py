def referral_created_message(destination: str,) -> str:
    return (
        "CatalystX: A health referral has been "
        f"created for you. Please visit "
        f"{destination} as advised by the health worker."
    )

def follow_up_reminder_message(destination: str,) -> str:
    return (
        "CatalystX reminder: Your health referral "
        f"to {destination} is still pending. "
        "Please follow up with the health worker."
    )