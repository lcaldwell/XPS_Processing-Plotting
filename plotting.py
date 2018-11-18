import matplotlib
matplotlib.use("TkAgg") # Fixes some weird error
from matplotlib import pyplot as plt


def Plot_Comparison(data, plot_names, output_file_name):
    num_plots = len(data)
    fig, ax = plt.subplots(1,num_plots)
    if num_plots == 1: ax = [ax]
    for i in range(len(data)):
        ax[i].set_title(plot_names[i])
        sub_plot_data = data[i]
        for j in range(len(sub_plot_data)):
            ax[i].plot(*sub_plot_data[j])

    
    fig.savefig(output_file_name)



