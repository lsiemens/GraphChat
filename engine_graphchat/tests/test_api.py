import os.path

import schemathesis

path, _ = os.path.split(os.path.abspath(__file__))

schema = schemathesis.openapi.from_url("http://localhost:8000/openapi.json")
config = schemathesis.Config.from_path(os.path.join(path, "schemathesis.toml"))


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
