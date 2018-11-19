import matplotlib
matplotlib.use("TkAgg") # Fixes some weird error
from matplotlib import pyplot as plt


def Plot_Comparison(data, plot_names, legend_names, output_file_name):
    num_plots = len(data)
    fig, ax = plt.subplots(1,num_plots)
    if num_plots == 1: ax = [ax]
    for i in range(len(data)):
        ax[i].set_title(plot_names[i])
        sub_plot_data = data[i]
        for j in range(len(sub_plot_data)):
            x_max = max(sub_plot_data[j][0])
            x_min = min(sub_plot_data[j][0])
            ax[i].set_xlim(x_max, x_min)
            ax[i].plot(*sub_plot_data[j], label=legend_names[j])
            ax[i].legend(loc='upper left', prop={'size': 6})

    
    fig.savefig(output_file_name)



