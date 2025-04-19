import pytest
from src.services.email import (
    send_email,
    send_reset_password_email,
)

def test_send_email():
    send_email("to@example.com", "subject", "body")


def test_send_reset_password_email(monkeypatch):
    monkeypatch.setattr("src.services.email.send_email", lambda to, s, b: None)
    send_reset_password_email("to@example.com", "token")


