from app.utils.security import hash_password, verify_password


def test_hash_password_deterministic():
    assert hash_password("admin") == hash_password("admin")


def test_hash_password_different_inputs():
    assert hash_password("admin") != hash_password("kawa")


def test_verify_password_correct():
    hashed = hash_password("kawa")
    assert verify_password("kawa", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("kawa")
    assert verify_password("wrong_password", hashed) is False


def test_hash_is_string():
    result = hash_password("test")
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex = 64 chars
