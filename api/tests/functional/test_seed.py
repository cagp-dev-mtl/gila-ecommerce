from fastapi.testclient import TestClient

from app.core.db import SessionFactory
from app.core.seed import run_startup_seed, seed_catalog
from app.core.settings import Settings
from app.main import app

SEED = 'name,sku,price,stock\nWidget,WD-1,10.00,5\nGadget,GD-2,20.00,3\n'


def _write(tmp_path, content=SEED):
    path = tmp_path / 'seed.csv'
    path.write_text(content, encoding='utf-8')
    return path


def test_seed_catalog_populates_empty_catalog(tmp_path, client):
    with SessionFactory() as session:
        seed_catalog(session, _write(tmp_path))
    assert client.get('/api/products').json()['total'] == 2


def test_seed_catalog_skips_when_populated(tmp_path, client):
    client.post('/api/products', json={'name': 'Existing', 'sku': 'EX-1', 'price': '9.99', 'stock': 1})
    with SessionFactory() as session:
        seed_catalog(session, _write(tmp_path))
    assert client.get('/api/products').json()['total'] == 1


def test_run_startup_seed_disabled_is_noop(monkeypatch, client):
    monkeypatch.setattr(Settings.get_settings(), 'SEED_ON_STARTUP', False)
    run_startup_seed()
    assert client.get('/api/products').json()['total'] == 0


def test_run_startup_seed_enabled_loads_file(monkeypatch, tmp_path, client):
    settings = Settings.get_settings()
    monkeypatch.setattr(settings, 'SEED_ON_STARTUP', True)
    monkeypatch.setattr(settings, 'SEED_FILE', str(_write(tmp_path)))
    run_startup_seed()
    assert client.get('/api/products').json()['total'] == 2


def test_lifespan_runs_startup_hook():
    with TestClient(app):
        pass
