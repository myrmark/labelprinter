#Author Filip Malmberg

import keyring
import os
import pymysql
import subprocess
import time

from datetime import datetime


dbpw = keyring.get_password("172.28.88.47", "simdbuploader")
printermachine='ME340_lager'
user = os.getlogin()


def sqlquery(column,itemnumber):
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    cursor.execute(f"SELECT {column} FROM simdb.standardprojectglabels WHERE pn='{itemnumber}'")
    try:
        result = cursor.fetchone()[0]
    except Exception:
        result = False
    return(result)
    db.close()


def getitemnumber():
    while True:
        itemnumber = input('Please enter your item number: ')
        if itemnumber[0]=='6' and len(itemnumber)==6 and itemnumber.isnumeric() or len(itemnumber)==9 and '-' in itemnumber and itemnumber[0]=='6':
            dbitemnumber = sqlquery('pn',itemnumber)
            if dbitemnumber is not False:
                return(itemnumber)
                break
            else:
                print('Label does not exist in database.')
        else:
            print('Please enter a valid item number.\n')


if __name__ == '__main__':
    while True:
        itemnumber = getitemnumber()
        labeloption = sqlquery('labeloption',itemnumber)
        description1 = sqlquery('description1',itemnumber)
        description2 = sqlquery('description2',itemnumber)
        description3 = sqlquery('description3',itemnumber)
        description4 = sqlquery('description4',itemnumber)
        description5 = sqlquery('description5',itemnumber)
        revision = sqlquery('revision',itemnumber)
        customer_pn = sqlquery('customer_pn',itemnumber)
        todays_date = datetime.today().strftime('%Y-%m-%d')
        serialcheck = sqlquery('serial',itemnumber)
        if serialcheck == 'True':
            serial = input('Enter your serial: ')
        else:
            serial = None
        amount = input("Enter amount of labels to print: ")
        cmd = "glabels-batch-qt  "\
                f"/mnt/fs/Icomera/Line/SupplyChain/Production/Glabels/Templates/{labeloption}.glabels  "\
                f"-D  description1={description1}  "\
                f"-D  description2={description2}  "\
                f"-D  description3={description3}  "\
                f"-D  description4={description4}  "\
                f"-D  description5={description5}  "\
                f"-D  serial={serial}  "\
                f"-D  pn={itemnumber}  "\
                f"-D  todays_date={todays_date}  "\
                f"-D  customer_pn={customer_pn}  "\
                f"-D  revision={revision}  "\
                f"-o  /home/{user}/{itemnumber}.pdf".split("  ")
        subprocess.call(cmd)
        printcmd = f"lp -n {amount} /home/{user}/{itemnumber}.pdf -d {printermachine}".split()
        subprocess.call(printcmd)
    done
