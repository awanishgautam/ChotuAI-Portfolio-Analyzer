from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

STREAMLIT_URL = "http://localhost:8501"


@app.api_route(
    "/callback",
    methods=["GET", "POST"],
)
async def callback(request: Request):

    api_session = None

    # POST from Breeze
    if request.method == "POST":

        form = await request.form()

        api_session = form.get("API_Session")

    # Fallback
    if not api_session:

        api_session = (
            request.query_params.get("API_Session")
            or request.query_params.get("apisession")
        )

    if not api_session:

        return {
            "error": "API_Session missing"
        }

    return RedirectResponse(
        f"http://localhost:8501/?broker=ICICI_DIRECT&apisession={api_session}",
        status_code=302,
    )