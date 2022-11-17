#Author Filip Malmberg

import keyring
import lzma
import os
import pymysql
import subprocess
import tarfile

from datetime import datetime
from pick import pick
from time import sleep

dbpw = keyring.get_password("172.28.88.47", "simdbuploader")
user = os.getlogin()


try:
    os.listdir(f"/home/{user}/labelfiles")
except Exception:
    print("labelfiles folder was not found. Creating folder")
    os.mkdir(f"/home/{user}/labelfiles")


try:
    ps = subprocess.Popen('sudo lpinfo -m', stdout=subprocess.PIPE, shell=True)
    drivers_check = subprocess.check_output(('grep', 'TTP-644MT'), stdin=ps.stdout)
    ps.wait()
    drivers_check = drivers_check.decode().strip()
except Exception:
    print(f"Printer drivers not installed. Installing..")
    with lzma.open('drivers.tar.xz') as fd:
        with tarfile.open(fileobj=fd) as tar:
            content = tar.extractall('drivers')
    os.chdir('drivers')
    cmd = 'sudo ./install-driver'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('sudo lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'TTP-644MT'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer TTP-644MT not installed. Installing..")
    cmd = 'sudo lpadmin -p TTP-644MT -E -m tscbarcode/TTP-644MT.ppd -v lpd://172.28.88.43/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('sudo lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'ME340_lager'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer ME340_lager not installed. Installing..")
    cmd = 'sudo lpadmin -p ME340_lager -E -m tscbarcode/ME340.ppd -v lpd://172.28.88.46/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('sudo lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'ME340_production'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer ME340_production not installed. Installing..")
    cmd = 'sudo lpadmin -p ME340_production -E -m tscbarcode/ME340.ppd -v lpd://172.28.88.60/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('sudo lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'Zebra_ZT230_production'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer Zebra_ZT230_production not installed. Installing..")
    cmd = 'sudo lpadmin -p Zebra_ZT230_production -E -m drv:///sample.drv/zebra.ppd -v socket://172.28.88.44:9100 -o PageSize=Custom.101x152mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('sudo lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'Zebra_ZT230_lager'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer Zebra_ZT230_lager not installed. Installing..")
    cmd = 'sudo lpadmin -p Zebra_ZT230_lager -E -m drv:///sample.drv/zebra.ppd -v socket://172.28.88.45:9100 -o PageSize=Custom.101x152mm'.split()
    subprocess.run(cmd)


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


title = 'Select printer: '
options = ['TTP-644MT', 'ME340_production', 'Zebra_ZT230_production', 'ME340_lager', 'Zebra_ZT230_lager']
printer, index = pick(options, title)


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
        mmyyyy = datetime.today().strftime('%m-%Y')
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
                    f"/mnt/fs/Icomera/Line/Supply Chain/Production/Glabels/Templates/{labeloption}.glabels  "\
                    f"-D  description1={description1}  "\
                    f"-D  description2={description2}  "\
                    f"-D  description3={description3}  "\
                    f"-D  description4={description4}  "\
                    f"-D  description5={description5}  "\
                    f"-D  serial={serial}  "\
                    f"-D  pn={itemnumber}  "\
                    f"-D  todays_date={todays_date}  "\
                    f"-D  mmyyyy={mmyyyy}  "\
                    f"-D  customer_pn={customer_pn}  "\
                    f"-D  revision={revision}  "\
                    f"-o  /home/{user}/labelfiles/{serial}.pdf".split("  ")
            commands.append(f"-c /home/{user}/labelfiles/{serial}.pdf")
            subprocess.call(cmd)
        files_strings = " ".join(commands)
        cmd = f"lp -n {amount} {files_strings} -d {printer}".split()
        subprocess.call(cmd)
