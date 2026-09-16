SAMPLE = (
    'name,sku,description,category,price,stock,weight_kg\n'
    'Running Shoes,RS-001,light,Footwear,$89.99,150,0.35\n'
    'Wireless Mouse,WM-042,mouse,Electronics,29.99,75,0.12\n'
    'Yoga Mat,YM-015,mat,Sports,free,200,1.2\n'
    'Desk Lamp,DL-007,lamp,Home,45.50,-5,2.1\n'
    ',HD-099,noname,Electronics,149.99,30,0.25\n'
    '   ,WS-001,whitespace,Misc,5.00,10,0.1\n'
    ',,,,,,\n'
    'Running Shoes,RS-001,updated,Footwear,94.99,120,0.35\n'
)


def upload(client, content, filename='catalog.csv', content_type='text/csv'):
    return client.post('/api/products/import', files={'file': (filename, content, content_type)})


def test_import_report(client):
    report = upload(client, SAMPLE).json()
    assert report['imported'] == 2
    assert report['updated'] == 1
    assert report['skipped'] == 1
    assert {error['row'] for error in report['errors']} == {4, 5, 6, 7}


def test_import_persists_last_wins(client):
    upload(client, SAMPLE)
    body = client.get('/api/products?search=RS-001').json()
    assert body['items'][0]['price'] == '94.99'
    assert body['items'][0]['description'] == 'updated'


def test_import_is_idempotent(client):
    upload(client, SAMPLE)
    report = upload(client, SAMPLE).json()
    assert report['imported'] == 0
    assert report['updated'] == 3


def test_import_missing_columns(client):
    response = upload(client, 'name,price\nFoo,10\n')
    assert response.status_code == 400


def test_import_non_csv_rejected(client):
    response = upload(client, '{}', filename='data.json', content_type='application/json')
    assert response.status_code == 415


def test_import_non_utf8_rejected(client):
    response = upload(client, b'\xff\xfe\x00bad')
    assert response.status_code == 400


def test_import_too_large_rejected(client):
    content = 'name,sku,price,stock\n' + 'a' * (5 * 1024 * 1024)
    response = upload(client, content)
    assert response.status_code == 413
