from flask import Flask, Response, render_template, request, redirect
import boto3
import humanfriendly
import logging
from logging.handlers import RotatingFileHandler
import os
import ConfigParser

logger = logging.getLogger()
handler = logging.StreamHandler()
# handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=10)
formatter = logging.Formatter(
        '%(asctime)s %(name)s %(funcName)s():%(lineno)i %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__, static_url_path='/static')

conn = None
s3_bucket_name = None

config_file = 'config.ini'


def validate_config_file():
    if os.path.exists(config_file):
        logging.info("config file exists")
    else:
        logging.error("config file doesn't exists, creating config.")
        config = ConfigParser.RawConfigParser()
        config.add_section('credentials')
        config.set('credentials', 'aws_access_key', '')
        config.set('credentials', 'aws_secret_key', '')
        config.set('credentials', 's3_bucket_name', '')
        with open(config_file, 'wb') as cfg_file:
            config.write(cfg_file)


def upload_file_to_s3(s3_file, bucket_name):
    try:

        conn.upload_fileobj(s3_file, bucket_name, s3_file.filename)

    except Exception as e:
        print("Something Happened: ", e)
        logging.error(e)
        return e


@app.route('/')
def home_page():
    global conn
    global s3_bucket_name
    validate_config_file()
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file))
    s3_access_id = config.get('credentials', 'aws_access_key')
    s3_access_key = config.get('credentials', 'aws_secret_key')
    s3_bucket_name = config.get('credentials', 's3_bucket_name')
    conn = boto3.client('s3', aws_access_key_id=s3_access_id, aws_secret_access_key=s3_access_key)
    if s3_access_id and s3_access_key and s3_bucket_name:
        return render_template('index.html', bucketname=s3_bucket_name)
    else:
        return render_template('configure.html')


@app.route('/browse_root')
def browse_root():
    logging.info(s3_bucket_name)
    response = conn.list_objects_v2(
            Bucket=s3_bucket_name,
            Delimiter='/',
        )

    def generate():
        yield "<p class='card-text'><table class='table table-sm'><thead><tr><th scope='col'><p class='text-left'>Key</p></th><th scope='col'><p class='text-left'>Size</p></th><th scope='col'><p class='text-left'>LastModified</p></th></tr></thead><tbody>"
        if "CommonPrefixes" in response:
            for s3_folder in response["CommonPrefixes"]:
                yield "<tr><td><p class='text-left'>" \
                      "<button id='" + s3_folder['Prefix'] + "' class='btn btn-link'><i class='far fa-folder'></i> " + \
                      s3_folder['Prefix'] + "</button></p></td><td></td><td></td></tr>"
        if "Contents" in response:
            for s3_Key in response["Contents"]:
                yield "<tr><td><p class='text-left'>" \
                      "<button id='" + s3_Key['Key'] + "' class='btn btn-link' > <i class='far fa-file'></i> " + \
                      s3_Key['Key'] + "</button></p></td><td>" + \
                      humanfriendly.format_size(s3_Key['Size']) + "</td><td>" + \
                      s3_Key['LastModified'].strftime("%Y-%m-%d %H:%M:%S %Z") + "</td></tr>"
        yield "</tbody></table></p>"
    return Response(generate())


@app.route('/browse_further', methods=['POST'])
def browse_further():
    logging.info(s3_bucket_name)
    response = conn.list_objects_v2(
            Bucket=s3_bucket_name,
            Delimiter='/',
            Prefix=request.form['s3path'],

        )

    logging.info("user clicked on : " + request.form['s3path'])

    def generate():
        yield "<h9 class='card-title'>"
        if 'Prefix' in response:
            yield "<span id='back-button-path' class='badge badge-pill badge-warning'>" + response['Prefix'] + "</span>"
        else:
            yield "<span class='badge badge-pill badge-warning'>" + "/" + "</span>"
        yield "</h9><p class='card-text'><table class='table table-sm'><thead><tr><th scope='col'><p class='text-left'>Key</p></th><th scope='col'><p class='text-left'>Size</p></th><th scope='col'><p class='text-left'>LastModified</p></th></tr></thead><tbody>"
        if "CommonPrefixes" in response:
            for s3_folder in response["CommonPrefixes"]:
                folder_p = s3_folder['Prefix'].split('/')[-2]
                yield "<tr><td><p class='text-left'>" \
                      "<button id='" + s3_folder['Prefix'] + "' class='btn btn-link'><i class='far fa-folder'></i> " + \
                      folder_p + "</button></p></td><td></td><td></td></tr>"

        if "Contents" in response:
            for s3_Key in response["Contents"]:
                if response["Prefix"] != s3_Key['Key']:
                    file_p = s3_Key['Key'].split('/')[-1]
                    yield "<tr><td><p class='text-left'>" \
                          "<button id='" + s3_Key['Key'] + "' class='btn btn-link' ><i class='far fa-file'></i> " + \
                          file_p + "</button></p></td><td>" + \
                          humanfriendly.format_size(s3_Key['Size']) + "</td><td>" + \
                          s3_Key['LastModified'].strftime("%Y-%m-%d %H:%M:%S %Z") + "</td></tr>"
        yield "</tbody></table></p>"
    return Response(generate())


@app.route('/saveConfig', methods=['POST'])
def save_config_file():
    global conn
    global s3_bucket_name
    config = ConfigParser.RawConfigParser()
    config.readfp(open(config_file))
    config.set('credentials', 'aws_access_key', request.form['accesskey'])
    config.set('credentials', 'aws_secret_key', request.form['secretkey'])
    config.set('credentials', 's3_bucket_name', request.form['bucketname'])
    with open(config_file, 'wb') as cfg_file:
        config.write(cfg_file)
        logging.info("credentials saved to file.")
    s3_access_id = config.get('credentials', 'aws_access_key')
    s3_access_key = config.get('credentials', 'aws_secret_key')
    s3_bucket_name = config.get('credentials', 's3_bucket_name')
    conn = boto3.client('s3', aws_access_key_id=s3_access_id, aws_secret_access_key=s3_access_key)
    return redirect('/', code=302)


@app.route('/uploadFile', methods=['POST'])
def upload_file():
    key_file = request.files['fileInput']
    upload_file_to_s3(key_file, s3_bucket_name)

    return redirect('/', code=302)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
