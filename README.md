<div align="center">
<img src="media/pollin-cam-sticker.png" style="width: 400px; height: auto;">
</div>

# Autonomous plant-pollinator camera trap for research

This repo contains the code to standup a prototype plant-pollinator camera trap for remote, field-based surveys of pollinator visitation to wild or cultivated plants and other related research. 

# Components and build instructions

| Component | Description | Documentation |
| :---- | :---- | :---- |
| **1\.** Raspberry Pi Zero 2W | Microcontroller that manages camera imaging and environmental sensors | n/a |
| **2\.** MakerSpot USB hub | Multi-port USB hub for thumb drive and camera interface | n/a |
| **3\.** WittyPi 4 Mini RTC | Real-time clock that controls scheduled startup and shutdown | [Link to documentation](https://www.uugear.com/doc/WittyPi4Mini_UserManual.pdf) |
| **4\.** USB thumb drive | External drive for image storage | n/a |
| **5\.** Arducam IMX219 camera | Autofocus camera unit for imaging bumble bees visiting the trap | [Link to documentation](https://www.uctronics.com/download/Amazon/B029201_Maunal.pdf%20)  |
| **6\.** DHT22 temp/humid sensor | Temperature/humidity sensor for environmental conditions at the trap | n/a |
| **7\.** Voltaic V75 + panel | Solar-fed battery to power camera trap | | 
| **8\.** Outdoor junction box | Waterproof housing for battery and Pi. | | 


# Raspberry Pi setup and configuration
Prototype trap deployed | Trap imaging surface
:-------------------------:|:-------------------------:
<img src="media/camera-trap1.jpg" height="500"> |  <img src="media/camera-trap2.jpeg" height="500">

## 1. Physical setup 🏗️
1. Solder (or use hammer-header) GPIO pin header to the Pi.
2. Attach stacking header and then Witty Pi 4 mini on top of that
3. Mount the USB hub, ensuring the Pogo pins are correctly aligned (see [here](https://makerspot.com/stackable-usb-hub-for-raspberry-pi-zero/) for instructions.
4. Plug in the USB thumb drive to any of the USB ports on the hub.

## 2. Operating system
### Imaging MicroSD card
Use the Raspberry Pi Imager software to install the recommended operating system for the Raspberry Pi Zero 2W on the microSD card, but opt for the *32-bit* version of Debian Trixie for this particular iteration of the camera trap to save memory.

For customizations, you will need to define:

1. Hostname: use `pollincam-XX` Replace the `XX` with the next sequence of defined in the lab pi asset tracking spreadsheet.
2. Username: use `ibuglab`
3. Password: use standard lab password for devices (see asset tracking spreadsheet)
4. WiFi network: use either personal hotspot or local network that you have full access to (we can later swap to Eduroam or other networks). If neither hotspot or local network is available, leave blank for now and manually configure using keyboard/mouse/monitor after completing the rest of this guide.
5. Enable SSH using password authentication (this is to enable remote access using the device password above)
6. Enable Raspberry Pi Connect (additional remote access capabilities including screen sharing). You will need to open and sign in to our lab's Raspberry Pi connect account in order to obtain the authentication token. Account details are in the iBUG Pi asset spreadsheet.

##  3. Updates and software 💿
### Updates and dependency installation
Once the microSD card is flashed with the OS, install it in the Pi and boot it up. If the Pi is auto-connecting to available hotspot or wifi, login to Raspberry Pi Connect and then login to the device using a remote shell connection (i.e., terminal window). If the device is not on the network, use a keyboard/mouse and monitor to open a terminal window and execute the following:

```bash
sudo apt update
sudo apt upgrade
```
Accept upgrade installations and wait for the device to update fully. This may take 5-15 minutes. Once complete, `sudo reboot` to reboot the Pi. Once the Pi has rebooted, open a terminal and then install the requisite programs/packages needed:

```bash
# GUI for managing disk devices/partitions
# Install this first
sudo apt-get install gparted

# Then run this section of code
sudo apt install -y \
python3-flask \
python3-numpy \
v4l-utils \
python3-opencv
```
## 4. Clone Github repository to the Pi
Now we'll clone this repo to the Pi so that we have the requisite scripts to test and run both the DHT22 sensor (`dht22.py`) and camera trap script (`pollincam.py`).

```bash
git clone https://github.com/ibug-lab/pollin-cam.git
```

Once cloned, we'll need to adjust the file paths in both the `dht22.py` and `pollincam.py` scripts. Open then using `nano` and adjust the file paths to the directory we just created above, should be something like: `/home/ibuglab/pollincam-01"

This will create a directory (folder) inside our home folder called `pollin-cam` where our scripts will be housed. 

## 5. Witty Pi 4 mini configuration 🔋

```bash
wget https://www.uugear.com/repo/WittyPi4/install.sh
sudo sh install.sh
```

After the installation, the installer will prompt you to reboot the pi. Do so, and then we'll setup the web interface to adjust the schedule for startup/shutdown. 

```bash
sudo /home/ibuglab/uwi/diagnose.sh
```

This will configure the web interface and provide the URL to access the Witty Pi device and enter the scheduling information. When you first open the web UI, it will show an error that the witty pi software can't be found. This is because the configuration file has the incorrect username specified for our pi. To fix this, we'll open up that file, and replace "pi" in the file paths with "ibug". Run the following line, and then replace pi in the filepath with ibuglab in the 5 last lines of that configuration file. 

```bash
nano /home/ibuglab/uwi/uwi.conf
```

Return the to web interface and refresh. THe error should go away! Now that you have accessed the Witty Pi UI, select "Schedule Script" and paste in:

```
# Define start and end to schedule
BEGIN 2026-06-01 06:00:00
END   2035-12-31 20:00:00

ON  H14
OFF H10 

```

Click save, and then refresh the UI. You should now see the `Next Shutdown` and `Next Startup` with a time of 20:00 of the current day (for Next Shutdown) and 06:00 for the next day (for Next Startup). 

Next, set the low voltage setting to 3V. This ensures that the Pi gracefully shuts down if/when the battery is drained and voltage begins to drop. 

If the web interface isn't working, you can edit the schedule and adjust the low voltage setting using the terminal. First, we'll move our schedule file from our Github repo folder to the schedules folder inside our WittyPi:

```bash
mv /home/ibuglab/pollin-cam/all_day_0600_2000.wpi /home/ibuglab/wittypi/schedules/
```

Next, open up the `wittyPi.sh` file:

```bash
nano /home/ibuglab/wittypi/wittyPi.sh
```

This will open an interactive terminal menu that you can navigate. Start by Synchronizing with network time (option 3), and then select "5. Choose schedule script". This will bring up a list of schedule scripts, and you should see the `all_day_0600_2000.wpi` file that we moved in. Select that script. It should load it, and configure the next startup and shutdown date and time. Double check that the next shutdown is today at 20:00 (8pm), and the next startup is tomorrow at 06:00 (6am). Next, select  "6. Set low voltage threshold". Enter 3 as the low voltage and save. You cna then exit (option 13). The WittyPi is now configured!

## 6. External hard drive configuration (USB thumb-drive) 💽
### Using Gparted
Launch screen sharing to the device via Raspberry Pi Connect. Under the Pi menu, go to System Tools and launch "GParted". From here, select the external drive from the dropdown in the upper right, and then select the partition. Go to partition --> unmount and then partition --> delete partition. Then, partition --> create partitition. Keep all the default settings and only enter the label, which should be the device name (e.g., `pollincam-01`). Once you're done with that, go to edit --> apply all operations. This will take a few minutes to create the new partition table on the device. 

Next, we'll create the mounting point for the hard drive. Adjust the directory name below to match the device name (e.g., `pollincam-04`)

```bash
mkdir pollincam-XX
```

We'll now add the hard drive to the file system table (fstab). Run the following code, and copy the UUID for the hard drive we just partitioned.

```bash
sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL
```

Next, open the fstab file and add the hard drive... 

```bash
sudo nano /etc/fstab
```
At the end of this file, add 

```bash
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /home/ibuglab/pollincam-XX ext4 defaults,auto,users,rw,nofail 0 0
```
replacing both the UUID with the one you just copied, and adjusting the file path to the directory we just created (i.e., replace `pollincam-xx` with the correct name, e.g., `pollincam-04`)

Next, we'll mount the drive:

```bash
sudo mount -a
```

And finally, update the folder permissions so that we can read and write. Adjust the directory name in each of these to match the device:

```bash
sudo chown ibuglab:ibuglab -R /home/ibuglab/pollincam-XX/
sudo chmod a+rwx /home/ibuglab/pollincam-XX/
sudo chmod -R 775 /home/ibuglab/pollincam-XX/
```

## 7. DHT22 configuration 🌡️
The DHT22 is a temperature/humidity sensor to record environmental conditions at the trap. To configure it, first ensure that the sensor is correctly installed on the GPIO pins of the Pi (see diagram below). 

<div align="center">
<img src="media/pi-dht.png" style="width: 400px; height: auto;">
</div>

Open a terminal and install the necessary dependencies and initialize a python virtual environment to run the `dht22.py` script. 

```bash
sudo apt install -y \
python3-venv \
python3-dev \
build-essential \
swig \
liblgpio-dev
```

Next, we'll adjust the raspberry pi configuration file to tell it which GPIO pin we're using. This is key as the WittyPi uses the default 1-wire pin.

```bash
sudo nano /boot/firmware/config.txt
```

To the end of this file, add:

```bash
dtoverlay=w1-gpio,gpiopin=27
```

Save and exit.

Next, we'll create a virtual environment to run the script, install the packages that talk to the sensor, and test that it's working:

```bash
# this creates a virtual environment to run the script:
python3 -m venv /home/ibuglab/dht-env
source /home/ibuglab/dht-env/bin/activate

# this installs a few packages to talk to the sensor
pip install lgpio
pip install adafruit-blinka
pip install adafruit-circuitpython-dht

# this runs the script to test if the sensor is working
python /home/ibuglab/pollin-cam/dht22.py # this starts the script
```

If the terminal is reading out temperatures and humidities that make sense, great -- it's working! You can exit the script by entering `cntl+c`. 

## 8. Setup CRONTAB events for all camera trap scripts 📅
Using the Witty Pi will start up and shutdown the Pi automatically to save on battery overnight. Because of this, we'll need to configure our Pi to automatically start our camera trap and temperature/humidity sensor script automatically each time the Pi boots up in the morning. For this, we'll use crontab, which is a job scheduler.

```
crontab -e

# add this line to start the scripts after reboot with a 60 second delay
@reboot sleep 60 && /home/ibuglab/dht-env/venv/bin/python /home/ibuglab/pollincam/dht22.py
@reboot sleep 60 && /usr/bin/python3 /home/ibuglab/pollin-cam/pollincam.py
```

Save and exit the crontab. Our scripts are successfully scheduled to startup as soon as the Pi boots up in the morning (+ a 1 minute delay to ensure the device unit boots).  
