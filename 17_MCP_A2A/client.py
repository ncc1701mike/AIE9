"""
Cat Shop MCP Client
-------------------
A custom MCP client that connects to the cat shop server over Streamable HTTP,
authenticates via OAuth (PKCE), and orchestrates a full shopping flow.

Usage:
    python client.py                                  # uses localhost
    MCP_SERVER_URL=https://your-ngrok-url python client.py
"""

import asyncio
import base64
import hashlib
import json
import os
import secrets
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# ── Config ────────────────────────────────────────────────────────────────────

SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
MCP_URL = f"{SERVER_URL}/mcp"
CALLBACK_PORT = 9876
REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/callback"
CLIENT_ID = "cat-shop-custom-client"

# ── OAuth PKCE helpers ────────────────────────────────────────────────────────

def generate_pkce_pair():
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Local callback server to capture the auth code ───────────────────────────

_auth_code: str | None = None
_auth_state: str | None = None

class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code, _auth_state
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _auth_code = params.get("code", [None])[0]
        _auth_state = params.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
        <!DOCTYPE html><html><head>
        <style>
            body { font-family: monospace; background: #000; color: #0f0;
                   display: flex; align-items: center; justify-content: center;
                   min-height: 100vh; margin: 0; }
            .box { text-align: center; }
            h1 { font-size: 2rem; margin-bottom: 1rem; }
            p  { color: #888; }
        </style></head><body>
        <div class="box">
          <h1>&#x1F431; Authorised!</h1>
          <p>You can close this window and return to the terminal.</p>
        </div></body></html>
        """)

    def log_message(self, *args):
        pass  # silence request logs


def _run_callback_server():
    server = HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)
    server.handle_request()   # serve exactly one request then stop


# ── OAuth flow ────────────────────────────────────────────────────────────────

async def do_oauth(client: httpx.AsyncClient) -> str:
    """
    Full OAuth 2.0 + PKCE flow:
      1. Dynamically register the client
      2. Build the authorisation URL and open the browser
      3. Capture the callback code on a local server
      4. Exchange code → access token
    Returns the access token string.
    """

    # 0. Discover OAuth endpoints via well-known metadata
    print("  → Discovering OAuth endpoints...")
    meta_resp = await client.get(f"{SERVER_URL}/.well-known/oauth-authorization-server")
    if meta_resp.status_code == 200:
        meta = meta_resp.json()
        registration_endpoint = meta.get("registration_endpoint", f"{SERVER_URL}/oauth/register")
        authorize_endpoint    = meta.get("authorization_endpoint", f"{SERVER_URL}/authorize")
        token_endpoint        = meta.get("token_endpoint", f"{SERVER_URL}/token")
        print(f"     registration : {registration_endpoint}")
        print(f"     authorize    : {authorize_endpoint}")
        print(f"     token        : {token_endpoint}")
    else:
        # Fall back to MCP SDK defaults
        registration_endpoint = f"{SERVER_URL}/oauth/register"
        authorize_endpoint    = f"{SERVER_URL}/authorize"
        token_endpoint        = f"{SERVER_URL}/token"
        print(f"  ⚠  Discovery failed ({meta_resp.status_code}), using defaults")

    # 1. Dynamic client registration
    print("  → Registering client with the server...")
    reg_resp = await client.post(
        registration_endpoint,
        json={
            "client_id": CLIENT_ID,
            "client_name": "Cat Shop Custom Client",
            "redirect_uris": [REDIRECT_URI],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        },
    )
    if reg_resp.status_code not in (200, 201, 400):
        print(f"  ⚠  Registration returned {reg_resp.status_code}: {reg_resp.text[:200]}")
    reg_data = reg_resp.json() if reg_resp.status_code in (200, 201) else {}
    actual_client_id = reg_data.get("client_id", CLIENT_ID)

    # 2. Start callback listener in background thread
    t = Thread(target=_run_callback_server, daemon=True)
    t.start()

    # 3. Build auth URL and open browser
    verifier, challenge = generate_pkce_pair()
    state = secrets.token_hex(16)
    auth_params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": actual_client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": "read write",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    auth_url = f"{authorize_endpoint}?{auth_params}"

    print(f"\n  → Opening browser for login...")
    print(f"     If the browser doesn't open, visit:\n     {auth_url}\n")
    webbrowser.open(auth_url)

    # 4. Wait for callback
    print("  → Waiting for you to log in...")
    t.join(timeout=120)
    if _auth_code is None:
        raise RuntimeError("OAuth callback timed out — did you log in?")
    print(f"  → Got auth code ✓")

    # 5. Exchange code for token
    token_resp = await client.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": _auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": actual_client_id,
            "code_verifier": verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    access_token = token_data["access_token"]
    print(f"  → Access token obtained ✓\n")
    return access_token


# ── MCP tool helpers ──────────────────────────────────────────────────────────

async def call_tool(session: ClientSession, name: str, **kwargs):
    result = await session.call_tool(name, arguments=kwargs)
    # result.content is a list of content blocks; first is usually TextContent
    raw = result.content[0].text if result.content else "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def as_list(data) -> list:
    """Normalise a tool response that may be a list or a dict with an items key."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "products", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]
    return [data]


def banner(title: str):
    width = 60
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


def print_products(products: list[dict]):
    for p in products:
        print(f"  [{p['id']:>2}] {p['name']:<28} ${p['price']:>6.2f}  ({p['category']})")
        print(f"       {p['description']}")


def print_cart(cart: dict):
    if not cart.get("items"):
        print("  Cart is empty.")
        return
    for item in cart["items"]:
        print(f"  {item['quantity']}x {item['name']:<28} ${item['subtotal']:>6.2f}")
    print(f"  {'':─<40}")
    print(f"  {'TOTAL':<32} ${cart['total']:>6.2f}  ({cart['item_count']} item(s))")


# ── Main shopping flow ────────────────────────────────────────────────────────

async def main():
    print("\n🐱  Cat Shop MCP Client")
    print("=" * 60)
    print(f"  Server : {SERVER_URL}")
    print(f"  MCP    : {MCP_URL}")

    async with httpx.AsyncClient(follow_redirects=True) as http:

        # ── OAuth ────────────────────────────────────────────────────────────
        banner("Step 1 — OAuth Authentication")
        access_token = await do_oauth(http)

        # ── Connect MCP session ──────────────────────────────────────────────
        banner("Step 2 — Connecting MCP Session")
        headers = {"Authorization": f"Bearer {access_token}"}

        async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"  Connected ✓  ({len(tools.tools)} tools available)")
                for t in tools.tools:
                    print(f"    • {t.name}")

                # ── Browse all products ──────────────────────────────────────
                banner("Step 3 — Browse All Products")
                products = as_list(await call_tool(session, "list_products"))
                print_products(products)

                # ── Browse by category ───────────────────────────────────────
                banner("Step 4 — Browse Toys Category")
                toys = as_list(await call_tool(session, "list_products", category="toys"))
                print_products(toys)

                # ── Get a specific product ───────────────────────────────────
                banner("Step 5 — Get Product Details (id=4)")
                product = await call_tool(session, "get_product", product_id=4)
                print(f"  Name        : {product['name']}")
                print(f"  Description : {product['description']}")
                print(f"  Price       : ${product['price']:.2f}")
                print(f"  Category    : {product['category']}")

                # ── Add items to cart ────────────────────────────────────────
                banner("Step 6 — Add Items to Cart")
                items_to_add = [
                    (2, 2),   # 2x Catnip Mouse
                    (4, 1),   # 1x Cozy Cat Bed
                    (6, 3),   # 3x Salmon Treats
                ]
                for product_id, qty in items_to_add:
                    result = await call_tool(session, "add_to_cart",
                                            product_id=product_id, quantity=qty)
                    print(f"  {result.get('message', result)}")

                # ── View cart ────────────────────────────────────────────────
                banner("Step 7 — View Cart")
                cart = await call_tool(session, "view_cart")
                print_cart(cart)

                # ── Remove an item ───────────────────────────────────────────
                banner("Step 8 — Remove Salmon Treats (id=6)")
                result = await call_tool(session, "remove_from_cart", product_id=6)
                print(f"  {result.get('message', result)}")

                # ── View cart again ──────────────────────────────────────────
                banner("Step 9 — Cart After Removal")
                cart = await call_tool(session, "view_cart")
                print_cart(cart)

                # ── Checkout ─────────────────────────────────────────────────
                banner("Step 10 — Checkout")
                order = await call_tool(session, "checkout")
                if "error" in order:
                    print(f"  Error: {order['error']}")
                else:
                    print(f"  Order ID : {order['order_id']}")
                    print(f"  Status   : {order['status']}")
                    print(f"  Total    : ${order['total']:.2f}")
                    print(f"\n  {order['message']}")

                print(f"\n{'=' * 60}")
                print("  Shopping flow complete! 🎉")
                print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
