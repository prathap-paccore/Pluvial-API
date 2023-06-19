import requests
from datetime import datetime
from api.library.commonFunctions import *
from django.conf import settings

def calcEvaportation(data):
    tmax = data['tmax']
    tmin = data['tmin']
    rh = data['rh']
    day = data['day']
    latitude = data ['latitude'] #l
    altitude = data['altitude'] #z
    uv = data['uv']
    albedo = data['albedo']
    uz = data['uz']
    cd = data['cd']
    cn = data['cn']
    kc= data['kc']
    precipitationSummary= data['precipitationSummary']

    tmean = calTmean(tmax, tmin) #Tmean calculation

    A = tmean + 237.3
    P = atm_pressure(altitude)
    gamma = calcGamma(P) #ghama

    B = tmax + 273.16
    C = tmin + 273.16
    delta = delta_svp(tmean, A) #b50

    VPm = calVPM(tmax, tmin)
    VDa = calVDa(rh, VPm) #Acutal Vapor Pressure  formula is diff is diff than excel  B44 (multiply * but it has +)********

    dr = inv_rel_dist_earth_sun(day) #dr, Inverse realtive Earth-Sun Distance (In excel the formaula is 0.33 but in pdf 0.033)****

    solarDec = sol_dec(day) #δ, solar declination

    latRad = lat_rad(latitude) # φ, Latitude Radians

    sunset_hour_angle_ws = sunset_hour_angle(latRad, solarDec)  #ws

    rs = calRS(uv) 

    #rs = data['rs'] * 0.0864  #(uv * 40* )
    Rns = net_solor(rs, albedo)  #Rns excel value is shoud be 166.32 but it has 166 , but here 166.32


    Ra = calcRa(dr, solarDec, latRad, sunset_hour_angle_ws)

    Rso = calRso(altitude, Ra)

    Rnl = calRnl(B, C, cd, rs, Rso, VDa)

    Rn = Rns - Rnl

    DT = calcDT (delta, gamma, cd, uz)

    Rng = 0.408 * Rn

    PT = calcPT(gamma, delta, uz, cd)

    TT = calcTT(cn, tmean, uz)
    
    Etrad = DT * Rng

    ETwind = PT * TT * (VPm - VDa)

    ETo = Etrad + ETwind  #units mm/day

    EToPerDay = ETo/25.4 #units inch/day

    ETc = kc * ETo  #units mm/day
    waterDeficiency = ETc - precipitationSummary
    results = {
        "Tmean": tmean,
        "Gamma": gamma,
        "Delta": delta,
        "altitude": altitude,
        "Acutal Vapor Pressure - VDa": VDa,
        "dr": dr,
        "δ": solarDec,
        "φ": latRad,
        "Sunset hour angle - ws": sunset_hour_angle_ws,
        "Incoming Solar Radiation - rs": rs,
        "Net solar or shortwave radiation - Rns": Rns,
        "Extraterrestial Radiation - Ra": Ra,
        "Clear Sky Solar Radiation - Rso": Rso,
        "Net Outgoing Longwave Radiation - Rnl": Rnl,
        "Net radiation - Rn": Rn,
        "Delta terms - DT": DT,
        "Net Radiation in equivalent of Evaporation - Rng": Rng,
        "Psi Term - PT": PT,
        "Temperature Term - TT": TT,
        "Etrad": Etrad,
        "ETwind": ETwind,
        "ETo": ETo,
        "ETo Per Day": EToPerDay,
        "ETc": ETc,
        "waterDeficiency": waterDeficiency
    }
    return results


def callWeatherAPI(long, lat, elevation):
    
    # Any process that you want
    weatherApiurl= settings.WEATHER_API+"&query="+str(lat)+","+str(long)+"&subscription-key="+settings.WEATHER_SUNSCRIPTION_KEY 
    response = requests.get(weatherApiurl)
    data = response.json()
    weatherInfoResponse = data['results'][0]
    #print(weatherInfoResponse, "weatherInfoResponse")
    #geather weather API INfo

    
    weatherInfoDict = {
        "tmax" : float(weatherInfoResponse['temperatureSummary']['past24Hours']['maximum']['value']),
        "tmin" : float(weatherInfoResponse['temperatureSummary']['past24Hours']['minimum']['value']),
        "rh" : float(weatherInfoResponse['relativeHumidity']),
        "day" : float(datetime.strptime(weatherInfoResponse['dateTime'], '%Y-%m-%dT%H:%M:%S%z').timetuple().tm_yday),
        "latitude" : float(lat), #l
        "altitude" : float(elevation), #z
        "uv" : float(weatherInfoResponse['uvIndex']),
        "uz" : float(weatherInfoResponse['wind']['speed']['value'] * (1000/3600)),  
        "albedo" : float(0.23),
        "cd" : float(0.28),
        "cn" : float(1600),
        "kc" : float(0.40),
        "precipitationSummary": float(weatherInfoResponse['precipitationSummary']['past24Hours']['value'])
    }
    #print(weatherInfoDict, 'weatherInfoDict')
    #results = calcEvaportation(weatherInfoDict)
    print(weatherInfoResponse['dateTime'])
    import pytz
    dt = datetime.fromisoformat(weatherInfoResponse['dateTime'])
    dt_utc = dt.astimezone(datetime.now().astimezone().tzinfo)
    print(dt_utc)
    #print(datetime.strptime(weatherInfoResponse['dateTime'], "%Y-%m-%dT%H:%M:%S%z"))
    weatherResults = {
    'weatherInfoRequest': {'long':long, 'lat':lat, 'elevation':elevation},
    'weatherInfoResponse': weatherInfoResponse, 
    #'weatherResults': results,
    "tmax" : float(weatherInfoResponse['temperatureSummary']['past24Hours']['maximum']['value']),
    "tmin" : float(weatherInfoResponse['temperatureSummary']['past24Hours']['minimum']['value']),
    "rh" : float(weatherInfoResponse['relativeHumidity']),
    "day" : float(datetime.strptime(weatherInfoResponse['dateTime'], '%Y-%m-%dT%H:%M:%S%z').timetuple().tm_yday),
    "latitude" : float(lat), #l
    "altitude" : float(elevation), #z
    "uv" : float(weatherInfoResponse['uvIndex']),
    "uz" : float(weatherInfoResponse['wind']['speed']['value'] * (1000/3600)),
    "precipitationSummary": float(weatherInfoResponse['precipitationSummary']['past24Hours']['value']),
    'weatherDate':  datetime.strptime(weatherInfoResponse['dateTime'], '%Y-%m-%dT%H:%M:%S%z'),
    'extraInfo': {"albedo" : float(0.23),"cd" : float(0.28), "cn" : float(1600),"kc" : float(0.40)}
     }
    #print(weatherResults,"weatherResults")

    return weatherResults
 