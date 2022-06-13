import numpy as np
import pandas as pd
from airtraj import conversions as conv
import pickle
from traffic.data import airports
from os import path


def proba_col_when_both_in_volume(
    traj, kde_dict, theta=90, vga_lszh=100, dt=1
):
    lambda_xy = 265 * 0.3048  # meter
    lambda_h = 165 * 0.3048  # meter
    kde = kde_dict["kde"]

    coords_traj = np.array(
        [
            traj["SwissGridX"].values,
            traj["SwissGridY"].values,
            conv.ft2m(traj["Altitude[ft]"].values),
        ]
    )

    log_pdf_traj = kde.score_samples(coords_traj.T)
    pdf_traj = np.exp(log_pdf_traj)
    ct = np.cos(np.deg2rad(theta))
    st = np.sin(np.deg2rad(theta))
    vga_dub = traj["Groundspeed[kts]"].values / 1.94384

    col_prob = (
        4
        * lambda_xy
        * lambda_h
        * (
            np.sqrt((vga_dub * ct - vga_lszh) ** 2 + (vga_dub * st) ** 2)
            * pdf_traj
        ).sum()
        * dt
    )

    return col_prob


def proba_col_when_simult_landings(
    traj, kde_dict, theta=90, vga_lszh=100, dt=1
):
    # median time spent on GA 14:
    ga_14_time_total = 991  # seconds

    # probability that GA 14 is ever in the volume:
    p_ga_going_into_f = kde_dict["n_GAs_in_volume"] / kde_dict["n_total_GAs"]

    # probability that GA 14 is in volume of f:
    p_ga14_in_f = (
        kde_dict["mean_time_in_volume"] / ga_14_time_total
    ) * p_ga_going_into_f

    # probability that GA 14 is in volume of f
    p_ga29_in_f = 0.5
    p_vol = proba_col_when_both_in_volume(
        traj, kde_dict, theta=theta, vga_lszh=vga_lszh, dt=dt
    )
    return p_vol * p_ga14_in_f * p_ga29_in_f


def load_ga_lsmd(data_dir):
    with open(path.join(data_dir, "trajs_dict_ga_lsmd.pkl"), "rb") as handle:
        trajs_dict_ga_lsmd = pickle.load(handle)

    # return keys (ID's here)
    trajs_dict_ga_lsmd.keys()

    # drop bad GA's and keep o nly relatively standard ones
    trajs_dict_ga_lsmd = {
        key: value
        for key, value in trajs_dict_ga_lsmd.items()
        if key not in ids_ga_lsmd_to_drop
    }

    # get altitude of lsmd in m
    ALT_LSMD = airports["LSMD"].altitude * 0.3048

    # make baro alt so that it lands on the ground in the end
    for traje in trajs_dict_ga_lsmd.values():
        last_alt = traje.data.tail(3)["AltitudeBaro"].median()
        difference = last_alt - ALT_LSMD
        traje.data["AltitudeBaro"] = traje.data["AltitudeBaro"] - difference

    # create df with all GAs in LSMD
    df_ga_lsmd = pd.concat(
        [trajs_dict_ga_lsmd[ids].data.tail(240) for ids in trajs_dict_ga_lsmd]
    )

    # df_ga_lsmd = df_ga_lsmd.filter(
    #     [
    #         "ID",
    #         "Groundspeed",
    #         "AltitudeBaro",
    #         "AltitudeGPS",
    #         "SwissGridX",
    #         "SwissGridY",
    #         "Lat",
    #         "Lon",
    #     ]
    # )
    return df_ga_lsmd


def load_ga_lszh(data_dir):

    with open(
        path.join(data_dir, "trajs_dict_ga_lszh_rwy_14.pkl"), "rb"
    ) as handle:
        trajs_dict_ga_lszh14 = pickle.load(handle)

    trajs_dict_ga_lszh14 = {
        key: value
        for key, value in trajs_dict_ga_lszh14.items()
        if key not in ids_ga_14_to_drop
    }
    # get altitude of lszh in m
    ALT_LSZH = airports["LSZH"].altitude * 0.3048

    for traje in trajs_dict_ga_lszh14.values():
        last_alt = traje.data.tail(3)["AltitudeBaro"].median()
        difference = last_alt - ALT_LSZH
        traje.data["AltitudeBaro"] = traje.data["AltitudeBaro"] - difference

    df_ga_lszh14 = pd.concat(
        [
            trajs_dict_ga_lszh14[ids].data.tail(240).sort_index()
            for ids in trajs_dict_ga_lszh14
        ]
    )

    df_ga_lszh14 = df_ga_lszh14.query(
        "(@lon_bounds[0]< Lon< @lon_bounds[1]) & (@lat_bounds[0]< Lat< @lat_bounds[1]) & (@alt_bounds[0]< AltitudeGPS< @alt_bounds[1])"
    )

    # df_ga_lszh14_spatfilt = pd.concat(trajs_list_spatial)
    return df_ga_lszh14


def zoom_center(
    lons: tuple = None,
    lats: tuple = None,
    lonlats: tuple = None,
    format: str = "lonlat",
    projection: str = "mercator",
    width_to_height: float = 2.0,
) -> (float, dict):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434

    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.

    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
        if isinstance(lonlats, tuple):
            lons, lats = zip(*lonlats)
        else:
            raise ValueError("Must pass lons & lats or lonlats")

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        "lon": round((maxlon + minlon) / 2, 6),
        "lat": round((maxlat + minlat) / 2, 6),
    }

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array(
        [
            0.0007,
            0.0014,
            0.003,
            0.006,
            0.012,
            0.024,
            0.048,
            0.096,
            0.192,
            0.3712,
            0.768,
            1.536,
            3.072,
            6.144,
            11.8784,
            23.7568,
            47.5136,
            98.304,
            190.0544,
            360.0,
        ]
    )

    if projection == "mercator":
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width, lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f"{projection} projection is not implemented"
        )

    return zoom, center


# lon_bounds = [8.50, 8.76]
lon_bounds = [8.30, 8.96]
# lat_bounds = [47.35, 47.44]
lat_bounds = [47.05, 47.64]
# lat_bounds[1] += 0.05
sgx_bounds = [680000, 699800]
sgy_bounds = [245000, 254800]
alt_bounds = [609, 2407]

ids_ga_14_to_drop = [
    1071988134765919846,
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
    499530574154424264,
]

ids_ga_lsmd_to_drop = [
    307445286313341840,
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
    643804178878251296,
]
