from flask import Flask, render_template
import json
import sys
import collections
 
app = Flask(__name__)

@app.route('/')
def homepage():

    title = "CBT-librbdfio Output"
    paragraph = [""]

    try:
        return render_template("index.html", title = title, paragraph=passthrough_errorsragraph)
    except Exception, e:
        return str(e)


@app.route('/graph')
def graph(chartID = 'chart_ID', chart_type = 'column', chart_height = 400):
    clat_perc = all_data["jobs"][0]["write"]["clat"]["percentile"]
    all_data["jobs"][0]["write"]["clat"].pop("percentile")
    clat_data=all_data["jobs"][0]["write"]["clat"]
    parsed_perc_clat = collections.OrderedDict(map(lambda (k,v): (float(k),v), clat_perc.iteritems()))
    iodepth_data = all_data["jobs"][0]["iodepth_level"]
    latency_data = all_data["jobs"][0]["latency_ms"]
    write_slat = all_data["jobs"][0]["write"]["slat"]
    write_lat= all_data["jobs"][0]["write"]["lat"]
    raw = get_x_y(parsed_perc_clat)
    x_vals1 = raw[0]
    y_vals1 = raw[1]
    raw = get_x_y(clat_data)
    x_vals2 = [x.encode('UTF8') for x in raw[0]]
    y_vals2 = raw[1]
    raw = get_x_y(write_slat)
    x_vals3 = [x.encode('UTF8') for x in raw[0]]
    y_vals3 = raw[1]    
    raw = get_x_y(write_lat)
    x_vals4 = [x.encode('UTF8') for x in raw[0]]
    y_vals4 = raw[1]
    raw = get_x_y(iodepth_data)
    x_vals_a = [x.encode('UTF8') for x in raw[0]]
    y_vals_a = raw[1]
    raw = get_x_y(latency_data)
    x_vals_b = [x.encode('UTF8') for x in raw[0]]
    y_vals_b = raw[1]

    write_charts = [
        { 
        "id": "1",
        "chart": {"renderTo": "chart1", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals1}],
        "title": {"text": 'Write cycle Completion latency Percentiles'},
        "xAxis": {"categories": x_vals1, "title": {"text": 'Percentiles'}},
        "yAxis": {"title": {"text": 'Values'}},
        "chartID": "chartID1"
        },
        { 
        "id": "2",
        "chart": {"renderTo": "chart2", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals2}],
        "title": {"text": 'Write cycle Completion Latency Statistics'},
        "xAxis": {"categories": x_vals2, "title": {"text": 'Statistics'}},
        "yAxis": {"title": {"text": 'Time taken'}},
        "chartID": "chartID2"
        },
        {
        "id": "3",
        "chart": {"renderTo": "chart3", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals3}],
        "title": {"text": 'Write cycle Submission Latency'},
        "xAxis": {"categories": x_vals3, "title": {"text": 'Statistics'}},
        "yAxis": {"title": {"text": 'Time taken'}},
        "chartID": "chartID3"
        },
        {
        "id": "4",
        "chart": {"renderTo": "chart4", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals4}],
        "title": {"text": 'Write cycle Total Latency'},
        "xAxis": {"categories": x_vals4, "title": {"text": 'Statistics'}},
        "yAxis": {"title": {"text": 'Time taken'}},
        "chartID": "chartID4"
        }   

    ]

    other_charts= [
        {
        "id": "a",
        "chart": {"renderTo": "chart_a", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals_a}],
        "title": {"text": 'Trim cycle IO depth levels'},
        "xAxis": {"categories": x_vals_a, "title": {"text": 'IO Depth levels'}},
        "yAxis": {"title": {"text": 'Values'}},
        "chartID": "chartID_a"
        },
        {
        "id": "b",
        "chart": {"renderTo": "chart_b", "type": chart_type, "height": chart_height},
        "series": [{"name": 'Value', "data": y_vals_b}],
        "title": {"text": 'Experiment Latency'},
        "xAxis": {"categories": x_vals_b, "title": {"text": 'Latency'}},
        "yAxis": {"title": {"text": 'Percentages'}},
        "chartID": "chartID_b"
        }   
    ]

    charts=[]
    charts.append(write_charts)
    charts.append(other_charts)
    disk_util_data = all_data["disk_util"][0]
    basic_info= {}
    basic_info["Fio Version"] = all_data["fio version"]
    basic_info["Timestamp"] = all_data["timestamp"]
    basic_info["Time"] = all_data["time"]
    global_info = all_data["global options"]
    return render_template('index.html', charts=charts, disks=disk_util_data, basic_info=basic_info, global_info=global_info)
 

def get_x_y(data):
    vals= []
    vals.append(data.keys()) #x values
    vals.append(data.values()) #y values 
    return vals


if __name__ == "__main__":
    with open('../input/fio_json.out') as fp:
        global all_data 
        all_data = json.loads(fp.read(), object_pairs_hook=collections.OrderedDict)

    app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
