#!/usr/bin/python3
import time
from http.client import RemoteDisconnected
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import sys
import json
import configparser
from functools import wraps
from waitress import serve
from flask import Flask, request, abort, jsonify

configparser = configparser.ConfigParser()
configparser.read('config.ini')
rpcuser = configparser['RPC']['user']
rpcpassword = configparser['RPC']['password']
rpchost = configparser['RPC']['host']
rpcport = configparser['RPC']['port']

host = configparser['Server']['host']
port = configparser['Server']['port']
authorization = configparser['Server']['authorization']

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile("config.py")

def connect():
    try:
        rpc = AuthServiceProxy("http://%s:%s@%s:%s" % (rpcuser, rpcpassword, rpchost, rpcport), timeout=120)
        print("[+] RPC Connection successful")
        return rpc
    except Exception as e:
        print("[-] RPC Connection failed, aborting")
        sys.exit(str(e))


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header == authorization:
            return f(*args, **kwargs)

        abort(401, 'Invalid token')

    return decorated

# --------- Errors ---------
@app.errorhandler(400)
def bad_request(r):
    return {'error': '%s' % r.description}, 400


@app.errorhandler(401)
def unauthorized(r):
    return {'error': '%s' % r.description}, 401


@app.errorhandler(404)
def not_found(r):
    return {'error': '%s' % r.description}, 404


@app.errorhandler(405)
def method_not_allowed(r):
    return {'error': '%s' % r.description}, 405


@app.errorhandler(500)
def internal_server_error(r):
    return {'error': '%s' % r.description}, 500


# --------- Routes ---------
@app.route('/get_received/<string:address>', defaults={'min_conf': 2}, methods=['GET'])
@app.route('/get_received/<string:address>/<int:min_conf>', methods=['GET'])
@auth_required
def get_received(address, min_conf):
    try:
        rpc = connect()
        data = rpc.getreceivedbyaddress(address, int(min_conf))
        return {'received': "%.8f" % data}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/get_balance/', methods=['GET'])
@auth_required
def get_balance():
    try:
        rpc = connect()
        data = rpc.getbalance()
        return {'balance': '%.8f' % data}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/create_address', methods=['POST'])
@auth_required
def create_address():
    try:
        rpc = connect()
        address = rpc.getnewaddress()
        return {'address': address}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/validate_address/<string:address>/', methods=['GET'])
@auth_required
def validate_address(address):
    try:
        rpc = connect()
        is_valid = rpc.validateaddress(address)['isvalid']
        return {'is_valid': is_valid}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/transfer', methods=['POST'])
@auth_required
def transfer():
    try:
        data = json.loads(request.data)
        to_address = str(data['to'])
        amount = float(data['amount'])
    except:
        return abort(400, 'Invalid data')

    try:
        rpc = connect()
        txid = rpc.sendtoaddress(to_address, amount, "", "", True)
        print(str(txid))
        return {'transaction_id': txid}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    serve(app, host=host, port=port)
