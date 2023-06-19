import math
from pyproj import CRS, Transformer
import urllib
import requests
from django.conf import settings


# date_timestamp = datetime.strptime('2022-12-13T17:04:00-08:00', '%Y-%m-%dT%H:%M:%S%z').timetuple().tm_yday
def calTmean(tmax, tmin):
    return (tmax + tmin) / 2.0


def atm_pressure(altitude):
    tmp = (293.0 - (0.0065 * altitude)) / 293.0
    return math.pow(tmp, 5.26) * 101.3


def calcGamma(atmos_pres):
    return 0.000665 * atmos_pres


# =0.000665*(101.3*((293-0.0065*B11)/293)^5.26)


def delta_svp(tmean, a):
    tmp = 4098 * (0.6108 * math.exp((17.27 * tmean) / a))
    return tmp / math.pow(a, 2)


def calVPM(tmax, tmin):
    tmp1 = math.exp((17.27 * tmax) / (tmax + 237.3))
    tmp2 = math.exp((17.27 * tmin) / (tmin + 237.3))
    return 0.6108 * (tmp1 + tmp2) / 2


def calVDa(rh, vpm):
    return (rh / 100) * vpm


def inv_rel_dist_earth_sun(day):
    # _check_doy(day)
    # return 1 + (0.033 * math.cos((2.0 * math.pi / 365.0) * day))
    return 1 + (0.033 * (math.cos(((2 * math.pi / 365) * day))))


def sol_dec(day):
    # _check_doy(day)
    # date_val.strftime('%j')
    tmp = ((2 * math.pi / 365) * day) - 1.39
    return 0.409 * math.sin(tmp)


def lat_rad(latitude):
    return (math.pi / 180) * latitude


def sunset_hour_angle(lat_rad, sol_dec):
    cos_sha = -math.tan(lat_rad) * math.tan(sol_dec)
    return math.acos(cos_sha)


def calRS(uv):
    return uv * 40 * 0.0864


def net_solor(rs, albedo):
    return (1 - albedo) * rs


def calcRa(dr, solarDec, lat_rad, ws):
    tmp = (1440 / math.pi) * 0.0820
    tmp1 = ws * math.sin(lat_rad) * math.sin(solarDec)
    tmp2 = math.cos(lat_rad) * math.cos(solarDec) * math.sin(ws)
    tmp3 = dr * (tmp1 + tmp2)
    return tmp * tmp3
    # print("B19", ws, "B18", solarDec, "B16", lat_rad, "b17" ,dr)
    # return (24*60/math.pi)*0.082*dr*(ws* math.sin(lat_rad)*math.sin(solarDec)+math.cos(lat_rad)*math.cos(solarDec)*math.sin(ws))
    # =(24*60/PI())*0.082*B17*(B19*SIN(B16)*SIN(B18)+COS(B16)*COS(B18)*SIN(B19))
    # B19 = ws, B18= solo, B16= radi, b17 dr


def calRso(altitude, Ra):
    return (0.00002 * altitude + 0.75) * Ra


def calRnl(B, C, cd, rs, rso, avp):
    tmp1 = (math.pow(B, 4) + math.pow(C, 4)) / 2
    tmp2 = cd - (0.14 * math.sqrt(avp))
    tmp3 = 1.35 * (rs / rso) - 0.35
    # print("B51", cd, "B44" , avp, "B67" , rs, "B68" ,rso)
    return 0.000000004903 * tmp1 * tmp2 * tmp3

    # =0.000000004903*(((math.pow(B, 4) + math.pow(C, 4)) / 2))*(B51-0.14*SQRT(B44))*(1.35*B67/B68-0.35)
    # B = tmax + 273.16, C = tmin + 273.16
    # print("B51", cd, "B44" , avp, "B67" , rs, "B68" ,rso)
    # B51 = cd, B44= avp, B67= rs, B68=rso


