from app.security import LoginThrottle


def test_throttle_can_be_cleared_after_success():
    throttle = LoginThrottle(limit=1)
    throttle.failed("client")
    assert not throttle.allowed("client")
    throttle.succeeded("client")
    assert throttle.allowed("client")
