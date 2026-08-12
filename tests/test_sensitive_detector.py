from src.sensitive_detector import detect_sensitive_information


def test_otp_detection():
    message = "Your OTP is 123456."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "one_time_password"
    assert "123456" not in findings[0].masked_text
    assert findings[0].risk == "high"


def test_password_detection():
    message = "Use password Secret123 to sign in."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "password"
    assert "Secret123" not in findings[0].masked_text


def test_card_detection():
    message = "My card number is 4111 1111 1111 1111."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "card_number"
    assert "4111" not in findings[0].masked_text


def test_address_detection():
    message = "My home address is 42 Lake View Road, Chennai."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "home_address"
    assert "42 Lake View Road" not in findings[0].masked_text

def test_token_detection():
    message = "The temporary access token is tok_demo_A8K29Q-53."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "authentication_token"
    assert "tok_demo_A8K29Q-53" not in findings[0].masked_text
    assert findings[0].risk == "high"


def test_phone_detection():
    message = "You can contact me on 98765 43210-86."

    findings = detect_sensitive_information(message)

    assert len(findings) == 1
    assert findings[0].sensitivity_type == "phone_number"
    assert "98765" not in findings[0].masked_text