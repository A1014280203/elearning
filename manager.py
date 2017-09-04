from app import create_app

app = create_app()


@app.after_request
def allow_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':
    app.run(host='localhost', threaded=True)