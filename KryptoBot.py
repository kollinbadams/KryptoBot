import json
import requests
from pprint import pprint
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



def get_crypto_data():
    #Summation variable Initialization, and Individual holding value variable initialization
    sumHodl=holdingValue= 0.0
    
    #Hardcode Coin IDs found from https://api.coinmarketcap.com/v2/listings/
    btcID = 1
    ltcID = 2
    xlmID = 512
    xrpID = 52
    trxID = 1958
    
    #Hardcode coin holding amounts
    btcHodl =.01
    ltcHodl =4.00
    xlmHodl =400.00
    xrphodl =1080.00
    trxhodl =9626.00
    
    #Initialize Dictionary with the Ids for each Crypto, paired with each holding amount
    #Could be handled dynamically in the future if need be
    portfolio = {
            btcID:btcHodl,
            ltcID:ltcHodl,
            xlmID:xlmHodl,
            xrpID:xrphodl,
            trxID:trxhodl
        }

    #initialize data array with current date
    cryptoData = [datetime.datetime.now().strftime("%m/%d/%y")]

    for coin, amount in portfolio.items():
        #Fetch JSON data from coinmarket cap api, passing in what coin data to fetch
        r = requests.get('https://api.coinmarketcap.com/v2/ticker/'+str(coin), verify=False).json()
        #initialize price, holdingValue, percentchange variables for readability
        price = '{0:,.3f}'.format(r['data']['quotes']['USD']['price'])
        holdingValue = '{0:,.3f}'.format(r['data']['quotes']['USD']['price'] *amount)
        percentChange24hour = r['data']['quotes']['USD']['percent_change_24h']
        #Append items to array
        cryptoData.append(price)
        cryptoData.append(holdingValue)
        cryptoData.append(percentChange24hour)
        #Calculates sum of individual holdings
        sumHodl += float(holdingValue)
    #append sum to array
    cryptoData.append(sumHodl)
    #Insert to Google Sheet Call
    InsertToGoogleSheet(cryptoData)
    #Send Email Call
    SendEmail(cryptoData)

def test_get_crypto_data():
    #Summation variable Initialization, and Individual holding value variable initialization
    sumHodl=hodlVal= 0
    
    #Hardcode Coin IDs found from https://api.coinmarketcap.com/v2/listings/
    btcID = 1
    ltcID = 2
    xlmID = 512
    xrpID = 52
    trxID = 1958
    
    #Hardcode coin holding amounts
    btcHodl =.01
    ltcHodl =4.00
    xlmHodl =400.00
    xrphodl =1080.00
    trxhodl =9626.00
    
    #Initialize Dictionary with the Ids for each Crypto, paired with each holding amount
    #Could be handled dynamically in the future if need be
    portfolio = {
            btcID:btcHodl,
            ltcID:ltcHodl,
            xlmID:xlmHodl,
            xrpID:xrphodl,
            trxID:trxhodl
        }

    cryptoData = [datetime.datetime.now().strftime("%m/%d/%y")]
    
    
    #for id in range(len(coins)):
    for coin, amount in portfolio.items():
        #Fetch JSON data from coinmarket cap api, passing in what coin data to fetch
        r = requests.get('https://api.coinmarketcap.com/v2/ticker/'+str(coin), verify=False).json()
        price = r['data']['quotes']['USD']['price']
        holdingValue = r['data']['quotes']['USD']['price'] *amount
        percentChange24hour = r['data']['quotes']['USD']['percent_change_24h']
        cryptoData.append(price)
        cryptoData.append(holdingValue)
        cryptoData.append(percentChange24hour)
        #Prints current price of specified coin
        print("Current Price(USD) of " + r['data']['name'] + ": " + '{0:,.2f}'.format(r['data']['quotes']['USD']['price']))
        #Calculates individual holding value from corresponding coin/token
        hodlVal = r['data']['quotes']['USD']['price'] * amount
        #Prints current value of individual holding
        print("Current Value of " + r['data']['symbol']+ " Holdings: " + '{0:,.2f}'.format(hodlVal))
        #Calculates sum of individual holdings
        sumHodl += hodlVal
    #Prints total value of portfolio
    cryptoData.append('{0:,.3f}'.format(sumHodl))
    print("Gross Value of Holdings: $ "+ '{0:,.2f}'.format(sumHodl))
    print(cryptoData)

def InsertToGoogleSheet(data):
    scope =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('kryptobot_info.json',scope)
    client = gspread.authorize(creds)
    
    sheet = client.open('Crypto Portfolio History').sheet1
    
    row = data
    sheet.append_row(row)
    print("Operation - InsertToGoogleSheet(data) complete...")

def SendEmail(data):
    fromaddr = "FROMADDR"#Place from email address when ready to run
    toaddr = "TOADDR"#place to email address when ready to run
    currentDate = datetime.datetime.now().strftime("%m/%d/%y")
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Crypto Portfolio Report - " + currentDate
    
    xlmPrice        = data[1]
    xlmHoldValue    = data[2]
    xlm24hour       = data[3]
    btcPrice        = data[4]
    btcHoldValue    = data[5]
    btc24hour       = data[6]
    ltcPrice        = data[7]
    ltcHoldValue    = data[8]
    ltc24hour       = data[9]
    xrpPrice        = data[10]
    xrpHoldValue    = data[11]
    xrp24hour       = data[12]
    trxPrice        = data[13]
    trxHoldValue    = data[14]
    trx24hour       = data[15]
    holdingNetWorth = data[16]
    Invested        = 3965.130
    Variance        = data[16] - Invested


    body = """\
    <html>
        <head>
        <style>
            table {{
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }}
    
            td, th {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
    
            tr:nth-child(even) {{
                background-color: #dddddd;
            }}
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
          <tr>
            <td>Bitcoin(BTC)</td>
            <td>{btcPrice}</td>
            <td>{btcHoldValue}</td>
            <td>{btc24hour}</td>
          </tr>
          <tr>
            <td>LiteCoin(LTC)</td>
            <td>{ltcPrice}</td>
            <td>{ltcHoldValue}</td>
            <td>{ltc24hour}</td>
          </tr>
          <tr>
            <td>Stellar Lumens(XLM)</td>
            <td>{xlmPrice}</td>
            <td>{xlmHoldValue}</td>
            <td>{xlm24hour}</td>
          </tr>
          <tr>
            <td>Ripple(XRP)</td>
            <td>{xrpPrice}</td>
            <td>{xrpHoldValue}</td>
            <td>{xrp24hour}</td>
          </tr>
          <tr>
            <td>Tron(TRX)</td>
            <td>{trxPrice}</td>
            <td>{trxHoldValue}</td>
            <td>{trx24hour}</td>
          </tr>
        </table>
        <br><br>
        <table>
            <tr>
                <th>Net Worth</th>
                <th>Invested</th>
                <th>Variance</th>
            </tr>
            <tr>
                <td>{holdingNetWorth}</td>
                <td>{Invested}</td>
                <td>{Variance}</td>
            </tr>
        </table>
        <br><br>
        <h2>Today's Popular Headlines:</h2>
        <br>
        </body>
        </html>
    """.format(**locals())
    
    msg.attach(MIMEText(body, 'html'))
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "PASSWORD")#Place from email password when ready to run
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == "__main__":
    get_crypto_data()
