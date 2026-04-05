from app.core.security import create_oauth_state, decrypt_secret, encrypt_secret, verify_oauth_state


def test_secret_encryption_round_trip():
    encrypted_value = encrypt_secret("access-token", "unit-test-secret")

    assert encrypted_value != "access-token"
    assert decrypt_secret(encrypted_value, "unit-test-secret") == "access-token"


def test_oauth_state_verification():
    state = create_oauth_state("unit-test-secret")

    assert verify_oauth_state(state, "unit-test-secret")


def test_oauth_state_rejects_tampering():
    state = create_oauth_state("unit-test-secret")
    tampered_state = f"{state}x"

    assert not verify_oauth_state(tampered_state, "unit-test-secret")