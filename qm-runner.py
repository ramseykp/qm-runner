from ast import Store
import os
import re
import subprocess
import argparse 

# CameraType
camera_types = ['LWIR', 'RGB', 'NIR', 'SWIR', 'MWIR', 'UV', 'Thermal_Composite', 'LNV', 'LVU', 'RGBN', 'RGBU', 'MWIR_LWIR', 'FLRGB']
# Output_Type
output_types = ['8-bit_Linear', '8-bit_Enhanced', '16-bit', 'Hotspot_Highlight', 'NIROPS_Ortho', 'NIROPS_Color', 'Oil_On_Water', '8-bit_Linear_eNUC', '16-bit_eNUC', 'NIReRGB', 'Temperature']
# File_Format
file_formats = ['GeoTIFF', 'VRT', 'SuperOverlay_KML', 'SuperOverlay_KMZ']
# Geocorrection_Level
geocorrection_levels = ['Best', 'Fastest', 'Best']
# Resolution
resolutions = ['Auto', 'Full', 'Auto', '1_meter', '2_meter', '3_meter', '5_meter', '10_meter', '15_meter', '30_meter']

def parse_cmd_line():
    # Parse the command line for the arguments
    parser = argparse.ArgumentParser(
        description='runs QuickMosaic on all Flight Folders specified in the --dir argument')

    parser.add_argument('-d', '--dir', required=True, help='Specify the directory containing the flight folders')
    parser.add_argument('-c', '--camera-type', default='LWIR', choices=camera_types,
                        help='Specify the camera type (choose from {})'.format(', '.join(camera_types)))
    parser.add_argument('-o', '--output-type', default='8-bit_Linear', choices=output_types,
                        help='Specify the output type (choose from {})'.format(', '.join(output_types)))
    parser.add_argument('-f', '--file-format', default='GeoTIFF', choices=file_formats,
                        help='Specify the file format (choose from {})'.format(', '.join(file_formats)))
    parser.add_argument('-g', '--geocorrection-level', default='Best', choices=geocorrection_levels,
                        help='Specify the geocorrection level (choose from {})'.format(', '.join(geocorrection_levels)))
    parser.add_argument('-r', '--resolution', default='Auto', choices=resolutions,
                        help='Specify the resolution (choose from {})'.format(', '.join(resolutions)))

    # Add the help option
   # parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    return parser.parse_args()

def get_version():
    version = str(subprocess.check_output(["/var/SmartStorage/bin/GetVersion"]).strip(), "utf-8")
    return version

def clean_metadata(dir):
    for cam_type in cams:
        full_res_folder = cam_type + '_FullRes'
        flight_path = os.path.join(dir, full_res_folder)
        if os.path.exists(flight_path):
            remove_snapped = ' rm -rf ' + flight_path + '/*snapped*.csv'
            remove_regd = ' rm -rf ' + flight_path + '/*Reg_*.csv'
            print( flight_path + 'exists removing metadata! with following calls' )
            print( remove_regd )
            print( remove_snapped)
            subprocess.check_call([remove_snapped], shell=True,
                                  stderr=subprocess.STDOUT)
            subprocess.check_call([remove_regd], shell=True,
                                  stderr=subprocess.STDOUT)


def clean_reg_data(dir):
    remove_reg_files = ' rm -rf ' + dir + '/*_Registration*.csv'
    subprocess.check_call([remove_reg_files], shell=True, stderr=subprocess.STDOUT)

def LogError(error):
    file_path = os.path.expanduser('~/qm_runner_errors.txt')
    with open(file_path, "a") as file_object:
        file_object.write(error)
        file_object.write('\n')

def RunCmd(cmd):
    try:
        print(cmd)
        subprocess.check_call(
            [cmd], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print("error executing: " + cmd + " return code = " + str(err.returncode))
        LogError("error executing: " + cmd + " return code = " + str(err.returncode))

def RunQuickMosaic(self, flight_dir, camera_type, output_type):
    complete_flight_dir = flight_dir
    Dir = complete_flight_dir + '/LWIR_FullRes'
    camera_type = 'LWIR'
    print('run qm testinf flight dir = ' + Dir)

    if os.path.exists(Dir):
        print('-----------Calling QuickMosaic on ' + camera_type + ' 8-bit_Linear ' + self.geo_corr )
        cmd = Store.perm + '/var/SmartStorage/bin/QuickMosaic' + ' ' + complete_flight_dir + store.cam_call_2 + \
            camera_type + ' Output_Type 8-bit_Linear Geocorrection_Level ' + self.geo_corr + ' File_Format SuperOverlay_KMZ' + \
                self.getQMLog(complete_flight_dir)
        self.RunCmd(cmd)

def getAllFlightFolders(parent_folder):
    pattern = r'^Flight_\d{4}.*$'
    flight_folders = []
    for folder in os.listdir(parent_folder):
        if os.path.isdir(os.path.join(parent_folder, folder)):
            if re.match(pattern, folder):
                flight_folders.append(folder)
    return flight_folders

def getOptions():
    args = parse_cmd_line()
    cmd_string = ' CameraType ' + args.camera_type + ' Output_Type ' + args.output_type + ' File_Format ' + args.file_format + ' Geocorrection_Level ' + args.geocorrection_level + ' Resolution ' + args.resolution
    return cmd_string

def runQuickMosaicOnAllFlights(parent_folder):
    #version = get_version()
    #print('QuickMosaic version: ' + version)
    for flight_folder in getAllFlightFolders(parent_folder):
        flight_dir = os.path.join(parent_folder, flight_folder)
        #clean_metadata(flight_dir)
        #clean_reg_data(flight_dir)
        print(flight_dir)
        qm_cmd = '/var/SmartStorage/bin/QuickMosaic ' + flight_dir + getOptions()
        RunCmd(qm_cmd)


def main():
    args = parse_cmd_line()
    runQuickMosaicOnAllFlights(args.dir)

if __name__ == '__main__':
    main()