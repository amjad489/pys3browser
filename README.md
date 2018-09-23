# pyS3browser
Simple web based interface for browsing AWS S3 buckets on web browser. Since I couldn't find much apps for Mac OS. I have created this app using Python-Flask as backend.

## Technologies

- Python-Flask
- Bootstrap
- Jquery

## Python Dependencies

- Flask
- boto3
- humanfriendly

 
# Installation
## Clone repo
```bash
$git clone https://github.com/amjad489/pys3browser.git
```
## Install dependencies
```bash
cd pys3browser
$pip install -r requirements
```
## Run
```bash
$ python app.py                  
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
2018-09-23 14:01:54,639 werkzeug _log():88 INFO      * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

```
Launch browser and access http://localhost:5000/

## Pull Request
If you want to contribute.

## Support

[GitHub issues](https://github.com/amjad489/pys3browser/issues) for bug reports and new feature requests.
