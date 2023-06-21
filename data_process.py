import pandas as pd
import numpy as np


def getMetaParam(X_AXIS, Y_AXIS):
    parameters = dict()

    df = pd.read_csv("./all_results.csv")

    PARAMETER_LIST = df.columns.values.tolist()
    PARAMETER_LIST.remove(X_AXIS)
    PARAMETER_LIST.remove(Y_AXIS)
    try:
        PARAMETER_LIST.remove("HtoD Avg (ms)")
    except ValueError:
        pass

    try:
        PARAMETER_LIST.remove("DtoH Avg (ms)")
    except ValueError:
        pass

    try:
        PARAMETER_LIST.remove("Kernel Time (ms)")
    except ValueError:
        pass

    for p in PARAMETER_LIST:
        parameters[p] = np.transpose(
            df.filter(items=[p]).drop_duplicates().to_numpy()
        ).tolist()[0]

    return parameters


def selectData(select_options):
    preset_options = {
        "x_axis": "stratas",
        "y_axis": "Kernel Time (ms)",
        "channels": [],
        "hardware": [],
        "backend": [],
        "block_depth": [],
        "image_size": 1440,
        "stratas": [],
    }

    integer_list = ["channels","block_depth","stratas"]

    for key in select_options:
        preset_options[key] = select_options[key]

    select_options = preset_options

    # What filter should be integer?
    for i in integer_list:
        tmp = []
        for j in select_options[i]:
            tmp.append(int(j))
        select_options[i] = tmp

    parameters = dict()

    df = pd.read_csv("./all_results.csv")

    PARAMETER_LIST = df.columns.values.tolist()
    PARAMETER_LIST.remove(select_options["x_axis"])
    PARAMETER_LIST.remove(select_options["y_axis"])

    try:
        PARAMETER_LIST.remove("HtoD Avg (ms)")
    except ValueError:
        pass

    try:
        PARAMETER_LIST.remove("DtoH Avg (ms)")
    except ValueError:
        pass

    try:
        PARAMETER_LIST.remove("Kernel Time (ms)")
    except ValueError:
        pass

    # Chosen Image Size
    data = df[df["image_size"] == int(select_options["image_size"])]

    # Set Distinct data in parameter
    for p in PARAMETER_LIST:
        parameters[p] = np.transpose(
            df.filter(items=[p]).drop_duplicates().to_numpy()
        ).tolist()[0]

    # Remove image size from calculation
    PARAMETER_LIST.remove("image_size")

    # Divide Data
    divide_sandbox = [data]
    tmp = []

    for p in PARAMETER_LIST:
        for datablock in divide_sandbox:
            for i in parameters[p]:
                tmp.append(datablock[(datablock[p] == i)])
        divide_sandbox = tmp
        tmp = []

    # print(divide_sandbox)
    # print("Array Size:", len(divide_sandbox))

    table_set = []
    # Filter Here
    for datablock in divide_sandbox:
        # print(datablock["channels"].iloc[0])
        condition_satisfy = True
        for p in PARAMETER_LIST:
            if (len(select_options[p]) != 0) and select_options["x_axis"] != p:
                if (datablock[p]).iloc[0] not in select_options[p]:
                    condition_satisfy = False

        # Old codes
        # if (
        #     len(select_options["hardware"]) != 0
        #     and select_options["x_axis"] != "hardware"
        # ):
        #     if datablock["hardware"].iloc[0] not in select_options["hardware"]:
        #         condition_satisfy = False
        # if (
        #     len(select_options["backend"]) != 0
        #     and select_options["x_axis"] != "backend"
        # ):
        #     if datablock["backend"].iloc[0] not in select_options["backend"]:
        #         condition_satisfy = False
        # if (
        #     len(select_options["block_depth"]) != 0
        #     and select_options["x_axis"] != "block_depth"
        # ):
        #     if datablock["block_depth"].iloc[0] not in select_options["block_depth"]:
        #         condition_satisfy = False
        # if len(select_options["stratas"]) != 0 and select_options["x_axis"] != "stratas":
        #     if datablock["stratas"].iloc[0] not in select_options["stratas"]:
        #         condition_satisfy = False
        if condition_satisfy:
            table_set.append(datablock)

    # Find Array Min Max
    X_MIN = table_set[0][select_options["x_axis"]].min()
    X_MAX = 0

    Y_MIN = table_set[0][select_options["y_axis"]].min()
    Y_MAX = 0

    for d in table_set:
        tmp_xmin, tmp_xmax = float(d[select_options["x_axis"]].min()), float(
            d[select_options["x_axis"]].max()
        )
        tmp_ymin, tmp_ymax = float(d[select_options["y_axis"]].min()), float(
            d[select_options["y_axis"]].max()
        )

        if X_MIN > tmp_xmin:
            X_MIN = tmp_xmin
        if X_MAX < tmp_xmax:
            X_MAX = tmp_xmax

        if Y_MIN > tmp_ymin:
            Y_MIN = tmp_ymin
        if Y_MAX < tmp_ymax:
            Y_MAX = tmp_ymax

    expdata = []
    # Getting Groups
    for graph_line in table_set:
        element = dict()

        # Group Name
        desc = "| "

        # Group name in object
        desc_dict = dict()
        for p in parameters:
            desc += str(p) + ":" + str(graph_line.iloc[0][p]) + " "
            desc_dict[p] = graph_line.iloc[0][p]
        desc += "|"
        element["desc"] = desc

        # we can't jsonify the dict, we need to encode it to string
        # Translate the single quote to double quote, let the JSON parse in the webpage possible
        element["desc_dict"] = str(desc_dict).replace("'", '"')

        # Group Data
        element["data"] = (
            graph_line[[select_options["x_axis"], select_options["y_axis"]]]
            .to_numpy()
            .tolist()
        )
        expdata.append(element)

    retVal = {
        "elements": expdata,
        "x_axis": select_options["x_axis"],
        "y_axis": select_options["y_axis"],
        "y_min": float(Y_MIN),
        "y_max": float(Y_MAX),
        "x_min": float(X_MIN),
        "x_max": float(X_MAX),
        "parameters": parameters,
    }
    return retVal
