import datetime

def date():
  the_date = datetime.datetime.now()
  str_the_date = str(the_date)

  str_current_date_year = str_the_date[0] + str_the_date[1] + str_the_date[2] + str_the_date[3]
  str_current_date_month = str_the_date[5] + str_the_date[6]
  str_current_date_number = str_the_date[8] + str_the_date[9]
  str_current_time = str_the_date[11] + str_the_date[12] + str_the_date[13] + str_the_date[14] + str_the_date[15] + str_the_date[16] + str_the_date[17] + str_the_date[18]

  int_current_date_year = int(str_current_date_year)

  current_date_number = int(str_current_date_number)
  yesterday_date_number = current_date_number - 1

  if yesterday_date_number == 0:
    int_current_data_month = int(str_current_date_month)
    yesterday_date_month = int_current_data_month - 1
    str_yesterday_date_month = str(yesterday_date_month)

    if str_yesterday_date_month != '10' or str_yesterday_date_month != '11' or str_yesterday_date_month != '12':
      str_yesterday_date_month = '0' + str_yesterday_date_month
    else:
      pass

    if((yesterday_date_month==2) and ((int_current_date_year%4==0)  or ((int_current_date_year%100==0) and (int_current_date_year%400==0)))):
      yesterday_str_date_number = '29'
      last_month_day_date = (str_current_date_year, str_yesterday_date_month, yesterday_str_date_number)
      return last_month_day_date
    elif(yesterday_date_month==2):
      yesterday_str_date_number = '28'
      last_month_day_date = (str_current_date_year, str_yesterday_date_month, yesterday_str_date_number)
      return last_month_day_date
    elif(yesterday_date_month==1 or yesterday_date_month==3 or yesterday_date_month==5 or yesterday_date_month==7 or yesterday_date_month==8 or yesterday_date_month==10):
      yesterday_str_date_number = '31'
      last_month_day_date = (str_current_date_year, str_yesterday_date_month, yesterday_str_date_number)
      return last_month_day_date
    elif(yesterday_date_month==0):
      yesterday_str_date_number = '31'
      str_yesterday_date_month = '12'
      str_yesterday_date_year = str(int_current_date_year - 1)
      last_month_day_date = (str_current_date_year, str_yesterday_date_month, yesterday_str_date_number)
      return last_month_day_date
    else:
      yesterday_str_date_number = '30'
      last_month_day_date = (str_current_date_year, str_yesterday_date_month, yesterday_str_date_number)
      return last_month_day_date
  elif yesterday_date_number >=1 and yesterday_date_number <= 9:
    yesterday_str_date_number = '0' + str(yesterday_date_number)
    yesterday_date = (str_current_date_year, str_current_date_month, yesterday_str_date_number)
    return yesterday_date
  else:
    yesterday_str_date_number = str(yesterday_date_number)
    yesterday_date = (str_current_date_year, str_current_date_month, yesterday_str_date_number)
    return yesterday_date

date()