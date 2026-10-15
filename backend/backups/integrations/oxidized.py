import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class OxidizedError(Exception):
    """Error controlado al comunicarse con la API de Oxidized."""


class OxidizedClient:
    def __init__(self, base_url, timeout=10, opener=urlopen):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.opener = opener

    def list_nodes(self):
        response = self._request("/nodes.json", expected_json=True)
        if not isinstance(response, list):
            raise OxidizedError("Oxidized devolvió una lista de nodos inválida.")
        return response

    def reload_nodes(self):
        return self._request("/reload")

    def queue_node(self, node_name):
        node = self._encode_node(node_name)
        return self._request(
            f"/node/next/{node}.json",
            method="PUT",
            json_body={},
        )

    def fetch_config(self, node_name, group=None):
        node = self._encode_node(node_name)
        if group:
            encoded_group = quote(str(group).strip(), safe="")
            path = f"/node/fetch/{encoded_group}/{node}"
        else:
            path = f"/node/fetch/{node}"
        return self._request(path)

    def _encode_node(self, node_name):
        value = str(node_name).strip()
        if not value:
            raise OxidizedError("El nombre del nodo de Oxidized es obligatorio.")
        return quote(value, safe="")

    def _request(self, path, method="GET", expected_json=False, json_body=None):
        data = None
        headers = {"Accept": "application/json, text/plain"}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            raise OxidizedError(
                f"Oxidized respondió con HTTP {error.code} para {path}."
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise OxidizedError(
                "No fue posible conectar con la API de Oxidized."
            ) from error

        if not expected_json:
            return body
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise OxidizedError("Oxidized devolvió una respuesta JSON inválida.") from error
