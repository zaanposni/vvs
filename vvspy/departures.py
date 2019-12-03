from typing import List, Union
from datetime import datetime
import requests
import json

from vvspy.obj import Departure, Arrival

API_URL = "http://www3.vvs.de/vvs/widget/XML_DM_REQUEST?"
# TODO: new station id format de:08111:2599 (lapp kabel)


def _get_api_response(station_id: Union[str, int], check_time: datetime = None, dep_arr: str = "departure",
                      limit: int = 100, **kwargs) -> List[Union[Arrival, Departure]]:  # TODO: use func for arr and dep
    if not check_time:
        check_time = datetime.now()

    params = {
        "locationServerActive": kwargs.get("locationServerActive", 1),  # typo from zocationServerActive ?!
        "lsShowTrainsExplicit": kwargs.get("lsShowTrainsExplicit", 1),
        "stateless": kwargs.get("stateless", 1),
        "language": kwargs.get("language", "de"),
        "SpEncId": kwargs.get("SpEncId", 0),
        "anySigWhenPerfectNoOtherMatches": kwargs.get("anySigWhenPerfectNoOtherMatches", 1),
        "limit": limit,
        "depArr": dep_arr,
        "type_dm": kwargs.get("type_dm", "any"),
        "anyObjFilter_dm": kwargs.get("anyObjFilter_dm", 2),
        "deleteAssignedStops": kwargs.get("deleteAssignedStops", 1),
        "name_dm": station_id,
        "mode": kwargs.get("mode", "direct"),
        "dmLineSelectionAll": kwargs.get("dmLineSelectionAll", 1),
        "useRealtime": kwargs.get("useRealtime", 1),  # live delay
        "outputFormat": kwargs.get("outputFormat", "json"),
        "coordOutputFormat": kwargs.get("coordOutputFormat", "WGS84[DD.ddddd]"),
        "itdDateYear": check_time.strftime("%Y"),
        "itdDateMonth": check_time.strftime("%m"),
        "itdDateDay": check_time.strftime("%d"),
        "itdTimeHour": check_time.strftime("%H"),
        "itdTimeMinute": check_time.strftime("%M")

    }

    r = requests.get(API_URL, params=params, **kwargs.get("request_params", {}))
    r.encoding = 'UTF-8'
    return _parse_response(r.json())  # TODO: error handling


def _parse_response(result: dict) -> List[Union[Arrival, Departure]]:
    parsed_response = []
    if not result or "departureList" not in result or not result["departureList"]:  # error in response/request
        return []

    if isinstance(result["departureList"], dict):  # one result
        parsed_response.append(Departure(**result["departureList"]["departure"]))
    elif isinstance(result["departureList"], list):  # multiple result
        for departure in result["departureList"]:
            parsed_response.append(Departure(**departure))

    return parsed_response


departures = _get_api_response  # alias
