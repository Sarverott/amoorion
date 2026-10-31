"""Post from inside another program, by the API: Python's standard library only.

Blender, GIMP, OBS and ComfyUI each run Python scripts with their own interpreter,
where amoorion isn't installed. They only need to reach a running `amoorion api`. Copy
this file there; call it when a render ends, an export is done or a stream starts.
The token is amoorion's `api/token`; read it from where that program keeps settings.
"""

import json
import urllib.request


def post(
    text: str,
    to: list[str],
    token: str,
    api: str = "http://127.0.0.1:8000",
) -> list[dict]:

    request = urllib.request.Request(
        f"{api}/methods/publish",
        data=json.dumps(
            {
                "text": text,
                "to": to,
            }
        ).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)
