from index import app
import json

def handler(request, context):
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('method', 'POST'),
        headers=request.get('headers', {}),
        data=request.get('body', ''),
        environ_base={'REMOTE_ADDR': request.get('client_ip', '127.0.0.1')}
    ):
        try:
            response = app.full_dispatch_request()
            return {
                "statusCode": response.status_code,
                "headers": dict(response.headers),
                "body": response.get_data().decode('utf-8')
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }