import json
import requests
import pprint
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import configparser

# For Reference:
# Coin IDs found from https://api.coinmarketcap.com/v2/listings/
#         Bitcoin ID = 1
#         Litecoin ID = 2
#         Stellar Lumens ID = 512
#         Ripple ID = 52
#         Tron ID = 1958
#
class KryptoBot:
    def __init__(self,config_filepath, coin_config_filepath):
        self.config = configparser.ConfigParser()
        self.config.read(config_filepath)
        self.config_filepath = config_filepath

        self.coin_config = configparser.ConfigParser()
        self.coin_config.read(coin_config_filepath)
        self.coin_config_filepath = coin_config_filepath

        self.sumHodl = self.variance = 0.0
        self.date = datetime.datetime.now().strftime("%m/%d/%y")
        self.portfolio_arr = [self.date]
        self.api_url = 'https://api.coinmarketcap.com/v2/ticker/'

    def get_krypto_data(self):
        sections = self.coin_config.sections()
        filepath = self.coin_config_filepath
        for section in sections:
            r = requests.get(self.api_url + self.coin_config.get(section,'id'), verify=False).json()

            self.coin_config[section]['price'] = '{0:.3f}'.format(r['data']['quotes']['USD']['price'])
            self.coin_config[section]['percent_change_24h'] = '{0:.3f}'.format(r['data']['quotes']['USD']['percent_change_24h'])
            self.coin_config[section]['holding_sum'] = '{0:.3f}'.format(float(self.coin_config.get(section,'price')) * float(self.coin_config.get(section,'amount')))
            self.portfolio_arr.append(self.coin_config.get(section,'price'))
            self.portfolio_arr.append(self.coin_config.get(section,'holding_sum'))
            self.portfolio_arr.append(self.coin_config.get(section,'percent_change_24h'))

            self.sumHodl += eval(self.coin_config.get(section, 'holding_sum'))
            with open(filepath, 'w') as changes:
                self.coin_config.write(changes)

        self.sumHodl = '{0:.3f}'.format(self.sumHodl)
        self.portfolio_arr.append(self.sumHodl)
        self.variance = '{0:.3f}'.format(float(self.sumHodl) - float(self.config.get('Summary', 'Total_Invested')))
        self.portfolio_arr.append(self.variance)

    def test_get_krypto_data(self):
        print("Getting coin config sections...")
        sections = self.coin_config.sections()
        print("Setting config filepath...")
        filepath = self.coin_config_filepath
        print("Begin get_krypto_data...")
        for section in sections:
            r = requests.get(self.api_url + self.coin_config.get(section,'id'), verify=False).json()
            print("Request: ", r)
            print("Setting config values...")
            self.coin_config[section]['price'] = '{0:.3f}'.format(r['data']['quotes']['USD']['price'])
            self.coin_config[section]['percent_change_24h'] = '{0:.3f}'.format(r['data']['quotes']['USD']['percent_change_24h'])
            self.coin_config[section]['holding_sum'] = '{0:.3f}'.format(float(self.coin_config.get(section,'price')) * float(self.coin_config.get(section,'amount')))
            print("Appending to array...")
            self.portfolio_arr.append(self.coin_config.get(section,'price'))
            self.portfolio_arr.append(self.coin_config.get(section,'holding_sum'))
            self.portfolio_arr.append(self.coin_config.get(section,'percent_change_24h'))
            print(self.portfolio_arr)
            print("Calculating sum:")
            self.sumHodl += float(self.coin_config.get(section, 'holding_sum'))
            print(self.sumHodl)
            print("Saving config changes...")
            with open(filepath, 'w') as changes:
                self.coin_config.write(changes)
            print("Save complete...")

        self.sumHodl = '{0:.3f}'.format(self.sumHodl)
        print("End get_krypto_data...")
        self.portfolio_arr.append(self.sumHodl)
        print("Final sum: ", self.sumHodl)
        self.variance = '{0:.3f}'.format(float(self.sumHodl) - float(self.config.get('Summary', 'Total_Invested')))
        print("Variance: ", self.variance)
        self.portfolio_arr.append(self.variance)
        print("Final array: ", self.portfolio_arr)

        
    def InsertToGoogleSheet(self):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('kryptobot_info.json',scope)
        client = gspread.authorize(creds)
        
        sheet = client.open('Crypto Portfolio History').sheet1
        
        row = self.portfolio_arr
        sheet.append_row(row)
    
    def test_dynamic_email(self):
        from_addr = self.config.get('Email', 'FromAddress')
        to_addr = self.config.get('Email', 'ToAddress')
        password = self.config.get('Email','Password')
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = "TEST - Crypto Portfolio Report - " + self.date

        self.coin_config.read(self.coin_config_filepath)
        sections = self.coin_config.sections()
    
        body = """\
        <html>
            <head>
            <style>
                table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                }
        
                td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
        
                tr:nth-child(even) {
                    background-color: #dddddd;
                }
            </style>
            </head>
            <body>
            
            <h2>Test Daily Report:</h2>
            
            <table>
              <tr>
                <th>Coin/Token</th>
                <th>Current Price</th>
                <th>Current Holding Value</th>
                <th>24H Variance</th>
              </tr>
			  """
        for section in sections:
            body = body + "<tr>"
            body = body + "<td>" + section + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'price') + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'holding_sum') + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'percent_change_24h') + "</td>"
            body = body + "</tr>"
        body = body + """\
            </table>
            <br><br>
            <table>
                <tr>
                    <th>Net Worth</th>
                    <th>Invested</th>
                    <th>Variance</th>
                </tr>
                <tr>
                    <td>{sumhodl}</td>
                    <td>{investment}</td>
                    <td>{variance}</td>
                </tr>
            </table>
            <br><br>
            </body>
            </html>
        """.format(sumhodl = self.sumHodl,
                  investment= self.config.get('Summary', 'Total_Invested'),
                  variance = self.variance)
        
        msg.attach(MIMEText(body, 'html'))
         
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, password)
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)
        server.quit()

    def send_email(self):
        from_addr = self.config.get('Email', 'FromAddress')
        to_addr = self.config.get('Email', 'ToAddress')
        password = self.config.get('Email','Password')
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = "Crypto Portfolio Report - " + self.date

        self.coin_config.read(self.coin_config_filepath)
        sections = self.coin_config.sections()
    
        body = """\
        <html>
            <head>
            <style>
                table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                }
        
                td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
        
                tr:nth-child(even) {
                    background-color: #dddddd;
                }
            </style>
            </head>
            <body>
            
            <h2>Daily Report:</h2>
            
            <table>
              <tr>
                <th>Coin/Token</th>
                <th>Current Price</th>
                <th>Current Holding Value</th>
                <th>24H Variance</th>
              </tr>
			  """
        for section in sections:
            body = body + "<tr>"
            body = body + "<td>" + section + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'price') + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'holding_sum') + "</td>"
            body = body + "<td>" + self.coin_config.get(section, 'percent_change_24h') + "</td>"
            body = body + "</tr>"
        body = body + """\
            </table>
            <br><br>
            <table>
                <tr>
                    <th>Net Worth</th>
                    <th>Invested</th>
                    <th>Variance</th>
                </tr>
                <tr>
                    <td>{sumhodl}</td>
                    <td>{investment}</td>
                    <td>{variance}</td>
                </tr>
            </table>
            <br><br>
            </body>
            </html>
        """.format(sumhodl = self.sumHodl,
                  investment= self.config.get('Summary', 'Total_Invested'),
                  variance = self.variance)
        
        msg.attach(MIMEText(body, 'html'))
         
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, password)
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)
        server.quit()
        
#if __name__ == "__main__":
#    _Init_Krypto_Bot()
bot = KryptoBot(r"C:\Users\Kollin\Documents\Development\PythonDev\Config.ini", r"C:\Users\Kollin\Documents\Development\PythonDev\coin_config.ini")