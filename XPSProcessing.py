# Abbreviations - to aid in readability here is a list of all
# abbreviations used in variable/method names
#
# BE - Binding Energy

import pandas as pd

RANGES_FOR_AVERAGING = {
    'Survey': (-10, 0),
    'C1s Scan': (280, 282),
    'O1s Scan': (521, 523),
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
        peaks_frame = self.file.parse('Peak Table', header=1)
        return (peaks_frame['Peak BE'] - C_PEAK_BE).abs().min()

    def get_scan_data(self, scan_name):
        scan = ElementScan(self.file, scan_name)
        return scan


class ElementScan:
    plot_upper_limit = 0
    plot_lower_limit = 0

    def __init__(self, file, scan_name):
        self.file = file
        self.scan_name = scan_name
        self.data = self.process_sheet()

    def process_sheet(self):
        # column names are on row 13
        header_row = 13

        frame = self.file.parse(sheet_name=self.scan_name, header=header_row)
        # drop columns 1 and 3 because they are always empty
        frame = frame.drop([frame.columns[1], frame.columns[3]], axis=1)

        # name column which contains raw data (has no header in excel file)
        frame.rename(columns={'Unnamed: 2': 'Raw'}, inplace=True)

        # drop first row (just defines units which are all the same)
        frame.drop(0, axis=0, inplace=True)

        return frame

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
        y_shift = self.data['Raw'][mask].mean()

        return y_shift
