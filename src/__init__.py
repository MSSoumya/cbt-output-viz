from flask import Flask, render_template
from pymongo import MongoClient 
from collections import OrderedDict
import json
import collections
import re
import pprint

pp = pprint.PrettyPrinter(indent=4)

client = MongoClient('localhost', 27017)   
db = client.xyz    
collection = db.abc 
 
app = Flask(__name__)

@app.route('/')
def homep():
    # try:
    return render_template("layout.html")
    # except Exception as e:
    #     return str(e)


@app.route('/graph')
def graph(chartID = 'chart_ID', chart_type = 'column', chart_height = 400):
    viz_data = get_latest_doc_from_db()
    viz_data = collections.OrderedDict(sorted(viz_data.items()))
    pp.pprint(viz_data["cbt_results"]["output_8"])
    num_of_outputs = len(viz_data["cbt_results"].keys())
    data_to_viz = {}
    for output,i in zip(viz_data["cbt_results"].keys(), range(num_of_outputs)):
        data_to_viz[output] = {}
        for key in viz_data["cbt_results"][output].keys():
            pp.pprint(output)
            if key == "0" or key == "1":
                all_data = viz_data["cbt_results"][output][key]

                pp.pprint(all_data)
                if all_data["global options"]["rw"] == "randread":
                    rw_var = "read"
                if all_data["global options"]["rw"] == "randwrite":
                    rw_var = "write"
                clat_perc = all_data["jobs"][0][rw_var]["clat_ns"]["percentile"]
                # pp.pprint(clat_perc)
                all_data["jobs"][0][rw_var]["clat_ns"].pop("percentile")
                clat_data=all_data["jobs"][0][rw_var]["clat_ns"]
                parsed_perc_clat = collections.OrderedDict(map(lambda (k,v): (float(k),v), clat_perc.items()))
                iodepth_data = all_data["jobs"][0]["iodepth_level"]
                latency_data = all_data["jobs"][0]["latency_ms"]
                slat_data = all_data["jobs"][0][rw_var]["slat_ns"]
                lat_data= all_data["jobs"][0][rw_var]["lat_ns"]
                raw = get_x_y(parsed_perc_clat)
                x_vals1 = raw[0]
                y_vals1 = raw[1]
                raw = get_x_y(clat_data)
                x_vals2 = [x.encode('UTF8') for x in raw[0]]
                y_vals2 = raw[1]
                raw = get_x_y(slat_data)
                x_vals3 = [x.encode('UTF8') for x in raw[0]]
                y_vals3 = raw[1]    
                raw = get_x_y(lat_data)
                x_vals4 = [x.encode('UTF8') for x in raw[0]]
                y_vals4 = raw[1]
                raw = get_x_y(iodepth_data)
                x_vals_a = [x.encode('UTF8') for x in raw[0]]
                y_vals_a = raw[1]
                raw = get_x_y(latency_data)
                x_vals_b = [x.encode('UTF8') for x in raw[0]]
                y_vals_b = raw[1]

                data_to_viz[output][key] = {
                    "charts" : [
                                 [
                                    { 
                                    "id": "1"+str(i)+key,
                                    "chart": {"renderTo": "chart1"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"showInLegend": 'false', "name": 'Value', "data": y_vals1}],
                                    "title": {"text": rw_var+' cycle Completion latency Percentiles'},
                                    "xAxis": {"categories": x_vals1, "title": {"text": 'Percentiles'}},
                                    "yAxis": {"title": {"text": 'Values'}},
                                    "chartID": "chartID1"+str(i)+key
                                    },
                                    { 
                                    "id": "2"+str(i)+key,
                                    "chart": {"renderTo": "chart2"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"name": 'Value', "data": y_vals2}],
                                    "title": {"text": rw_var+' cycle Completion Latency Statistics'},
                                    "xAxis": {"categories": x_vals2},
                                    "yAxis": {"title": {"text": 'Time taken'}},
                                    "chartID": "chartID2"+str(i)+key
                                    },
                                    {
                                    "id": "3"+str(i)+key,
                                    "chart": {"renderTo": "chart3"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"name": 'Value', "data": y_vals3}],
                                    "title": {"text": rw_var+' cycle Submission Latency'},
                                    "xAxis": {"categories": x_vals3},
                                    "yAxis": {"title": {"text": 'Time taken'}},
                                    "chartID": "chartID3"+str(i)+key
                                    },
                                    {
                                    "id": "4"+str(i)+key,
                                    "chart": {"renderTo": "chart4"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"name": 'Value', "data": y_vals4}],
                                    "title": {"text": rw_var+' cycle Total Latency'},
                                    "xAxis": {"categories": x_vals4},
                                    "yAxis": {"title": {"text": 'Time taken'}},
                                    "chartID": "chartID4"+str(i)+key
                                    }   
                                 ],
                                 [
                                    {
                                    "id": "a"+str(i)+key,
                                    "chart": {"renderTo": "chart_a"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"data": y_vals_a}],
                                    "title": {"text": 'Trim cycle IO depth levels'},
                                    "xAxis": {"categories": x_vals_a, "title": {"text": 'IO Depth levels'}},
                                    "yAxis": {"title": {"text": 'Values'}},
                                    "chartID": "chartID_a"+str(i)+key
                                    },
                                    {
                                    "id": "b"+str(i)+key,
                                    "chart": {"renderTo": "chart_b"+str(i)+str(key), "type": chart_type, "height": chart_height},
                                    "series": [{"data": y_vals_b}],
                                    "title": {"text": 'Experiment Latency'},
                                    "xAxis": {"categories": x_vals_b, "title": {"text": 'Latency'}},
                                    "yAxis": {"title": {"text": 'Percentages'}},
                                    "chartID": "chartID_b"+str(i)+key
                                    }   ]
                                ]}

                data_to_viz[output][key]["disk_util_data"] = all_data["disk_util"][0]
                basic_info= {}
                basic_info["Fio Version"] = all_data["fio version"]
                basic_info["Timestamp"] = all_data["timestamp"]
                basic_info["Time"] = all_data["time"]
                data_to_viz[output][key]["basic_info"] = basic_info
                data_to_viz[output][key]["global_info"] = all_data["global options"]

    pp.pprint(data_to_viz["output_1"])
    return render_template('index.html', viz_data=sortDictRec(data_to_viz))
 

def get_x_y(data):
    vals= []
    vals.append(data.keys()) #x values
    vals.append(data.values()) #y values 
    return vals

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def sortDictRec(od):
    convert = lambda text: float(text) if isfloat(text) else text
    alphanum_key = lambda pair: [convert(c) for c in re.split('([-+]?\d*\.\d+|\d+)', pair[0])] 

    res = OrderedDict()
    for k, v in sorted(od.items(), key=alphanum_key):
        if isinstance(v, dict):
            res[k] = sortDictRec(v)
        elif isinstance(v, list):
            res[k] = sortListRec(v)
        else:
            res[k] = v
    return res

def sortListRec(ls):
    newls = []
    for v in ls:
        if isinstance(v, dict):
            newls.append(sortDictRec(v))
        elif isinstance(v, list):
            newls.append(sortListRec(v))
        else:
            newls.append(v)
    return newls


def get_latest_doc_from_db():
    result = collection.find().sort( [['_id', -1]] ).limit(1) #to fetch the latest document stored in db
    cbt_res_viz_data = sortDictRec(result[0])
    return cbt_res_viz_data

if __name__ == "__main__":
    app.run(debug = True, port=8000, passthrough_errors=True)
