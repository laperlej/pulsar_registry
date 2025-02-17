from fastapi import APIRouter
from http import HTTPStatus
import unittest

router = APIRouter()

@router.get("/api/pulsar/health", status_code=HTTPStatus.OK)
async def health() -> str:
    print("Health check")
    return "OK"

class HealthControllerTests(unittest.IsolatedAsyncioTestCase):
    async def test_health(self):
        res = await health()
        self.assertEqual(res, "OK")
