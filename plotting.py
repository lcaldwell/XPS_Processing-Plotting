import matplotlib
matplotlib.use("TkAgg") # Fixes some weird error
from matplotlib import pyplot as plt


def Plot_Comparison(data, plot_names, legend_names, output_file_name):
    num_plots = len(data)
    fig, ax = plt.subplots(1,num_plots, figsize=(7,3))
    if num_plots == 1: ax = [ax]
    for i in range(len(data)):
        ax[i].set_title(plot_names[i])
        sub_plot_data = data[i]
        for j in range(len(sub_plot_data)):
            ax[i].plot(*sub_plot_data[j], label=legend_names[j])

        x_max = max(sub_plot_data[0][0])
        x_min = min(sub_plot_data[0][0])
        ax[i].set_xlim(x_max, x_min)
        ax[i].legend(loc='upper left', prop={'size': 6})
        ax[i].set_yticks([])
        ax[i].set_xlabel('Binding Energy (eV)')

    plt.tight_layout()
    fig.savefig(output_file_name)


def Plot_Fits(data, fits, envelopes, plot_names, output_file_name):
    num_plots = len(data)
    fig, ax = plt.subplots(1, num_plots, figsize=(7,3))
    if num_plots == 1: ax = [ax]
    for i in range(len(data)):
        ax[i].set_title(plot_names[i])
        sub_plot_data = data[i]
        sub_plot_fits = fits[i]
        sub_plot_envelope = envelopes[i]
        ax[i].scatter(*sub_plot_data, s=2)
        if not sub_plot_envelope is None:
            ax[i].plot(*sub_plot_envelope)
        if not sub_plot_fits is None:
            for j in range(len(sub_plot_fits)):
                ax[i].plot(*sub_plot_fits[j])

        x_max = max(sub_plot_data[0])
        x_min = min(sub_plot_data[0])
        ax[i].set_xlim(x_max, x_min)
        ax[i].set_yticks([])
        ax[i].set_xlabel('Binding Energy (eV)')

    plt.tight_layout()
    fig.savefig(output_file_name)