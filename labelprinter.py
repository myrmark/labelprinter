#Author Filip Malmberg

import keyring
import os
import pymysql
import subprocess

from datetime import datetime
from time import sleep

dbpw = keyring.get_password("172.28.88.47", "simdbuploader")
printer='ME340_lager'
user = os.getlogin()


try:
    os.listdir(f"/home/{user}/labelfiles")
except Exception:
    print("labelfiles folder was not found. Creating folder")
    os.mkdir(f"/home/{user}/labelfiles")


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
        serials = []
        if serialcheck == 'True':
            while True:
                serial = input('Enter your serial(s). Press return without input when finished: ')
                if serial == "":
                    break
                serials.append(serial)
        else:
            serials.append(itemnumber)
        amount = input("Enter amount of copies to print: ")
        commands = []
        for serial in serials:
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
                    f"-o  /home/{user}/{serial}.pdf".split("  ")
            commands.append(f"-c /home/{user}/labelfiles/{serial}.pdf")
            subprocess.call(cmd)
        files_strings = " ".join(commands)
        cmd = f"lp -n {amount} {files_strings} -d {printer}".split()
        #printcmd = f"lp -n {amount} /home/{user}/{serial}.pdf -d {printermachine}".split()
        #sleep(.1)
        subprocess.call(printcmd)