# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 14:34:32 2022

@author: fluf
"""

import pickle
from os import path
import math

import pandas as pd
import numpy as np
import numpy.matlib
#import xarray as xr
from shapely.geometry import LineString, Polygon

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mplc

from traffic.data import airports
import airtraj.core.conversions as conv

class GaTrajGen:
    
    def __init__(self, airport, runway, glideslope, boundaries):
        """
        """

        self.apt = airports[airport]
        self.rwy = runway
        self.gli = glideslope
        self.bou = boundaries

        rwy_lat = self.apt.runways.data[self.apt.runways.data.name == str(runway)]['latitude'].values[0]
        rwy_lon = self.apt.runways.data[self.apt.runways.data.name == str(runway)]['longitude'].values[0]

        self.rwy_alt = conv.ft2m(self.apt.altitude)
        self.rwy_sgx, self.rwy_sgy, _ = conv.get_ch_coord(rwy_lat, rwy_lon)
        self.rwy_hdg = self.apt.runways.data[self.apt.runways.data.name == str(runway)]['bearing'].values[0]
        self.pox_min = self.bou[0]
        self.pox_max = self.bou[2]
        self.poy_min = self.bou[1]
        self.poy_max = self.bou[3]


    def __str__(self):
        return (f'Airport: {self.apt.name}, \n' +
                f'RWY: {self.rwy}, \n' +
                f'Alt: {self.apt.altitude}, \n' +
                f'Glideslope: {self.gli}, \n' +
                f'boundaries: {self.bou}')


    def generate_ga(self, alt_ini, alt_lvl, gsp_cli, gsp_lvl, roc_cli, dt):
        """
        Docstring comes here. BTW, what are the expected units here?
        """

        # dataframe to be returned
        df_traj = pd.DataFrame(columns = ['Time', 'Altitude[ft]', 'Groundspeed[kts]', 'SwissGridX', 'SwissGridY'])

        # general trajectory parameters
        gsp_ms_cl = conv.kt2mps(gsp_cli)
        gsp_ms_lv = conv.kt2mps(gsp_lvl)
        gsx_ms_cl = gsp_ms_cl*math.sin(math.radians(self.rwy_hdg))
        gsy_ms_cl = gsp_ms_cl*math.cos(math.radians(self.rwy_hdg))
        gsx_ms_lv = gsp_ms_lv*math.sin(math.radians(self.rwy_hdg))
        gsy_ms_lv = gsp_ms_lv*math.cos(math.radians(self.rwy_hdg))

        # determination starting point of GA
        alt_dif = conv.ft2m(alt_ini)-self.rwy_alt
        ini_dxy = alt_dif/math.tan(math.radians(self.gli))
        ini_dxx = ini_dxy*math.sin(math.radians(self.rwy_hdg-180))
        ini_dyy = ini_dxy*math.cos(math.radians(self.rwy_hdg-180))
        ini_pox = self.rwy_sgx + ini_dxx
        ini_poy = self.rwy_sgy + ini_dyy

        # modelling of climb phase of GA
        time = 0
        alt = alt_ini
        gsp = gsp_cli
        pox = ini_pox
        poy = ini_poy

        while alt <= alt_lvl:
            new_point = [time, alt, gsp, pox, poy]
            df_traj.loc[len(df_traj)] = new_point

            pox = pox + gsx_ms_cl * dt
            poy = poy + gsy_ms_cl * dt
            alt = alt + (roc_cli / 60) * dt
            time = time + dt

        # modelling of level phase of GA
        alt = alt_lvl
        gsp = gsp_lvl
        pox = pox + gsx_ms_lv
        poy = poy + gsy_ms_lv
        time = time+1

        while ((pox >= self.pox_min) and (pox <= self.pox_max) and (poy >= self.poy_min) and (poy <= self.poy_max)):
            new_point = [time, alt, gsp, pox, poy]
            df_traj.loc[len(df_traj)] = new_point

            pox = pox + gsx_ms_lv * dt
            poy = poy + gsy_ms_lv * dt
            time = time + dt

        return df_traj


    def get_dist_from_point(self, x: np.array, y: np.array) -> np.array:
        """
        Compute distance from runway theshold of position (x, y) in SwissGrid
        coordinates.
        """

        # compute runway angle counter-cockwise from x-axis
        rwy_hdg = self.rwy_hdg / 180 * np.pi
        rwy_angle = np.mod(-rwy_hdg+np.pi/2, 2*np.pi)

        unit_vector = np.array([np.cos(rwy_angle), np.sin(rwy_angle)]).T
        point = np.array([x, y]).T
        origin = np.array([self.rwy_sgx, self.rwy_sgy])

        v = point-origin

        # compute distance for both the x and y component 
        d1 = v[:,0]/unit_vector[0]
        d2 = v[:,1]/unit_vector[1]

        if np.abs((d1-d2).max()) > 0.5:
            # The difference between the x and y component is "large". This can be
            # case if the points are not on a line with the given runway heading.
            raise(ValueError('It seems like the points are not on a line.'))

        return d1


    def get_point_from_distance(self, d: np.array) -> np.array:

        # compute runway angle counter-cockwise from x-axis
        rwy_hdg = self.rwy_hdg / 180 * np.pi
        rwy_angle = np.mod(-rwy_hdg+np.pi/2, 2*np.pi)

        unit_vector = np.array([np.cos(rwy_angle), np.sin(rwy_angle)]).T

        v = np.zeros((len(d), 2))
        v[:,0] = d*unit_vector[0]
        v[:,1] = d*unit_vector[1]

        origin = np.array([self.rwy_sgx, self.rwy_sgy])

        return v+origin




ids_ga_14_to_drop = [1071988134765919846,
                     1138873995177104477,
                     738180731578328500,
                     842975429641387387,
                     327842723335173642,
                     839062345312112267,
                     609144539899491951,
                     764055676093680025,
                     154216314926678182,
                     614723918756610006,
                     729992596009337431,
                     66893017620426030,
                     371266025711420953,
                     190068172647965519,
                     1134063563208383509,
                     566115142173115111,
                     419048411584092765,
                     621730642046755048,
                     198673211403906425,
                     927638181414003834,
                     942145282920981360,
                     77628755448283907,
                     142835883591498895,
                     336731787256885210,
                     716456609260322436,
                     16353974751974071,
                     307877269827381222,
                     528384751596132252,
                     143833149030410795,
                     435501402099690625,
                     625790486052239118,
                     1013622812575959209,
                     384718910886528343,
                     1139743111424891551,
                     308804396816320416,
                     357060195384272385,
                     63336209332479251,
                     471895723616486367,
                     921348631936655055,
                     568712657075563320,
                     335510685803028438,
                     413473226818975230,
                     1029964907874324315,
                     164274611014955613,
                     359571047932687367,
                     1033468838979450157,
                     1003901224178590037,
                     1005261225582514020,
                     1061245321220323970,
                     119152194392414477,
                     1000863877743560478,
                     178449631662184993,
                     730902920046053462,
                     742954519759044219,
                     367189079080462170,
                     771409870240197822,
                     804947009226142828,
                     595132526279568076,
                     1133957760611966827,
                     928259115509458424,
                     309854115498773373,
                     458227380262993234,
                     801022279874326574,
                     103702258280940940,
                     176643232771392473,
                     386673001891091050,
                     556245353043941997,
                     826566883352566550,
                     204473540686061046,
                     519332650454664957,
                     740670502289671748,
                     872369826351321444,
                     268837167702277988,
                     177681987507729240,
                     303479854709008925,
                     365310006712533731,
                     1042011363001929021,
                     236966404708333539,
                     433373596866479047,
                     423902609135065491,
                     849876227520894034,
                     647565765795681264,
                     399470551266875573,
                     987703274105755225,
                     536329516027442679,
                     468913128413150770,
                     184241646824478623,
                     739560663573261204,
                     176303574766623154,
                     439996275685744537,
                     911966336231264187,
                     320766483880221886,
                     787993390616803506,
                     838780277448162166,
                     905639430987801116,
                     676184481738862983,
                     233696761460085141,
                     585185211210237972,
                     1068590887066634762,
                     925087113997976587,
                     120559387225314707,
                     969751146274584163,
                     345998832650887234,
                     192958967481496239,
                     984739146577357883,
                     343378909257807318,
                     283614835641131700,
                     343358009959873833,
                     677533079332218382,
                     796996074532117165,
                     904948114180824084,
                     1076872281127042460,
                     907374514592125876,
                     667199920466111546,
                     481546291827118187,
                     799485164578619208,
                     137097206852276942,
                     205364158797894760,
                     492776599471188887,
                     876462402777197831,
                     700475426261229286,
                     798996568704935815,
                     91571036149370040,
                     62636998648028381,
                     598106325163837659,
                     555496177019205414,
                     82285161235500829,
                     600884953457437042,
                     279467463047729931,
                     543653993654090855,
                     926910699202714226,
                     713035337956488004,
                     784587787252263896,
                     382598265259417487,
                     255561404884759658,
                     1105486061010804236,
                     281417933618713709,
                     927732708241648515,
                     873523140494199476,
                     937475247436357331,
                     476919229574405484,
                     714409373123776534,
                     682378245359893723,
                     576179047519597158,
                     915286828086331438,
                     725412245772860375,
                     910149289742043590,
                     1073043215806359115,
                     176327006300441513,
                     1138184536840752194,
                     321234216114661354,
                     307955605543343038,
                     118452805136509815,
                     168020865999890560,
                     599800019702644954,
                     17370048562919665,
                     1010150639290717009,
                     352067353621931411,
                     592163914706621148,
                     108249117717516223,
                     878747327140819466,
                     622856808264571864,
                     444567142296732054,
                     688937436362143730,
                     713429996451996754,
                     325413971270953094,
                     1134488719994788502,
                     57131250195364410,
                     1141183683699220652,
                     134635671079446093,
                     570318389726031774,
                     254419367731721090,
                     789181526032673720,
                     206273715061954648,
                     432803561973066238,
                     383752271981707222,
                     92372726527374324,
                     684221687892558485,
                     499530574154424264]

ids_ga_lsmd_to_drop = [307445286313341840,
                       79628826075572014,
                       26143790205801934,
                       792918423780416376,
                       1014613566434957813,
                       29569336200270180,
                       767580236474713511,
                       935453303140199665,
                       34757854137922034,
                       116044812249039542,
                       632572738079119020,
                       44761783314664440,
                       167420860889382597,
                       1074082157084653922,
                       216089067420663508,
                       1003234063697986034,
                       643804178878251296]


ids_ga_lszh14_to_keep = [0]



