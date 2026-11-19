import pytest

from jobhunt.workspace import Workspace, init_workspace


@pytest.fixture
def ws(tmp_path) -> Workspace:
    root = tmp_path / "me"
    init_workspace(root)
    return Workspace(root)
