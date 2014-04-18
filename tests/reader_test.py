from unittest import TestCase
from citibike.reader import remove_station_details 

class ReaderNoDetailsTest(TestCase):
    """Tests to confirm the reader correctly removes station details."""

    ORIGINAL = {'birth year': '1989', 'end station longitude': '-73.9912551', 'bikeid': '19365', 'start station id': '173', 'start station longitude': '-73.98442659', 'end station latitude': '40.76019252', 'end station name': '9 Ave & W 45 St', 'start station latitude': '40.76064679', 'end station id': '479', 'usertype': 'Subscriber', 'stoptime': '2013-07-01 00:15:16', 'starttime': '2013-07-01 00:02:23', 'gender': '1', 'tripduration': '773', 'start station name': 'Broadway & W 49 St'}

    EXPECTED = {'birth year': '1989', 'bikeid': '19365', 'start station id': '173',  'end station id': '479', 'usertype': 'Subscriber', 'stoptime': '2013-07-01 00:15:16', 'starttime': '2013-07-01 00:02:23', 'gender': '1', 'tripduration': '773'}

    def test(self):
        self.assertEquals(remove_station_details(self.ORIGINAL),
                          self.EXPECTED)

        
