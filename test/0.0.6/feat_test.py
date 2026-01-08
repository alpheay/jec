import asyncio
import inspect
from fastapi import Request
from jec_api.decorators import version

# Case 1: Function WITHOUT request param
@version(">=1.0.0")
async def endpoint_without_request():
    return "ok"

# Case 2: Function WITH request param
@version(">=1.0.0")
async def endpoint_with_request(request: Request):
    return "ok"

def test():
    print("Checking signature of endpoint_without_request...")
    sig = inspect.signature(endpoint_without_request)
    print(f"Signature: {sig}")
    
    # Check if request param is present
    has_request = 'request' in sig.parameters
    print(f"Has 'request' in parameters: {has_request}")
    
    if has_request:
        param = sig.parameters['request']
        print(f"Request param kind: {param.kind}")
        print(f"Request param default: {param.default}")
    
    print("\nChecking signature of endpoint_with_request...")
    sig2 = inspect.signature(endpoint_with_request)
    print(f"Signature: {sig2}")
    has_request2 = 'request' in sig2.parameters
    print(f"Has 'request' in parameters: {has_request2}")



    

if __name__ == "__main__":
    test()
