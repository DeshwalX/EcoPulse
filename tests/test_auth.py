from backend.auth import get_password_hash, verify_password


def test_password_hashing_and_verification():
    """Verify raw strings hash securely and match true inputs while rejecting wrong guesses."""
    raw_password = "Password123"
    hashed = get_password_hash(raw_password)

    assert hashed != raw_password
    assert len(hashed) > 0
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False