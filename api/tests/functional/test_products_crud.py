def make_payload(**overrides):
    payload = {'sku': 'RS-001', 'name': 'Running Shoes', 'price': '89.99', 'stock': 150}
    payload.update(overrides)
    return payload


def test_create_and_get_product(client):
    created = client.post('/api/products', json=make_payload())
    assert created.status_code == 201
    product_id = created.json()['id']
    fetched = client.get(f'/api/products/{product_id}')
    assert fetched.status_code == 200
    assert fetched.json()['name'] == 'Running Shoes'


def test_create_duplicate_sku_conflicts(client):
    client.post('/api/products', json=make_payload())
    response = client.post('/api/products', json=make_payload(name='Dup'))
    assert response.status_code == 409


def test_create_blank_name_rejected(client):
    response = client.post('/api/products', json=make_payload(name='   '))
    assert response.status_code == 422


def test_create_negative_stock_rejected(client):
    response = client.post('/api/products', json=make_payload(stock=-1))
    assert response.status_code == 422


def test_get_missing_product(client):
    assert client.get('/api/products/999').status_code == 404


def test_update_product(client):
    product = client.post('/api/products', json=make_payload()).json()
    response = client.put(f"/api/products/{product['id']}", json=make_payload(name='New', price='94.99'))
    assert response.status_code == 200
    assert response.json()['name'] == 'New'
    assert response.json()['price'] == '94.99'


def test_update_missing_product(client):
    assert client.put('/api/products/999', json=make_payload()).status_code == 404


def test_update_conflicting_sku(client):
    first = client.post('/api/products', json=make_payload(sku='A-1')).json()
    client.post('/api/products', json=make_payload(sku='B-1', name='B'))
    response = client.put(f"/api/products/{first['id']}", json=make_payload(sku='B-1'))
    assert response.status_code == 409


def test_delete_product(client):
    product = client.post('/api/products', json=make_payload()).json()
    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_delete_missing_product(client):
    assert client.delete('/api/products/999').status_code == 404


def test_delete_product_with_orders_conflicts(client):
    product = client.post('/api/products', json=make_payload()).json()
    order = client.post('/api/orders', json={'items': [{'product_id': product['id'], 'quantity': 1}]})
    assert order.status_code == 201
    response = client.delete(f"/api/products/{product['id']}")
    assert response.status_code == 409
