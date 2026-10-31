"""API: `POST /methods/<name>` with the method's params as the body,
`POST /hooks/<name>` for incoming webhooks (kept in the inbox), `GET /` for
what is there.

Method calls need `Authorization: Bearer <api/token from the vault>`; without
that secret in the vault every method call is refused. Hooks verify
themselves (see amoorion.hooks).
"""

import argparse
import hmac
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from amoorion import __version__
from amoorion.core import AmoorionError, JsonView
from amoorion.dataset import Dataset
from amoorion.hooks import HOOKS, Forbidden
from amoorion.inbox import Inbox
from amoorion.methods import METHODS, Method
from amoorion.methods.all_params import NotifyParams
from amoorion.vault import Vault, open_vault

bearer = HTTPBearer(auto_error=False)


def create_app(
    vault: Vault | None = None,
    inbox: Inbox | None = None,
    dataset: Dataset | None = None,
) -> FastAPI:
    """The FastAPI application: one route per method, the hooks, and a token check.

    Routes are made from `METHODS`, so a new method needs nothing here. Whatever isn't
    passed comes from the environment: the vault of `.env` and the default inbox.
    """

    vault = vault or open_vault()

    inbox = inbox or Inbox()

    app = FastAPI(
        title="amoorion",
        version=__version__,
    )

    def authorized(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None, Depends(bearer)
        ],
    ) -> None:

        try:
            token = vault.get("api/token")
        except AmoorionError:
            raise HTTPException(
                503,
                "no api/token in the vault: method calls are off",
            ) from None

        if credentials is None or not hmac.compare_digest(
            credentials.credentials.encode(), token.encode()
        ):
            raise HTTPException(
                401,
                "wrong or missing bearer token",
            )

    @app.get("/")
    def index() -> dict[str, Any]:

        return {
            "name": "amoorion",
            "version": __version__,
            "methods": METHODS.names(),
            "hooks": HOOKS.names(),
        }

    def add_method(method: type[Method]) -> None:

        Params = method.Params

        def call(params: Params) -> Any:  # type: ignore[valid-type]

            try:
                return JsonView().render(
                    method(
                        vault,
                        inbox=inbox,
                        dataset=dataset,
                    ).run(params)
                )
            except AmoorionError as error:
                raise HTTPException(
                    400,
                    str(error),
                ) from None

        app.post(
            f"/methods/{method.name}",
            summary=method.description,
            dependencies=[Depends(authorized)],
            name=method.name,
        )(call)

    for name in METHODS.names():
        add_method(METHODS.get(name))

    @app.post("/hooks/{name}")
    async def hook(
        name: str,
        request: Request,
    ) -> Any:

        if name not in HOOKS:
            raise HTTPException(
                404,
                f"no hook named {name!r}",
            )

        body = await request.body()

        try:
            payload = await request.json()
        except ValueError:
            raise HTTPException(
                400,
                "body is not JSON",
            ) from None

        try:
            hook_ = HOOKS.get(name)(vault)

            message = hook_.handle(
                body,
                request.headers,
                payload,
            )
        except Forbidden as error:
            raise HTTPException(
                403,
                str(error),
            ) from None
        except AmoorionError as error:
            raise HTTPException(
                400,
                str(error),
            ) from None

        kept = inbox.keep([message]) if message else []

        for new in kept:  # not while the service waits on the event loop: other platforms answer slowly
            links = [new.url] if new.url else []

            await run_in_threadpool(
                METHODS.get("notify")(
                    vault,
                    inbox=inbox,
                ).run,
                NotifyParams(
                    text=new.text,
                    links=links,
                ),
            )

        answer = hook_.answer(payload)

        if answer is not None:
            return answer

        return JsonView().render(kept[0]) if kept else {}

    return app


def serve(args: argparse.Namespace) -> None:
    """Run the API until stopped: `amoorion api`."""

    import uvicorn

    uvicorn.run(
        create_app(),
        host=args.host,
        port=args.port,
    )
