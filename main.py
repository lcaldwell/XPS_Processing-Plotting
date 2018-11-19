from XPSProcessing import XPSDataSet
from plotting import Plot_Comparison

def Make_Comparison_Plot(file_names, normalisations, legend_names, scan_types, output_file_name, colours=None):
    if not len(file_names) == len(normalisations) == len(legend_names):
        raise Exception

    # Make empty lists for each plot
    data = [[] for i in range(len(scan_types))]

    for i in range(len(file_names)):
        file_name = file_names[i]
        normalisation = normalisations[i]
        dataset = XPSDataSet(file_name)
        for j in range(len(scan_types)):
            data[j].append(dataset.get_scan_data(scan_types[j], normalisation))

    Plot_Comparison(data, scan_types, legend_names, output_file_name)
    