def calcDT(delta, gamma, cd, uz):
    tmp1 = delta + (gamma * (1 + (cd * uz)))
    return delta / tmp1
    # =B50/(B50+B49*(1+B29*B51))


def calcPT(gamma, delta, uz, cd):
    tmp1 = gamma * (1 + (cd * uz))
    tmp2 = delta + tmp1
    return gamma / tmp2


def calcTT(cn, tmean, uz):
    temp1 = cn / (tmean + 273)
    return temp1 * uz


def coordinatesReproject(coordinates):
    inProj = CRS("EPSG:3857")
    outProj = CRS("EPSG:4326")
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")

    coordinates_reprojected = []
    for coord_list in coordinates:
        xs, ys = zip(*coord_list)
        xs_reproj, ys_reproj = transformer.transform(xs, ys)
        coordinates_reprojected.append(
            [list(pair) for pair in zip(ys_reproj, xs_reproj)]
        )
    return coordinates_reprojected


def getTimeZone(long, lat):
    # https://atlas.microsoft.com/timezone/byCoordinates/json?subscription-key=0tbRYbnJn25-al_7xML3Z2IWi-JnCLfZUx8qM2ZVGZo&api-version=1.0&options=all&query=1.9813681457058598,36.121712177345096
    urlTimeZone = (
        "https://atlas.microsoft.com/timezone/byCoordinates/json?subscription-key="
        + settings.WEATHER_SUNSCRIPTION_KEY
        + "&api-version=1.0options=all&query="
        + str(lat)
        + ","
        + str(long)
        + ""
    )
    # print(urlTimeZone, "mircosoft url")
    result = requests.get(urlTimeZone)
    timezone = result.json()["TimeZones"][0]["Id"]
    # print(elevation, "mircosoft url elevation")
    return timezone


def getElevation(long, lat):
    params = {"output": "json", "x": long, "y": lat, "units": "Meters"}  # lon  # lat

    # https://nationalmap.gov/epqs/pqs.php?output=json&x=36.11878411002355&y=1.982022259851874&units=Meters
    # result = requests.get((r'https://nationalmap.gov/epqs/pqs.php?' + urllib.parse.urlencode(params)))
    # elevation = result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']

    # urlTimeZone = 'https://atlas.microsoft.com/timezone/byCoordinates/json?subscription-key=0tbRYbnJn25-al_7xML3Z2IWi-JnCLfZUx8qM2ZVGZo&api-version=1.0&options=all&query=37.964879918872676,-121.48802316851038'

    # microsoft elevation API.
    # https://atlas.microsoft.com/elevation/point/json?subscription-key=0tbRYbnJn25-al_7xML3Z2IWi-JnCLfZUx8qM2ZVGZo&api-version=1.0&points=-121.48802316851038,37.964879918872676
    # url = (
    #     "https://atlas.microsoft.com/elevation/point/json?subscription-key="
    #     + settings.WEATHER_SUNSCRIPTION_KEY
    #     + "&api-version=1.0&points="
    #     + str(long)
    #     + ","
    #     + str(lat)
    #     + ""
    # )
    # # print(url, "mircosoft url")
    # result = requests.get(url)
    # print(result,'elevation')
    # elevation = result.json()["data"][0]["elevationInMeter"]
    # # print(elevation, "mircosoft url elevation")
    # return elevation

    #bing maps
    #https://dev.virtualearth.net/REST/v1/Elevation/List?points=35.89431,-110.72522&key=Ar429p8x9PqitUBwsO3O16CVf7Nn0Xew2veM-KUNtYLyHluIzjrfHXVJGLnx_i12
    
    url = "https://dev.virtualearth.net/REST/v1/Elevation/List?points="+str(lat)+ ","+str(long)+"&key=Ar429p8x9PqitUBwsO3O16CVf7Nn0Xew2veM-KUNtYLyHluIzjrfHXVJGLnx_i12"
    result = requests.get(url)
    elevation = result.json()["resourceSets"][0]["resources"][0]['elevations'][0]
    return elevation 
    
