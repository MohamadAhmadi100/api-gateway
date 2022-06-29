from typing import Optional

from fastapi import APIRouter, Response, HTTPException, Query

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.mobile_app.validators.model import ForceUpdate

router = APIRouter()


@router.post("/forceUpdate", tags=["ForceUpdate"])
def insert_force_update(
        response: Response,
        force_update: ForceUpdate
):
    """
    Insert force update
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "insert_force_update",
                    "body": force_update.__dict__
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/forceUpdate", tags=["ForceUpdate"])
def get_force_update(
        response: Response,
        os_type: Optional[str] = Query(None)
):
    """
    Get force update
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_force_update",
                    "body": {"os_type": os_type}
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/currency", tags=["Currency"])
def get_currency(
        response: Response,
):
    """
    Get currency
    """
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    #     product_result = rpc.publish(
    #         message={
    #             "mobile_app": {
    #                 "action": "get_currency",
    #                 "body": {}
    #             }
    #         },
    #         headers={'mobile_app': True}
    #     )
    #     product_result = product_result.get("mobile_app", {})
    #     if product_result.get("success"):
    #         response.status_code = product_result.get("status_code", 200)
    return {"message": {
        "harat_naghdi_buy": {
            "value": "29970",
            "change": 140,
            "timestamp": 1656484762,
            "date": "1401-04-08 11:09:22"
        },
        "harat_naghdi_sell": {
            "value": "29990",
            "change": 150,
            "timestamp": 1656484777,
            "date": "1401-04-08 11:09:37"
        },
        "sekkeh": {
            "value": "14350",
            "change": 0,
            "timestamp": 1656419977,
            "date": "1401-04-07 17:09:37"
        },
        "dirham_dubai": {
            "value": "8400",
            "change": -20,
            "timestamp": 1656484.352,
            "date": "1348-10-30 07:38:04"
        },
        "aed_sell": {
            "value": "8400",
            "change": -20,
            "timestamp": 1656484.352,
            "date": "1348-10-30 07:38:04"
        },
        "usd_farda_buy": {
            "value": "24910",
            "change": 0,
            "timestamp": 1607798179,
            "date": "1399-09-22 22:06:19"
        },
        "abshodeh": {
            "value": "5884",
            "change": 9,
            "timestamp": 1656484279,
            "date": "1401-04-08 11:01:19"
        },
        "usd_farda_sell": {
            "value": "24940",
            "change": 0,
            "timestamp": 1607798179,
            "date": "1399-09-22 22:06:19"
        },
        "usd_sell": {
            "value": "30720",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "usd_buy": {
            "value": "30600",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "dolar_harat_sell": {
            "value": "22730",
            "change": 0,
            "timestamp": 1575557809,
            "date": "1398-09-14 18:26:49"
        },
        "18ayar": {
            "value": "1358300",
            "change": 2100,
            "timestamp": 1656484272,
            "date": "1401-04-08 11:01:12"
        },
        "bahar": {
            "value": "13260",
            "change": 20,
            "timestamp": 1656484272,
            "date": "1401-04-08 11:01:12"
        },
        "nim": {
            "value": "7900",
            "change": -50,
            "timestamp": 1656484279,
            "date": "1401-04-08 11:01:19"
        },
        "rob": {
            "value": "4950",
            "change": 0,
            "timestamp": 1656484279,
            "date": "1401-04-08 11:01:19"
        },
        "gerami": {
            "value": "2100",
            "change": 0,
            "timestamp": 1641799896,
            "date": "1400-10-20 11:01:36"
        },
        "dolar_soleimanie_sell": {
            "value": "14000",
            "change": 0,
            "timestamp": 1575557809,
            "date": "1398-09-14 18:26:49"
        },
        "dolar_kordestan_sell": {
            "value": "11980",
            "change": 0,
            "timestamp": 1565795604,
            "date": "1398-05-23 19:43:24"
        },
        "dolar_mashad_sell": {
            "value": "14020",
            "change": 0,
            "timestamp": 1565795604,
            "date": "1398-05-23 19:43:24"
        },
        "cad_cash": {
            "value": "13610",
            "change": 0,
            "timestamp": 1591512632,
            "date": "1399-03-18 11:20:32"
        },
        "hav_cad_my": {
            "value": "24580",
            "change": 0,
            "timestamp": 1656418789,
            "date": "1401-04-07 16:49:49"
        },
        "": {
            "value": "0",
            "change": 0,
            "timestamp": 1638614375,
            "date": "1400-09-13 14:09:35"
        },
        "usdt": {
            "value": "31100",
            "change": 50,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd_shakhs": {
            "value": "31310",
            "change": -80,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd_sherkat": {
            "value": "31020",
            "change": -70,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "eur_hav": {
            "value": "32720",
            "change": -190,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "gbp_hav": {
            "value": "37580",
            "change": -110,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "aud_hav": {
            "value": "21240",
            "change": -150,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "myr_hav": {
            "value": "7010",
            "change": -20,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "cny_hav": {
            "value": "4690",
            "change": -10,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "try_hav": {
            "value": "1890",
            "change": 0,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "jpy_hav": {
            "value": "230",
            "change": 0,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "cad_hav": {
            "value": "24450",
            "change": -80,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "hav_cad_cheque": {
            "value": "24450",
            "change": -80,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "hav_cad_cash": {
            "value": "24460",
            "change": -80,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd_pp": {
            "value": "30720",
            "change": 0,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "eur_pp": {
            "value": "32370",
            "change": -190,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "aed_note": {
            "value": "8410",
            "change": -20,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "aed": {
            "value": "8400",
            "change": -20,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "gbp_wht": {
            "value": "37020",
            "change": -110,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "aud_wht": {
            "value": "20500",
            "change": -140,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd_doge": {
            "value": "2040",
            "change": -60,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "btc": {
            "value": "626923460",
            "change": -4855200,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "eth": {
            "value": "35234440",
            "change": -816470,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "xrp": {
            "value": "10420",
            "change": -160,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bch": {
            "value": "3212030",
            "change": -91710,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "ltc": {
            "value": "1628470",
            "change": -30210,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "eos": {
            "value": "29240",
            "change": -540,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bnb": {
            "value": "6845900",
            "change": -380630,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "dash": {
            "value": "1413140",
            "change": -49000,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd": {
            "value": "30720",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "eur": {
            "value": "32560",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gbp": {
            "value": "38150",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "jpy": {
            "value": "229.53",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "aud": {
            "value": "21500",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cad": {
            "value": "24430",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "chf": {
            "value": "32400",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ugx": {
            "value": "8.33",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cny": {
            "value": "4635",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "myr": {
            "value": "7050",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bgn": {
            "value": "16780",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pgk": {
            "value": "8810",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "irr": {
            "value": "0.74",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gmd": {
            "value": "570",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "xcd": {
            "value": "11430",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "htg": {
            "value": "268.12",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "top": {
            "value": "13320",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "vuv": {
            "value": "267.15",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "nok": {
            "value": "3165",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "isk": {
            "value": "234.84",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pkr": {
            "value": "147.39",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lbp": {
            "value": "20.54",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lyd": {
            "value": "6460",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "awg": {
            "value": "17130",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mwk": {
            "value": "30.35",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cup": {
            "value": "31000",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bwp": {
            "value": "2530",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "rub": {
            "value": "555",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "brl": {
            "value": "5940",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "azn": {
            "value": "18270",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "uyu": {
            "value": "780",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "stn": {
            "value": "1315",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "djf": {
            "value": "174.18",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mmk": {
            "value": "16.75",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "qar": {
            "value": "8460",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "clp": {
            "value": "33.7",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sek": {
            "value": "3080",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ils": {
            "value": "9090",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "kgs": {
            "value": "385.34",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "crc": {
            "value": "44.9",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "fjd": {
            "value": "14110",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cdf": {
            "value": "15.5",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "hnl": {
            "value": "1260",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lkr": {
            "value": "85.76",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "dkk": {
            "value": "4410",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "xaf": {
            "value": "49.82",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "tjs": {
            "value": "2815",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mga": {
            "value": "7.62",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lrd": {
            "value": "204.16",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ssp": {
            "value": "63.18",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lsl": {
            "value": "1935",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "scr": {
            "value": "2395",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "kwd": {
            "value": "101260",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "vnd": {
            "value": "1.33",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "egp": {
            "value": "1655",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "svc": {
            "value": "3540",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ttd": {
            "value": "4565",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ghs": {
            "value": "3900",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mru": {
            "value": "855",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "tzs": {
            "value": "13.3",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mnt": {
            "value": "9.92",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "nzd": {
            "value": "19520",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ron": {
            "value": "6640",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pen": {
            "value": "8210",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "jod": {
            "value": "43760",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "iqd": {
            "value": "21.25",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cve": {
            "value": "294.35",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "lak": {
            "value": "2.05",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "dop": {
            "value": "565",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sar": {
            "value": "8270",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "try": {
            "value": "1870",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bdt": {
            "value": "335.08",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pyg": {
            "value": "4.52",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mad": {
            "value": "3095",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "xpf": {
            "value": "272.64",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "aoa": {
            "value": "72.71",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "yer": {
            "value": "123.94",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "zar": {
            "value": "1955",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "idr": {
            "value": "2.09",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "kzt": {
            "value": "67.67",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bob": {
            "value": "4515",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bzd": {
            "value": "15380",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "kmf": {
            "value": "66.4",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "all": {
            "value": "272.43",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "khr": {
            "value": "7.63",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "czk": {
            "value": "1325",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "thb": {
            "value": "880",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "php": {
            "value": "565",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "tmt": {
            "value": "8860",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "afn": {
            "value": "345.08",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "jmd": {
            "value": "204.86",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gip": {
            "value": "38010",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "szl": {
            "value": "1935",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "npr": {
            "value": "247.51",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "krw": {
            "value": "24.13",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bhd": {
            "value": "82460",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "twd": {
            "value": "1045",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "uah": {
            "value": "1055",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "etb": {
            "value": "595",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "srd": {
            "value": "1415",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "syp": {
            "value": "12.59",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ern": {
            "value": "2055",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sos": {
            "value": "53.6",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "wst": {
            "value": "12020",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mur": {
            "value": "695",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "huf": {
            "value": "81.73",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ngn": {
            "value": "74.75",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "rsd": {
            "value": "279.71",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mkd": {
            "value": "530",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sbd": {
            "value": "3850",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ang": {
            "value": "17380",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mop": {
            "value": "3830",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bam": {
            "value": "16620",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "dzd": {
            "value": "213.01",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pln": {
            "value": "6990",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "hrk": {
            "value": "4360",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "byn": {
            "value": "9740",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ars": {
            "value": "249.88",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "tnd": {
            "value": "10120",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bif": {
            "value": "15.07",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "zmw": {
            "value": "1820",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gtq": {
            "value": "4000",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bnd": {
            "value": "22320",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sgd": {
            "value": "22400",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "hkd": {
            "value": "3955",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "amd": {
            "value": "71.46",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "ves": {
            "value": "5660",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bsd": {
            "value": "31000",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gnf": {
            "value": "3.57",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gel": {
            "value": "10530",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "omr": {
            "value": "80600",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "cop": {
            "value": "7.61",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mxn": {
            "value": "1560",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mdl": {
            "value": "1615",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "nio": {
            "value": "865",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "gyd": {
            "value": "148.21",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "rwf": {
            "value": "30.35",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sll": {
            "value": "2.36",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mvr": {
            "value": "2005",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "inr": {
            "value": "394.7",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "bbd": {
            "value": "15360",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "xof": {
            "value": "49.9",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "uzs": {
            "value": "2.83",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "pab": {
            "value": "31010",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "nad": {
            "value": "1935",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "sdg": {
            "value": "54.54",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mzn": {
            "value": "483.83",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "kes": {
            "value": "263.67",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mro": {
            "value": "850",
            "change": 0,
            "timestamp": 1656437371,
            "date": "1401-04-07 21:59:31"
        },
        "mex_usd_sell": {
            "value": "277079",
            "change": -50,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "mex_usd_buy": {
            "value": "274322",
            "change": -49,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "mex_eur_sell": {
            "value": "286425",
            "change": -201,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "mex_eur_buy": {
            "value": "283575",
            "change": -199,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "xau": {
            "value": "55909790",
            "change": -7210,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_sekkeh": {
            "value": "1162540",
            "change": 1700,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_bahar": {
            "value": "102540",
            "change": 21700,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_rob": {
            "value": "1631040",
            "change": 430,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_18ayar": {
            "value": "10140",
            "change": 2270,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_abshodeh": {
            "change_val": 0,
            "change_pct": 0,
            "time": 1557749542,
            "date": 1656484352
        },
        "bub_gerami": {
            "value": "452210",
            "change": 210,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "bub_nim": {
            "value": "1292080",
            "change": -49150,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "usd_xau": {
            "value": "1819.98",
            "change": -0.23499999999989996,
            "timestamp": 1656484352,
            "date": "1401-04-08 11:02:32"
        },
        "mob_usd": {
            "value": "42000",
            "change": 0,
            "timestamp": 1560948147,
            "date": "1398-03-29 17:12:27"
        },
        "mob_gbp": {
            "value": "54933",
            "change": 0,
            "timestamp": 1560948147,
            "date": "1398-03-29 17:12:27"
        },
        "mob_eur": {
            "value": "48872",
            "change": 0,
            "timestamp": 1560948147,
            "date": "1398-03-29 17:12:27"
        },
        "mob_aed": {
            "value": "11437",
            "change": 0,
            "timestamp": 1560948147,
            "date": "1398-03-29 17:12:27"
        }
    }}
    #     raise HTTPException(status_code=product_result.get("status_code", 500),
    #                         detail={"error": product_result.get("error", "Something went wrong")})
