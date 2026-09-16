import pytest

CATALOG = [
    {'sku': 'RS-001', 'name': 'Running Shoes', 'description': 'light shoes', 'category': 'Footwear', 'price': '89.99', 'stock': 150},
    {'sku': 'HB-002', 'name': 'Hiking Boots', 'description': 'waterproof boots', 'category': 'Footwear', 'price': '159.99', 'stock': 40},
    {'sku': 'WM-042', 'name': 'Wireless Mouse', 'description': 'ergonomic mouse', 'category': 'Electronics', 'price': '29.99', 'stock': 75},
]


@pytest.fixture
def catalog(client):
    for product in CATALOG:
        client.post('/api/products', json=product)


def test_list_envelope(client, catalog):
    body = client.get('/api/products').json()
    assert body['total'] == 3
    assert body['pages'] == 1


def test_search_by_description(client, catalog):
    body = client.get('/api/products?search=waterproof').json()
    assert [item['sku'] for item in body['items']] == ['HB-002']


def test_search_by_sku(client, catalog):
    body = client.get('/api/products?search=WM-042').json()
    assert body['total'] == 1


def test_category_filter(client, catalog):
    body = client.get('/api/products?category=Electronics').json()
    assert body['total'] == 1


def test_pagination(client, catalog):
    body = client.get('/api/products?page_size=2&page=2').json()
    assert body['page'] == 2
    assert len(body['items']) == 1


def test_sort_price_desc(client, catalog):
    body = client.get('/api/products?sort=price&order=desc').json()
    assert [item['price'] for item in body['items']] == ['159.99', '89.99', '29.99']


def test_sort_newest(client, catalog):
    body = client.get('/api/products?sort=newest&order=desc').json()
    assert body['items'][0]['sku'] == 'WM-042'


def test_invalid_sort_rejected(client):
    assert client.get('/api/products?sort=hack').status_code == 422


def test_categories_endpoint(client, catalog):
    assert client.get('/api/products/categories').json() == ['Electronics', 'Footwear']


def test_empty_catalog_metadata(client):
    body = client.get('/api/products').json()
    assert body['total'] == 0
    assert body['pages'] == 0
