import os
import sys
from uuid import UUID

sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'app'))

from schemas.otp import VerifyOTPRequest
from service.auth_service import build_login_payload, success_response


def test_otp_response_contains_user_id_only():
    response = success_response('OTP sent successfully', {'user_id': '7b0d4b3c-6a8c-4f9f-9a3d-cd5c8b8d2f41'})

    assert response['success'] is True
    assert response['message'] == 'OTP sent successfully'
    assert response['data']['user_id'] == '7b0d4b3c-6a8c-4f9f-9a3d-cd5c8b8d2f41'
    assert 'otp' not in response
    assert 'otp' not in response['data']


def test_verify_otp_request_accepts_user_id_and_otp_only():
    payload = VerifyOTPRequest(user_id='7b0d4b3c-6a8c-4f9f-9a3d-cd5c8b8d2f41', otp='123456')

    assert payload.user_id == UUID('7b0d4b3c-6a8c-4f9f-9a3d-cd5c8b8d2f41')
    assert payload.otp == '123456'


def test_build_login_payload_contains_common_fields():
    payload = build_login_payload(
        account_id='acc-123',
        email='ngo@example.com',
        name='Care NGO',
        phone='9876543210',
        role='ngo_admin',
        account_type='ngo',
    )

    assert payload['id'] == 'acc-123'
    assert payload['name'] == 'Care NGO'
    assert payload['role'] == 'ngo_admin'
    assert payload['token_type'] == 'bearer'
