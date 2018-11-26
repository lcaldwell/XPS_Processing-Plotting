# Abbreviations - to aid in readability here is a list of all
# abbreviations used in variable/method names
#
# BE - Binding Energy

import pandas as pd

RANGES_FOR_AVERAGING = {
    'Survey': (-10, 0),
    'C1s Scan': (280, 282),
    'O1s Scan': (525, 526.5),
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

# Binding energy of various peaks
C1s_PEAK_BE = 285
O1s_PEAK_BE = 530




class XPSDataSet:
    def __init__(self, filename):
        self.file = pd.ExcelFile(filename)
        self.BE_shift = self.get_BE_shift()

    def get_BE_shift(self):
        peaks_frame = self.get_cropped_peaks_sheet()
        peaks_column = peaks_frame['Peak BE']
        return (peaks_column - C1s_PEAK_BE).abs().min()

    def get_scan_data(self, scan_name, normalisation_type):
        scan = ElementScan(self, scan_name)
        normalisation = self.get_normalisation(normalisation_type)
        print(normalisation)
        return scan.get_scan_data(normalisation)

    def get_fit_data(self, scan_name, normalisation_type):
        scan = ElementScan(self, scan_name)
        normalisation = self.get_normalisation(normalisation_type)
        fit_names = scan.get_fit_names()
        fits_data = []
        for fit_name in fit_names:
            fits_data.append(scan.get_fit_data(fit_name, normalisation))
        return fits_data
    
    def get_envelope_data(self, scan_name, normalisation_type):
        scan = ElementScan(self, scan_name)
        normalisation = self.get_normalisation(normalisation_type)
        return scan.get_envelope_data(normalisation)

    def get_normalisation(self, normalisation_type):
        peaks_frame = self.get_cropped_peaks_sheet()
        name_column = peaks_frame['Name ']
        area_column = peaks_frame['Area (P) CPS.eV']
        peak_centres_column = peaks_frame['Peak BE']
        if normalisation_type == 'TC_OCFe':
            # Include all peaks of O, C and Fe
            matches = name_column.str.contains(r'^(?:O|C|Fe)\d')
        elif normalisation_type == 'Fe':
            # Include all peaks of Fe
            matches = name_column.str.contains(r'^Fe\d')
        elif normalisation_type == 'C-C':
            distances = (peak_centres_column - C1s_PEAK_BE).abs()
            matches = (distances == distances.min())
        elif normalisation_type == 'M-O':
            distances = (peak_centres_column - O1s_PEAK_BE).abs()
            matches = (distances == distances.min()) 
        else:
            raise Exception("normalisation_type not recognised")
        return area_column[matches].sum()

    def get_cropped_peaks_sheet(self):
        peaks_frame = self.file.parse('Peak Table', header=1)
        peak_centre_column = peaks_frame['Peak BE']
        list_of_nans = peak_centre_column.isna()
        if list_of_nans.values.any():
            final_peak_index = peak_centre_column.index[list_of_nans][0]
        else:
            final_peak_index = len(peak_centre_column)
        return peaks_frame.iloc[:final_peak_index,:]
 


class ElementScan:
    plot_upper_limit = 0
    plot_lower_limit = 0

    def __init__(self, parent_scan, scan_name):
        self.parent_scan = parent_scan
        self.scan_name = scan_name
        self.data = self.preprocess_sheet()
        self.shift_BEs()

    def preprocess_sheet(self):
        # column names are on row 13
        header_row = 13

        frame = self.parent_scan.file.parse(sheet_name=self.scan_name, header=header_row)
        # drop columns 1 and 3 because they are always empty
        frame = frame.drop([frame.columns[1], frame.columns[3]], axis=1)

        # name column which contains raw data (has no header in excel file)
        frame.rename(columns={'Unnamed: 2': 'Raw'}, inplace=True)

        # drop first row (just defines units which are all the same)
        frame.drop(0, axis=0, inplace=True)

        # drop any remaining unnamed columns
        frame = frame.iloc[:, ~frame.columns.str.contains(r'^Unnamed: \d+')]

        return frame

    def get_fit_names(self):
        NON_FIT_NAMES = ['Binding Energy (E)', 'Raw', 'Envelope', 'Residuals']
        column_names = self.data.columns
        fit_names = [x for x in column_names if not x in NON_FIT_NAMES]
        return fit_names

    def process_data(self, name, normalisation):
        df = self.crop_data_to_plot_range()
        unshifted_y_series = df[name]
        y_shift = self.calculate_y_shift()
        shifted_y_series = unshifted_y_series.subtract(y_shift)
        normalised_y_series = shifted_y_series.multiply(1/normalisation)

        x_values = df[BE_NAME].tolist()
        y_values = normalised_y_series.tolist()
        return (x_values, y_values)

    def get_scan_data(self, normalisation):
        return self.process_data('Raw', normalisation)
        
    def get_fit_data(self, fit_name, normalisation):
        return self.process_data(fit_name, normalisation)

    def get_envelope_data(self, normalisation):
        return self.process_data('Envelope', normalisation)

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
