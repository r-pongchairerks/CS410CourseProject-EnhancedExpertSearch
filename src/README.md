# ExpertSearch

To run the code, run the following command from `ExpertSearch` (tested with Python2.7 on MacOS and Linux):

`gunicorn server:app -b 127.0.0.1:8095` 

The site should be available at http://localhost:8095/

MacOSX: 
open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security
