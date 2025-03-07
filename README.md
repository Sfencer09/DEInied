<img src="DEInied.png" height="300" width="300">

Automated form submission for: http://enddei.ed.gov/
 
# Setup

You will need to get `chromedriver` from here for your version of chrome: https://googlechromelabs.github.io/chrome-for-testing/

Download the `chromedriver` for your version and put it in PATH, i.e.: `/usr/bin/chromedriver` on OSX/Linux.
Tested on python@3.10. Python@3.12 will require additional setup.  

```shell
pyenv shell 3.10
git clone https://github.com/WarezWhisperers/DEInied.git
cd DEInied
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 DEInied.py --help
```

If you get certificate errors, you might need to add your Selenium Wire CA cert to the trust store.
 
Linux:
```shell
python -m seleniumwire extractcert
sudo cp ./ca.crt /usr/local/share/ca-certificates/seleniumwire-ca.crt
sudo update-ca-certificates
```
OSX:
```shell
python -m seleniumwire extractcert
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ./ca.crt
```

# Usage

This will upload the file you specify, and you can use a residential rotating proxy service to increase success chances.

```shell
usage: DEInied.py [-h] --file-attachment FILE_ATTACHMENT [--proxy PROXY]

options:
  -h, --help            show this help message and exit
  --file-attachment FILE_ATTACHMENT
                        Path to the file to upload
  --proxy PROXY         Proxy URL (e.g., socks5://user:pass@proxy:port)

```

Example: `python DEInied.py --file-attachment ~/Desktop/cat.png`
