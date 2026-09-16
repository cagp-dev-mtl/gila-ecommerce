import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository


def create_product(client, **overrides):
    payload = {'sku': 'CHK-1', 'name': 'Item', 'price': '25.00', 'stock': 10}
    payload.update(overrides)
    return client.post('/api/products', json=payload).json()


def test_checkout_success_decrements_stock(client):
    product = create_product(client)
    response = client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 3}]})
    assert response.status_code == 201
    order = response.json()
    assert order['status'] == 'paid'
    assert order['total'] == '75.00'
    assert order['payment_reference'].startswith('FAKE-')
    assert client.get(f"/api/products/{product['id']}").json()['stock'] == 7


def test_checkout_insufficient_stock(client):
    product = create_product(client, stock=2)
    response = client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 5}]})
    assert response.status_code == 409


def test_checkout_unknown_product(client):
    response = client.post('/api/orders', json={'items': [{'product_id': 999, 'quantity': 1}]})
    assert response.status_code == 404


def test_checkout_empty_items_rejected(client):
    assert client.post('/api/orders', json={'items': []}).status_code == 422


def test_checkout_zero_quantity_rejected(client):
    product = create_product(client)
    response = client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 0}]})
    assert response.status_code == 422


def test_checkout_aggregates_duplicate_items(client):
    product = create_product(client, stock=10)
    response = client.post(
        '/api/orders',
        json={
            'items': [
                {'product_id': product['id'], 'quantity': 2},
                {'product_id': product['id'], 'quantity': 2},
            ]
        },
    )
    order = response.json()
    assert len(order['items']) == 1
    assert order['items'][0]['quantity'] == 4


def test_checkout_idempotent_replay(client):
    product = create_product(client, stock=10)
    headers = {'Idempotency-Key': 'key-1'}
    body = {'items': [{'product_id': product['id'], 'quantity': 2}]}
    first = client.post('/api/orders', json=body, headers=headers)
    second = client.post('/api/orders', json=body, headers=headers)
    assert first.json()['id'] == second.json()['id']
    assert client.get(f"/api/products/{product['id']}").json()['stock'] == 8


def test_get_order(client):
    product = create_product(client)
    order = client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 1}]}).json()
    fetched = client.get(f"/api/orders/{order['id']}")
    assert fetched.status_code == 200
    assert fetched.json()['id'] == order['id']


def test_get_missing_order(client):
    assert client.get('/api/orders/999').status_code == 404


def test_checkout_integrity_conflict_returns_existing(client, monkeypatch):
    product = create_product(client, stock=10)
    headers = {'Idempotency-Key': 'race'}
    body = {'items': [{'product_id': product['id'], 'quantity': 1}]}
    first = client.post('/api/orders', json=body, headers=headers).json()

    original = OrderRepository.get_by_idempotency_key
    state = {'missed': False}

    def flaky(self, key):
        if not state['missed']:
            state['missed'] = True
            return None
        return original(self, key)

    monkeypatch.setattr(OrderRepository, 'get_by_idempotency_key', flaky)
    second = client.post('/api/orders', json=body, headers=headers)
    assert second.status_code == 201
    assert second.json()['id'] == first['id']


def test_checkout_integrity_error_without_key_propagates(client, monkeypatch):
    product = create_product(client, stock=10)

    def boom(self):
        raise IntegrityError('stmt', {}, Exception('orig'))

    monkeypatch.setattr(Session, 'commit', boom)
    with pytest.raises(IntegrityError):
        client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 1}]})
