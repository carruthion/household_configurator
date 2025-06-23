# household_configurator
Simple configurator to create configurations for the ALPG.

This small GUI-based tool creates configuration files with which the [ALPG](https://github.com/utwente-energy/alpg) can generate artificial load profiles.

## Setup
It is possible to simulate realistic electric vehicles (in terms of charging power). 
This requires the `ev-data.json` file from the [OpenEV](https://github.com/chargeprice/open-ev-data) project.
If the file does not exist, it is loaded directly the first time it is called up.
Alternatively you can find it [here](https://github.com/chargeprice/open-ev-data/blob/3134cae485555ac288d01ba9b13573047bf92937/data/ev-data.json) and copy it into the repository folder.
