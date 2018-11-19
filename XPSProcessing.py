# Abbreviations - to aid in readability here is a list of all
# abbreviations used in variable/method names
#
# BE - Binding Energy

import pandas as pd

RANGES_FOR_AVERAGING = {
    'Survey': (-10, 0),
    'C1s Scan': (280, 282),
    'O1s Scan': (523, 525),
    'Fe2p Scan': (700, 702),
    'Si2p Scan': (95, 96)
}

RANGES_FOR_PLOTTING = {
    'Survey': (0, 1300),
    'C1s Scan': (281, 292),
    'O1s Scan': (525, 540),
    'Fe2p Scan': (700, 740),
    'Si2p Scan': (95, 107)
}

# Name for Binding Energy column
BE_NAME = 'Binding Energy (E)'

# Binding energy of C peak to shift values by
C_PEAK_BE = 285


class XPSDataSet:
    def __init__(self, filename):
        self.file = pd.ExcelFile(filename)
        self.BE_shift = self.get_BE_shift()

    def get_BE_shift(self):
        # Some files have more entries into columns under what we are interested
        # in, this code only includes entries in 'Peak BE' column up to first
        # nan value
        peaks_frame = self.file.parse('Peak Table', header=1)
        peaks_column = peaks_frame['Peak BE']
        list_of_nans = peaks_column.isna()
        if list_of_nans.values.any():
            final_peak_index = peaks_column.index[list_of_nans][0] - 1
        else:
            final_peak_index = len(peaks_column)
        return (peaks_column[:final_peak_index] - C_PEAK_BE).abs().min()

    def get_scan_data(self, scan_name, normalisation):
        scan = ElementScan(self, scan_name)
        return scan.get_scan_data(normalisation)


class ElementScan:
    plot_upper_limit = 0
    plot_lower_limit = 0

    def __init__(self, parent_scan, scan_name):
        self.parent_scan = parent_scan
        self.scan_name = scan_name
        self.data = self.process_sheet()
        self.shift_BEs()

    def process_sheet(self):
        # column names are on row 13
        header_row = 13

        frame = self.parent_scan.file.parse(sheet_name=self.scan_name, header=header_row)
        # drop columns 1 and 3 because they are always empty
        frame = frame.drop([frame.columns[1], frame.columns[3]], axis=1)

        # name column which contains raw data (has no header in excel file)
        frame.rename(columns={'Unnamed: 2': 'Raw'}, inplace=True)

        # drop first row (just defines units which are all the same)
        frame.drop(0, axis=0, inplace=True)

        return frame

    def get_scan_data(self, normalisation):
        df = self.crop_data_to_plot_range()
        unshifted_y_series = df['Raw']
        y_shift = self.calculate_y_shift()
        shifted_y_series = unshifted_y_series.subtract(y_shift)
        normalised_y_series = shifted_y_series.multiply(1/normalisation)

        x_values = df[BE_NAME].tolist()
        y_values = normalised_y_series.tolist()
        return (x_values, y_values)

    def shift_BEs(self):
        BE_shift = self.parent_scan.BE_shift
        self.data[BE_NAME].subtract(BE_shift)

    def crop_data_to_plot_range(self):
        plot_range = RANGES_FOR_PLOTTING[self.scan_name]
        mask = (self.data[BE_NAME] > plot_range[0]) & (
            self.data[BE_NAME] < plot_range[1])
        cropped_data = self.data[mask]

        return cropped_data

    def calculate_y_shift(self):
        av_range = RANGES_FOR_AVERAGING[self.scan_name]
        mask = (self.data[BE_NAME] > av_range[0]) & (
            self.data[BE_NAME] < av_range[1])
        if not mask.values.any(): 
            raise Exception('No values between range specified for y shift')
        y_shift = self.data['Raw'][mask].mean()

        return y_shift
