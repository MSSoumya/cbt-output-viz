import json
import matplotlib.pyplot as plt
import sys
import collections


def data_viz(data,title,x_label,y_label):
    keys = data.keys()
    vals = data.values()
    plt.bar(range(len(keys)), vals, align='center')
    plt.xticks(range(len(keys)), keys, rotation=30)
    plt
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig("output/"+title+".png")
    plt.close()
             

if __name__ == '__main__':
    with open(sys.argv[1]) as fp:
        data = json.loads(fp.read(), object_pairs_hook=collections.OrderedDict)

        clat_data = data["jobs"][0]["write"]["clat"]["percentile"]
        parsed_clat_data = collections.OrderedDict(map(lambda (k,v): (float(k),v), clat_data.iteritems()))
        data_viz(parsed_clat_data, "Write cycle clat Percentiles","Percentiles","Values")

        iodepth_data = data["jobs"][0]["iodepth_level"]
        data_viz(iodepth_data,"Trim cycle IO depth levels","IO Depth levels","Values")

        latency_data = data["jobs"][0]["latency_ms"]
        data_viz(latency_data,"Latency","latency","percentages")
        
        












