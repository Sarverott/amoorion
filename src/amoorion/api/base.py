"""API: `POST /methods/<name>` with the method's params as the body,
`POST /hooks/<name>` for incoming webhooks, `GET /` for what is there.

Method calls need `Authorization: Bearer <api/token from the vault>`; without
that secret in the vault every method call is refused. Hooks verify
themselves (see amoorion.hooks).
"""

import argparse
import hmac
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from amoorion import __version__
from amoorion.core import AmoorionError, JsonView
from amoorion.hooks import HOOKS, Forbidden
from amoorion.methods import METHODS, Method
from amoorion.vault import Vault, open_vault

bearer = HTTPBearer(auto_error=False)


def create_app(vault: Vault | None = None) -> FastAPI:
    vault = vault or open_vault()
    app = FastAPI(title="amoorion", version=__version__)

    def authorized(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
        try:
            token = vault.get("api/token")
        except AmoorionError:
            raise HTTPException(503, "no api/token in the vault: method calls are off") from None
        if credentials is None or not hmac.compare_digest(credentials.credentials.encode(), token.encode()):
            raise HTTPException(401, "wrong or missing bearer token")

    @app.get("/")
    def index() -> dict[str, Any]:
        return {"name": "amoorion", "version": __version__, "methods": METHODS.names(), "hooks": HOOKS.names()}

    def add_method(method: type[Method]) -> None:
        Params = method.Params

        def call(params: Params) -> Any:  # type: ignore[valid-type]
            try:
                return JsonView().render(method(vault).run(params))
            except AmoorionError as error:
                raise HTTPException(400, str(error)) from None

        app.post(
            f"/methods/{method.name}",
            summary=method.description,
            dependencies=[Depends(authorized)],
            name=method.name,
        )(call)

    for name in METHODS.names():
        add_method(METHODS.get(name))

    @app.post("/hooks/{name}")
    async def hook(name: str, request: Request) -> Any:
        if name not in HOOKS:
            raise HTTPException(404, f"no hook named {name!r}")
        body = await request.body()
        try:
            payload = await request.json()
        except ValueError:
            raise HTTPException(400, "body is not JSON") from None
        try:
            message = HOOKS.get(name)(vault).handle(body, request.headers, payload)
        except Forbidden as error:
            raise HTTPException(403, str(error)) from None
        except AmoorionError as error:
            raise HTTPException(400, str(error)) from None
        return JsonView().render(message)

    return app


def serve(args: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run(create_app(), host=args.host, port=args.port)
