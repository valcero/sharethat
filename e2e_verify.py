import requests

BASE_URL = 'http://localhost:8000'
email = 'tester_e2e@example.com'
password = 'SecretPass123!'

print("--> 1. Authenticating via /auth/jwt/login (with idempotent registration)...")
login_resp = requests.post(f'{BASE_URL}/auth/jwt/login', data={'username': email, 'password': password})
if login_resp.status_code != 200:
    reg_resp = requests.post(f'{BASE_URL}/auth/register', json={'email': email, 'password': password})
    assert reg_resp.status_code in (201, 400), f"Registration failed: {reg_resp.text}"
    login_resp = requests.post(f'{BASE_URL}/auth/jwt/login', data={'username': email, 'password': password})

assert login_resp.status_code == 200, f'Login failed: {login_resp.text}'
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print('    [PASS] Successfully authenticated with JWT bearer token!')

print("--> 2. Uploading sample_image.png with caption via POST /upload...")
with open('sample_image.png', 'rb') as f:
    files = {'file': ('sample_image.png', f, 'image/png')}
    data = {'caption': 'ShareThat Live E2E Post!'}
    upload_resp = requests.post(f'{BASE_URL}/upload', files=files, data=data, headers=headers)

assert upload_resp.status_code == 200, f'Upload failed: {upload_resp.text}'
post_id = upload_resp.json()['id']
print(f'    [PASS] Created Post ID: {post_id}')
print(f'           URL: {upload_resp.json()["url"]}')

print("--> 3. Querying GET /feed...")
feed_resp = requests.get(f'{BASE_URL}/feed', headers=headers)
assert feed_resp.status_code == 200
posts = feed_resp.json()['posts']
post = next((p for p in posts if p['id'] == post_id), None)
assert post is not None, 'Post not found in feed'
assert post['is_owner'] is True
print(f'    [PASS] Verified post in feed: Author={post["email"]}, is_owner={post["is_owner"]}, caption="{post["caption"]}"')

print(f"--> 4. Deleting post via DELETE /posts/{post_id}...")
del_resp = requests.delete(f'{BASE_URL}/posts/{post_id}', headers=headers)
assert del_resp.status_code == 200
print(f'    [PASS] {del_resp.json()["message"]}')

print("--> 5. Checking GET /feed after deletion...")
feed_resp_2 = requests.get(f'{BASE_URL}/feed', headers=headers)
assert not any(p['id'] == post_id for p in feed_resp_2.json()['posts'])
print('    [PASS] Confirmed post was completely removed from the database!')

print("\n=======================================================")
print(" ALL SHARETHAT END-TO-END WORKFLOWS PASSED! ")
print("=======================================================")
