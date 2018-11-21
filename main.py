from XPSProcessing import XPSDataSet
from plotting import Plot_Comparison

def Make_Comparison_Plot(file_names, normalisation_type, legend_names, scan_types, output_file_name, colours=None):
    if not len(file_names) == len(legend_names):
        raise Exception

    # Make empty lists for each plot
    data = [[] for i in range(len(scan_types))]

    for i in range(len(file_names)):
        file_name = file_names[i]
        dataset = XPSDataSet(file_name)
        for j in range(len(scan_types)):
            data[j].append(dataset.get_scan_data(scan_types[j], normalisation_type))

    Plot_Comparison(data, scan_types, legend_names, output_file_name)

def Make_Multiple_Comparison_Plot(files, normalisation_list, legend_names, scan_types, output_file_names):
    for i in range(len(normalisation_list)):
        Make_Comparison_Plot(files, normalisation_list[i], legend_names, scan_types, output_file_names + str(normalisation_list[i]) + '.pdf')
    
