from datetime import datetime, timedelta
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_ROMS_native, reader_netCDF_CF_generic
import pandas as pd


# Akerselva sept 2024
# loc = 'akerselva'
# deploy_lon = 10.7469
# deploy_lat = 59.9019

# Position for Vaes
# deploy_lon = 10.503582
# deploy_lat = 59.792911

# deploy_time = datetime(2024,9,11,9,0)

# indate = deploy_time.strftime(format='%Y%m%d')


class OpendriftRunner:
    def __init__(self, model_name):
        self.model = OceanDrift()

        # Set config
        self.model.disable_vertical_motion()

        if model_name == 'fjordos':
            path = 'https://thredds.met.no/thredds/dodsC/fjordos/operational_archive_daily_agg'
            reader = reader_ROMS_native.Reader(path)
            self.model.add_reader(reader)
        elif model_name == 'norkyst160':
            path = 'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_160m_m71_be'
            reader = reader_netCDF_CF_generic.Reader(path)
            self.model.add_reader(reader)
        elif model_name == 'norkyst800':
            path = 'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_800m_m00_be'
            reader = reader_netCDF_CF_generic.Reader(path)
            self.model.add_reader(reader)

        self.buffer=0.02

    def _read_data(self, filename):
        data = pd.read_csv(filename, sep=",")
        timestamp_str = data["timestamp"].to_numpy()
        timestamps = []
        for i in range(len(timestamp_str)):
            timestamps.append(datetime.strptime(timestamp_str[i], "%Y-%m-%d %H:%M:%S.000"))
        return timestamps, data["longitude"].to_numpy(),data["latitude"].to_numpy()

    def run(self, latitude, longitude, deploy_time, data_drifter = False, file = None, total_time = 24, time_step = 5, time_step_output = 180):

        deploy_time = datetime.strptime(deploy_time, "%Y-%m-%d-%H-%M")

        # SEED ELEMENTS AT VARIOUS DEPTHS
        # AT SAME LOCATION AND TIME
        self.model.seed_elements(lon=latitude, lat=longitude, z=-0.01, radius=50, number=2000, time=deploy_time )
        self.model.seed_elements(lon=latitude, lat=longitude, z=-1, radius=50, number=2000, time=deploy_time )
        self.model.seed_elements(lon=latitude, lat=longitude, z=-3, radius=50, number=2000, time=deploy_time )

        if data_drifter:
            drifter_fn = file
            
            [drifter_times, drifter_lons, drifter_lats ] = self._read_data(drifter_fn) 
            self.drifter={'lon': drifter_lons, 'lat': drifter_lats, 'time': drifter_times, 'linewidth': 2, 'color': 'b', 'label': 'Drifter'}

        self.model.list_configspec()

        self.model.run(steps=total_time*3600/time_step, time_step=time_step, time_step_output=time_step_output)

    def output_animation(self, loc, indate):
        self.model.animation(
            color='z',
            colorbar=True,
            background=['x_sea_water_velocity', 'y_sea_water_velocity'], scale=100,
            filename='plots/anim_'+loc+'_'+indate+'.mp4',
            buffer=self.buffer,
            drifter=self.drifter,
        )

    def output_plot(self, loc, indate):
        self.model.plot(
            linecolor='z',
            buffer=self.buffer,
            show_elements=False,
            filename='plots/plot_'+loc+'_'+indate+'.png',
            drifter=self.drifter,
        )
