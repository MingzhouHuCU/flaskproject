from flask import Flask, render_template, json, request,redirect,session,jsonify
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'mingzhou'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'etf'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSearchETF')
def showSearchETF():
    return render_template('searchETF.html')

@app.route('/showUserPreference')
def showUserPreference():
    return render_template('userPreference.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/getETFInfo')
def getETFInfo():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetETFByUser',(_user,))
            etfs = cursor.fetchall()

            _etf_symbol = etfs[-1]
            cursor.callproc('sp_GetETFInfo',(_etf_symbol[1],))
            etfInfo = cursor.fetchall()

            etfs_dict = []
            for etf in etfInfo:
                etf_dict = {
                    'Description': etf[1]}
                etfs_dict.append(etf_dict)

            return json.dumps(etfs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/getETFSector')
def getETFSector():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetETFByUser',(_user,))
            etfs = cursor.fetchall()

            _etf_symbol = etfs[-1]
            cursor.callproc('sp_GetETFSector',(_etf_symbol[1],))
            etfSector = cursor.fetchall()
    

            etfs_dict = []
            for etf in etfSector:
                etf_dict = {
                        'Sector': etf[1],
                        'Weight': etf[2]}
                etfs_dict.append(etf_dict)

            return json.dumps(etfs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/getETFHolding')
def getETFHolding():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetETFByUser',(_user,))
            etfs = cursor.fetchall()

            _etf_symbol = etfs[-1]
            cursor.callproc('sp_GetETFHolding',(_etf_symbol[1],))
            etfHoldings = cursor.fetchall()
    

            etfs_dict = []
            for etf in etfHoldings:
                etf_dict = {
                        'Name': etf[1],
                        'Weight': etf[2]}
                etfs_dict.append(etf_dict)

            return json.dumps(etfs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/getETF')
def getETF():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetETFByUser',(_user,))
            etfs = cursor.fetchall()

            etfs_dict = []
            for etf in etfs:
                etf_dict = {
                        'Id': etf[0],
                        'Symbol': etf[1],
                        'Date': etf[3]}
                etfs_dict.append(etf_dict)

            return json.dumps(etfs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/searchETF',methods=['POST'])
def searchETF():
    try:
        if session.get('user'):
            _etfsymbol = request.form['inputSymbol']
            _user = session.get('user')


            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_checkETF',(_etfsymbol,))
            check = cursor.fetchall()

            if len(check) is 0:

                _holding,_sector = _scrapper(_etfsymbol)

                _holding = json.loads(_holding)
                for _key in _holding['Name']:
                    _name_h=_holding['Name'][_key]
                    _weight_h=_holding['Weight'][_key]
                    cursor.callproc('sp_addETFHolding',(_etfsymbol,_name_h,_weight_h))
                
                _sector = json.loads(_sector)
                for _key in _sector['Sector']:
                    _sector_s=_sector['Sector'][_key]
                    _weight_s=_sector['Weight'][_key]
                    cursor.callproc('sp_addETFSector',(_etfsymbol,_sector_s,_weight_s))
                

            cursor.callproc('sp_searchETF',(_etfsymbol,_user))
            data = cursor.fetchall()
            
            
            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/userPreference',methods=['POST'])
def userPreference():
    try:
        if session.get('user'):
            _sector = request.form['inputSector']
            _term = request.form['inputTerm']
            print(_sector)
            print(_term)

            stockSymbol = 'AAPL'
            # Do stock stock pick
            # scarp for stock data
            # generate graph
            # generate world cloud
            # generate sentimental analysis
            # (maybe) network analysis
            stock_img = 'static/charts/aapl-stock.jpg'
            currentPrice = 134.34

            wordCloud = 'static/charts/word-cloud-big-data-4.jpg'
            
            
            positiveSent = "1.34%"
            negativeSent = "0.91%"
            posToNeg = 1.48
            return render_template('stockResult.html',chart_src_stock="/"+stock_img,chart_src_wordCloud="/"+wordCloud,stock_symbol = stockSymbol,\
                                    current_price = currentPrice,positive_sent=positiveSent,negative_sent=negativeSent,pos_neg=posToNeg)

    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        

        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        


        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


def _scrapper(ticker):
    import requests as rs
    from lxml import html
    from lxml import etree
    url = "https://uat-www.spdrs.com/product/fund.seam?ticker=%s" % (ticker)
    response = rs.get(url)
    if response.status_code == 200:
        import bs4
        soup = bs4.BeautifulSoup(response.content, 'html.parser')


        holding = soup.find('div',id="FUND_TOP_TEN_HOLDINGS")
        table_body = holding.find('tbody')
        rows = table_body.find_all('tr')
        data = []

        for row in rows:
            cols = [ele.strip() for ele in row.text.split('\n')]
            data.append([ele for ele in cols if ele])
        
        
        sector = soup.find('div',id="SectorsAllocChart")
        s = sector.find('div',style="display: none")
        se = list(s)[0].encode()
        print(se)
        root = etree.XML(se)
        print(root)
        data_s = []
        for element in root.iter('attribute'):
            data_s.append([element.find('label').text,element.find('value').text])
 

        import pandas as pd

        df = pd.DataFrame(data[1:],columns = data[0])
        df['Weight'] = df['Weight'].replace('%','',regex=True).astype('float')/100
        df['Shares Held']=df['Shares Held'].replace(',','',regex=True).astype('int')
        df.index = df.index+1
        holding_j = df.to_json()


        df_s = pd.DataFrame(data_s)
        df_s.columns=['Sector','Weight']
        df_s['Weight'] = df_s['Weight'].replace('%','',regex=True).astype('float')/100
        df_s.index=df_s.index+1
        sector_j = df_s.to_json()


        return holding_j, sector_j
        

if __name__ == "__main__":
    app.run(port=5002)
