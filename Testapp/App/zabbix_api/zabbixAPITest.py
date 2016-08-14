# -*- coding: utf-8 -*-
#import
from App.zabbix_api.zabbixAPI import ZabbixAPI
from django.shortcuts import render,HttpResponse
import json
import pycurl


def getWebData(request):
    za = ZabbixAPI("http://192.168.56.50/zabbix/api_jsonrpc.php")
    result = za.auth("Admin", "zabbix")

    if result is False:
        print
        za.errstr

    # Processor load (5 min average per core)   23297
    result = za.get_history(
        **{
            "output":"extend",
            "history": 0,
            "itemid": ["24526"],
            "time_from": "1470715200",  # 2016-08-09 00:00:00
            "time_till": "1470801599"  # 2016-08-09 23:59:59
        }
    )

    # 从result字典中取数clock 和 value
    clockData = []
    valueData = []
    data = {}

    # print('result:',result)
    # resutlt is not null
    if result:
        for item in result:
            clockData.append(item['clock'])

            item_value=item['value']
            if item_value == "0.0000":
                # print("item_value:", item_value)
                item_value="0.001"

            valueData.append(item_value)
        # clockList:clockList,valueList:valueList
        data = {"clockList": clockData, "valueList": valueData}

        print("clockList:",clockData)
        print("valueData:", valueData)

    return HttpResponse(json.dumps(data))
    # return HttpResponse()

