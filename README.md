# IOT-MAB: Decentralized Intelligent Resource Allocation Approach for LoRaWAN Networks

## Introduction

## Installation
It is recommend to use virtualenv to keep your Python environment isolated, together with virtualenvwrapper to make working with virtual environments much more pleasant, e.g.:

```python
$ pip install virtualenvwrapper
...
$ export WORKON_HOME=~/.virtualenvs
$ mkdir -p $WORKON_HOME
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv -p python3 iot_mab
```

You can install the required packages using the provided requirements.txt file:

```python
(lorasim)$ pip install -r requirements.txt
```

## Usage

### Synopsis

```python
python3 IoT_MAB.py <nrNodes> <nrIntNodes> <nrBS> <radius> <AvgSendTime> <horizonTime>
<packetLength> <freqSet> <sfSet> <powerSet> <captureEffect> <interSFInterference> <infoMode> <logdir> <exp_name>
```

Example:

```python
python3 IoT_MAB.py --nrNodes 5 --nrIntNodes 5 --nrBS 1 --radius 2000 --AvgSendTime 360000 --horizonTime 10  --packetLength 50 --freqSet '867300' --sfSet '7 8'  --powerSet "14"  --captureEffect 1  --interSFInterference 1 --infoMode NO --logdir logs --exp_name exp1
```
### Description
NODES

number of nodes to simulate.

nrIntNODES

number of smart nodes to simulate.

BS

number of base station.

RADIUS

radius to simulate

AVGSEND

average sending interval in milliseconds.

horTime

time to simulate

packetLength

length of packet to simulate

SFSET

set of SF to simulate

FREQSET

set of frequency to simulate

POWSET

set of power to simulate

CAPTURE_EFFECT

capture effect (power collision) or not

INTER_SF_INTERFERENCE

inter-sf interference

INFO_MODE

information mode to simulate

### Output

The result of every simulation run will be appended to a file named prob..._X.csv, whereby prob..._X. The data file is then plotted into .png file by using matplotlib.