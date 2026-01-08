import uvicorn
import webbrowser
import requests
import time
import threading
from typing import List
from pydantic import BaseModel
from jec_api.core import Core
from jec_api.route import Route

# --- Mock Data Structures ---
class UserRequest(BaseModel):
    name: str
    age: int
    active: bool = True

class UserResponse(BaseModel):
    id: int
    name: str
    status: str

# --- Mock Route ---
class UserRoute(Route):
    path = "/users"
    
    async def get(self) -> List[UserResponse]:
        return [
            UserResponse(id=1, name="Alice", status="active"),
            UserResponse(id=2, name="Bob", status="inactive")
        ]
    
    async def post(self, data: UserRequest) -> UserResponse:
        return UserResponse(id=99, name=data.name, status="pending")

# --- App Setup ---
app = Core()
app.register(UserRoute)
app.tinker(dev=True)

def run_checks():
    time.sleep(2) # Give server time to start
    
    base_url = "http://127.0.0.1:8000/__dev__"
    print(f"Checking {base_url}...")
    
    # 1. Check endpoints API
    try:
        resp = requests.get(f"{base_url}/api/endpoints")
        print(f"GET /api/endpoints status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data)} endpoints")
            for ep in data:
                print(f" - {ep['method']} {ep['path']}")
                if ep['path'].endswith('/users') and ep['method'] == 'POST':
                    print("   Input Schema found:", ep['input_schema'] is not None)
    except Exception as e:
        print(f"Error checking API: {e}")

    # 2. Check UI for tester integration
    try:
        resp = requests.get(f"{base_url}/")
        if "tester-overlay" in resp.text:
            print("SUCCESS: UI contains tester-overlay")
        else:
            print("FAILURE: UI missing tester-overlay")
            
        if "toggleTester()" in resp.text:
            print("SUCCESS: UI contains toggleTester logic")
        else:
            print("FAILURE: UI missing toggleTester logic")
    except Exception as e:
        print(f"Error checking UI: {e}")
        
    print("Verification complete. Press Ctrl+C to exit server.")

if __name__ == "__main__":
    t = threading.Thread(target=run_checks, daemon=True)
    t.start()
    app.run()
