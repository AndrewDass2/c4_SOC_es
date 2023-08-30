import datetime
import pytz

def day_ztime_info():
  the_date = datetime.datetime.now()
  str_the_date = str(the_date)

  str_current_date_year = str_the_date[0] + str_the_date[1] + str_the_date[2] + str_the_date[3]
  str_current_date_month = str_the_date[5] + str_the_date[6]
  str_current_date_number = str_the_date[8] + str_the_date[9]

  int_current_date_number = int(str_current_date_number)

  zulu_time = datetime.datetime.now(pytz.timezone('Zulu'))
  return str_current_date_year, str_current_date_month, int_current_date_number, zulu_time
  
day_ztime_info()