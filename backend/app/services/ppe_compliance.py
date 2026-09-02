from app.models.ppe_log import PPEStatus


def evaluate_compliance(
    helmet_detected: bool,
    vest_detected: bool,
) -> PPEStatus:
    """
    Convert helmet/vest detection into the database PPE status.
    """

    if helmet_detected and vest_detected:
        return PPEStatus.FULL_PPE

    if not helmet_detected and vest_detected:
        return PPEStatus.HELMET_MISSING

    if helmet_detected and not vest_detected:
        return PPEStatus.VEST_MISSING

    return PPEStatus.NO_PPE