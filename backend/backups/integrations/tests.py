import json
from unittest.mock import Mock
from urllib.error import URLError

from django.test import SimpleTestCase

from .oxidized import OxidizedClient, OxidizedError


class ResponseContext:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class OxidizedClientTests(SimpleTestCase):
    def test_list_nodes_reads_json(self):
        nodes = [{"name": "switch-01", "model": "ios"}]
        opener = Mock(return_value=ResponseContext(json.dumps(nodes).encode()))
        client = OxidizedClient("http://127.0.0.1:8888/", opener=opener)

        result = client.list_nodes()

        self.assertEqual(result, nodes)
        request = opener.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:8888/nodes.json")
        self.assertEqual(request.method, "GET")

    def test_queue_node_uses_put_and_escapes_name(self):
        opener = Mock(return_value=ResponseContext(b"queued"))
        client = OxidizedClient("http://127.0.0.1:8888", opener=opener)

        result = client.queue_node("sede/switch 01")

        self.assertEqual(result, "queued")
        request = opener.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://127.0.0.1:8888/node/next/sede%2Fswitch%2001.json",
        )
        self.assertEqual(request.method, "PUT")
        self.assertEqual(request.data, b"{}")
        self.assertEqual(request.headers["Content-type"], "application/json")

    def test_fetch_config_supports_group(self):
        opener = Mock(return_value=ResponseContext(b"hostname switch-01"))
        client = OxidizedClient("http://127.0.0.1:8888", opener=opener)

        result = client.fetch_config("switch-01", group="facultad norte")

        self.assertEqual(result, "hostname switch-01")
        request = opener.call_args.args[0]
        self.assertEqual(
            request.full_url,
            (
                "http://127.0.0.1:8888/node/fetch/"
                "facultad%20norte/switch-01"
            ),
        )

    def test_connection_error_is_converted_to_domain_error(self):
        opener = Mock(side_effect=URLError("connection refused"))
        client = OxidizedClient("http://127.0.0.1:8888", opener=opener)

        with self.assertRaisesMessage(
            OxidizedError,
            "No fue posible conectar con la API de Oxidized.",
        ):
            client.list_nodes()
