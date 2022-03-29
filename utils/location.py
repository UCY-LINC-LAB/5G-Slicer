from functools import lru_cache
from typing import Optional

from geopy.geocoders import Nominatim
from ns.mobility import GeographicPositions, ConstantPositionMobilityModel


class Location(object):
    __saved_locations__ = []
    lat: Optional[float]
    lon: Optional[float]
    alt: Optional[float]
    country: Optional[str]
    address: Optional[str]

    class LocationException(Exception): pass

    def __init__(self, lat: Optional[float] = None, lon: Optional[float] = None, alt: Optional[float] = 0.0,
                 country: Optional[str] = None, address: Optional[str] = None,
                 geolocator: Nominatim = Nominatim(user_agent="Fogify-extension"), *args, **kwargs):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.country = country
        self.address = address
        self.__geolocator = geolocator
        self.fill()

    def set_alt(self, alt: float):
        try:
            self.alt = float(alt)
        except ValueError:
            raise Location.LocationException("Altitude should be numeric")

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_alt(self):
        return self.alt if self.alt else 0.0

    def set_lat(self, lat):
        try:
            self.lat = float(lat)
        except ValueError:
            raise Location.LocationException("Latitude should be numeric")

    def set_lon(self, lon):
        try:
            self.lon = float(lon)
        except ValueError:
            raise Location.LocationException("Longitude should be numeric")

    def fill_country(self, force: bool = False):
        if self.country is None or force:
            self.country = str(self.geo_reverse_country(self.lat, self.lon)).upper()

    def fill_coords(self, force: bool = False):
        if (self.lat is not None or self.lon is not None) and not force: return
        if self.country:
            self.geolocate(self.country)
            return
        self.fill_coords_from_address()
        self.fill_country()

    def fill_coords_from_address(self, force: bool = False):
        if (self.lat is not None or self.lon is not None) and not force: return
        self.geolocate(self.address)

    def fill_coords_from_country(self, force=False):
        if (self.lat is not None or self.lon is not None) and not force: return
        self.geolocate(self.country)

    def fill(self):
        coords_exist = self.lat and self.lon
        if coords_exist: return

        if self.country:
            self.fill_coords_from_country()
        elif self.address:
            self.fill_coords()
        else:
            raise Location.LocationException("You did not provide any information about the location")

    @lru_cache(maxsize=None)
    def geo_reverse_country(self, lat: float, lon: float):
        location = self.__geolocator.reverse("%s,%s" % (lat, lon))
        country = location.raw['address']['country_code']
        return country

    @lru_cache(maxsize=None)
    def geolocate(self, place_name: str):
        try:
            loc = self.__geolocator.geocode(place_name)
            self.lat, self.lon = loc.latitude, loc.longitude
        except:
            return None

    def __str__(self):
        return "%r (%s, %s, %s, %s, %s)" % (
        self, self.get_lat(), self.get_lon(), self.get_alt(), self.country, self.address)

    def distance(self, location: "Location") -> float:
        a = ConstantPositionMobilityModel()
        b = ConstantPositionMobilityModel()
        a.SetPosition(self.to_ns3())
        b.SetPosition(location.to_ns3())
        return a.GetDistanceFrom(b) / 1000

    def to_ns3(self):
        return GeographicPositions().GeographicToCartesianCoordinates(self.get_lat(), self.get_lon(), self.get_alt(),
                                                                      GeographicPositions.WGS84)

    def to_dict(self):
        res = dict(lat=self.get_lat(), lon=self.get_lon())  # , altitude=self.altitude
        res['alt'] = self.get_alt()
        if self.country:
            res['country'] = self.country
        if self.address:
            res['address'] = self.address
        return res

    def __eq__(self, other):
        return self.get_lat() == other.get_lat() and self.get_lon() == other.get_lon() and self.get_alt() == other.get_alt()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.to_dict())
