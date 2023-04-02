from datetime import date, timedelta
import math
import pandas as pd
from datetime import timedelta, date
import holidays
import numpy as np

# NOTES
# 2023 will be a 53 week year.
# LULU:  In fiscal years with 53 weeks, the 53rd week of net revenue is excluded from the calculation of sales per square foot.


# json not in use yet
calendar_dictionary = {
    "LULU": {
        "year": {"begins_on": "02-01"},
        "week": {"begins_on": "Saturday"},
        "month": {"format": "4-5-4"},
        "holidays": [],
    },
    "WMT": {
        "year": {"begins_on": "02-01"},
        "week": {"begins_on": "Saturday"},
        "month": {"format": "4-5-4"},
        "holidays": [],
    },
    "TGT": {
        "year": {"begins_on": "02-01"},
        "week": {"begins_on": "Saturday"},
        "month": {"format": "4-5-4"},
        "holidays": [],
    },
    "AMZN": {
        "year": {"begins_on": "01-01"},
        "week": {"begins_on": "Saturday"},
        "month": {"format": "4-5-4"},
        "holidays": [],
    },
}

FOUR_WEEK_MONTHS = []
FIVE_WEEK_MONTHS = []


class CompanyTime:
    """
    A class to handle calendar to fiscal conversions
    """

    def __init__(self, ticker=""):
        self.ticker = ticker

        holiday_list = []
        for holiday in holidays.UnitedStates(years=[2022, 2023, 2024]).items():
            holiday_list.append(holiday)
        self.holidays = pd.DataFrame(
            holiday_list, columns=["holiday_date", "holiday_name"]
        )

    def gregorian_calendar_dataframe(
        self, start_date="01-01-2020", end_date="01-01-2021"
    ):
        """
        function to return gregorian calendar between two American format dd-mm-yyyy dates
        """

        if start_date == "":
            return

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days) + 1):
                yield date1 + timedelta(n)

        data = []
        start_day, start_month, start_year = start_date.split("-")
        end_day, end_month, end_year = end_date.split("-")

        start_dt = date(int(start_year), int(start_month), int(start_day))
        end_dt = date(int(end_year), int(end_month), int(end_day))
        for dt in daterange(start_dt, end_dt):
            data.append(dt.strftime("%Y-%m-%d"))

        return pd.DataFrame(data, columns=["calendar_date"])

    def week_from_date(self, date_object):
        """
        American calendar
        """
        date_ordinal = date_object.toordinal()
        year = date_object.year
        week = ((date_ordinal - self._week1_start_ordinal(year)) // 7) + 1
        if week >= 52:
            if date_ordinal >= self._week1_start_ordinal(year + 1):
                year += 1
                week = 1
        if len(str(week)) == 1:
            week = "0" + str(week)
        return str(year) + str(week)

    def _week1_start_ordinal(self, year):
        jan1 = date(year, 1, 1)
        jan1_ordinal = jan1.toordinal()
        jan1_weekday = jan1.weekday()
        week1_start_ordinal = jan1_ordinal - ((jan1_weekday + 1) % 7)
        return week1_start_ordinal

    def _get_walmart_week(self, d):
        return self.get_walmart_week(d)

    def _get_calendar_week(self, d):
        return self.week_from_date(d)

    def _get_year(self, d):
        return d.strftime("%Y")

    def _get_weekday(self, d):
        return d.strftime("%A")

    def _get_month(self, d):
        return d.strftime("%B")

    def _get_monthday(self, d):
        return d.strftime("%d")

    def get_walmart_week(self, d):
        """
        If no date is passed in, the methods defaults to today.
        """
        fiscal_year_start_date = self.get_fiscal_year_start_date(d)

        # Get the day of WM fiscal year
        day_of_wm_year = (d - fiscal_year_start_date).days + 1

        # Get week number by dividing day number by 7 and rounding up
        wm_week_nbr = math.ceil(day_of_wm_year / 7)
        fiscal_year = fiscal_year_start_date.year

        # Return WM Week as an int
        return (fiscal_year * 100) + wm_week_nbr

    def get_weeks_between_dates_inclusive(self, start_date, end_date):
        """
        Returns tuple of the WM Weeks between the two days passed to the method,
        including the weeks that the dates are in.
        """
        weeks = []
        weeks_start = self.get_previous_saturday(start_date)
        weeks_end = self.get_following_friday(end_date)
        nbr_of_weeks = math.ceil(((weeks_end - weeks_start).days + 1) / 7)

        for i in range(nbr_of_weeks):
            d = start_date + timedelta(weeks=i)
            weeks.append(self.get_walmart_week(d))

        return tuple(weeks)

    def get_following_friday(self, date_obj):
        """
        Returns the Friday immediately following the date passed in.
        If the date passed in is a Friday it should return itself.
        """
        # In Python isoweekday Monday is 1 and Sunday is 7
        weekday = date_obj.isoweekday()
        if weekday > 5:
            distance_from_fri = 7 - abs(5 - weekday)
        else:
            distance_from_fri = abs(5 - weekday)
        return date_obj + timedelta(days=distance_from_fri)

    def get_previous_saturday(self, date_obj):
        """
        Returns the Saturday prior to the date passed in.
        If the date passed in is a Saturday it should return itself.
        """
        # In Python isoweekday Monday is 1 and Sunday is 7
        weekday = date_obj.isoweekday()
        if weekday < 6:
            distance_from_sat = 7 - abs(6 - weekday)
        else:
            distance_from_sat = abs(6 - weekday)
        return date_obj - timedelta(days=distance_from_sat)

    def get_fiscal_year_start_date(self, date_obj):
        """
        Returns the start date of the fiscal year of the date passed in.
        ** Walmarts fiscal year starts with the first WM Week that ends in Feburary
        ** WM Weeks start on Saturday and end on Friday
        """
        # Find the next Friday that follows the given date
        following_friday = self.get_following_friday(date_obj)

        # Determine Walmart fiscal year
        if date_obj.month == 1 & following_friday.month != 2:
            fiscal_year = date_obj.year - 1
        else:
            fiscal_year = date_obj.year

        # Find the first Friday in Feburary of the fiscal year we just found
        feb_1 = date(fiscal_year, 2, 1)
        first_feb_friday = self.get_following_friday(feb_1)

        # Get the first day of the WM Week that ends on the first Friday we just found
        fiscal_year_start_date = first_feb_friday - timedelta(days=6)
        return fiscal_year_start_date

    def _get_walmart_month(self, d):
        walmart_month_index = {
            "01": "February",
            "02": "February",
            "03": "February",
            "04": "February",
            "05": "March",
            "06": "March",
            "07": "March",
            "08": "March",
            "09": "March",
            "10": "April",
            "11": "April",
            "12": "April",
            "13": "April",
            "14": "May",
            "15": "May",
            "16": "May",
            "17": "May",
            "18": "June",
            "19": "June",
            "20": "June",
            "21": "June",
            "22": "June",
            "23": "July",
            "24": "July",
            "25": "July",
            "26": "July",
            "27": "August",
            "28": "August",
            "29": "August",
            "30": "August",
            "31": "September",
            "32": "September",
            "33": "September",
            "34": "September",
            "35": "September",
            "36": "October",
            "37": "October",
            "38": "October",
            "39": "October",
            "40": "November",
            "41": "November",
            "42": "November",
            "43": "November",
            "44": "December",
            "45": "December",
            "46": "December",
            "47": "December",
            "48": "December",
            "49": "January",
            "50": "January",
            "51": "January",
            "52": "January",
            "53": "January",
        }
        walmart_week_number = str(d)[-2:]

        return walmart_month_index[walmart_week_number]

    def calendar_dataframe(self, df=pd.DataFrame(), col="calendar_date", ticker=""):
        """
        return a company calendar modified dataframe
        """
        if ticker == "":  # so, we will want to modify our output based on json input
            pass

        df["year"] = df[col].map(self._get_year)
        df["walmart_week"] = df[col].map(self.get_walmart_week)
        df["calendar_week"] = df[col].map(self._get_calendar_week)
        df["month"] = df[col].map(self._get_month)
        df["calendar_monthday"] = df[col].map(self._get_monthday)
        df["calendar_weekday"] = df[col].map(self._get_weekday)
        df["walmart_month"] = df["walmart_week"].map(self._get_walmart_month)
        df = pd.merge(
            df,
            self.holidays,
            how="left",
            left_on="calendar_date",
            right_on="holiday_date",
        )

        return df
