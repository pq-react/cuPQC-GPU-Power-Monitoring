# cuPQC-GPU-Power-Monitoring
Monitoring Nvidia GPU deploying cuPQC, Influxdb and Grafana components. This repository provides a **Dockerized GPU monitoring setup** that collects **NVIDIA GPU power draw metrics** using **Telegraf**, stores them in **InfluxDB**, and visualizes the data in **Grafana**.

## Pull and Run the  gpu-monitor Docker Container
To pull and run the container from Docker Hub:

```bash
docker pull demogoikon/gpu-monitor:latest
docker run -d --runtime=nvidia --name=gpu-monitor demogoikon/gpu-monitor
```
This pulls and starts the container with cuPQC, Telegraf, InfluxDB.

*The steps that has been followed to setup this container are described below:*

### I. Install cuPQC
cuPQC is an NVIDIA CUDA-based library for Post-Quantum Cryptography. We followed the steps below to install it inside our container.

To install the cuPQC (CUDA Post-Quantum Cryptography) library within your Docker container, follow these steps:​

Note: Initially we have ensured that our Docker container met all cuPQC requirements, including the appropriate CUDA Toolkit version and supported GPU architecture. [requirements](https://docs.nvidia.com/cuda/cupqc/requirements.html)

#### a. Download the cuPQC Package:

Visit the NVIDIA cuPQC Downloads page to obtain the latest version of the cuPQC library [current latest version]( https://developer.download.nvidia.com/compute/cupqc/redist/cupqc/cupqc-pkg-0.2.0.tar.gz).

#### b. Transfer the Package into the Docker Container:

Assuming you've downloaded the cuPQC package (cupqc-<version>.tar.gz) to your host machine, you can copy it into your running Docker container using the following command:​

``` bash
docker cp cupqc-<version>.tar.gz <container_id>:/root/
```
Replace <version> with the actual version number and <container_id> with your container's ID or name.

Ensure NVIDIA GPU support is enabled inside Docker.([Guide to Run CUDA WSL Docker](https://forums.developer.nvidia.com/t/guide-to-run-cuda-wsl-docker-with-latest-versions-21382-windows-build-470-14-nvidia/178365))

#### c. Access the Docker Container:
Enter you Docker container's shell:
``` bash
docker exec -it <container_id> /bin/bash
```
#### d. Extract the cuPQC Package:

Navigate to the directory containing the package and extract it:
``` bash
cd /root/
tar -xzf cupqc-<version>.tar.gz
```
#### e. Use Makefile to compile the examples

- Compile and link CUDA-based cuPQC examples using Nvidia's nvcc compiler using the Makefile in the 'example' - - folder. (path example: ~/cupqc/cupqc-pkg-0.2.0/example)

#### f. Now you can execute the cupqc examples:

``` bash
./example_ml_dsa
./example_ml_kem
```

### II. Installing & Configuring Telegraf

Telegraf collects GPU power draw metrics from nvidia-smi and sends them to InfluxDB.

#### Important Note:
You need first to setup a database for your data to be stored. You can follow the installation guide of [Influxdb](https://docs.influxdata.com/influxdb/v2/install/) or [CAM repository](https://github.com/pq-react/CAM---Context-Agility-Manager) to deploy a database and set telegraf configuration to send your data there.

#### a. Install Telegraf

``` bash
apt update && apt install telegraf -y
```
#### b. Edit Telegraf Configuration

- Modify the following sections:

*Data Collection Interval:*

```ini
[agent]
interval = "1s"
```

*InfluxDB Configuration:*
```ini
[[outputs.influxdb_v2]]
urls = ["http://<influxdb_IP_address>:8086"]
token = "$INFLUX_TOKEN"
organization = "<organization_name>"
bucket = "<bucket_name>"
```

*Nvidia_smi plugin enabling*

``` bash
[[inputs.nvidia_smi]]
  bin_path = "/usr/bin/nvidia-smi"
  timeout = "5s"

[[outputs.influxdb_v2]]
  urls = ["http://<influxdb_IP_adress>:8086"]
  token = "YOUR_INFLUXDB_TOKEN"
  organization = "name_of_organization"
  bucket = "name_of_bucket"
```
#### c. Restart Telegraf
``` bash
telegraf --config /etc/telegraf/telegraf.conf
```
- Now Telegraf sends GPU metrics to InfluxDB.

#### d. Configure and Run python script for gpu consumption metrics.

- The python snippet provided enables recovering Nvidia GPU's power draw.

*Update the snippet with the correct IP address, organization, bucket and token*

```python
# InfluxDB settings
INFLUXDB_URL = "http://<influxdb_IP_address>:8086/api/v2/write"
INFLUXDB_BUCKET = "<bucket_name>"
INFLUXDB_ORG = "<organization_name>"
INFLUXDB_TOKEN = "<influxdb****token>"
```

- Execute the python script included in this repository to ensure power draw metrics will appear as expected.

``` bash
python3 /root/gpu_power_monitor.py &
```

### III. Configure Grafana Data Source
- As a prerequisite you have to install and setup Grafana as described in [Grafana Documentation](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) or in step 3 of [CAM repository](https://github.com/pq-react/CAM---Context-Agility-Manager).

Launch the Grafana UI at http://<serverIP>:3000 in your browser and the following Grafana login page should greet you.

  1. Log in with the default credentials (admin / admin), and set new username and password.
  
  2. Click on the Add your first data source button.

  3. Choose “Connections → Data sources” on the side menu and click the “+ Add new data source” button.

  4. Click the InfluxDB button.

  5. On the next page, select “Flux” from the dropdown menu as the query language. Flux supports InfluxDB v2.x and is easier to set up and configure. Enter the following values:

  6. Enter the following values (example image below):

**HTTP:**
```plaintext
URL: 'http://<Influxdb_IP_Address>:8087'
```

**Auth:**

```plaintext
User: <Your_UserName>
Password: <Your_Influxdb_Password>
```

**InlfuxDB Details:**

```plaintext
Organization: <organization_name>
Token: <Influxdb_Token>
Bucket: <bucket_name>
Min time interval: 300ms
Max series: 10000
```

  7. Click the `Save and Test` button to verify the setup. The next message should be displayed.

### IV. Set up Grafana Dashboards

The next step is to set up Grafana Dashboard.

  1. Click on the button with the four squares and select “Dashboards” to open the “Import” dashboard screen. Follow the next steps and create a dashboard for each of your physical machines.

  2. From the `Import dashboard` load the provided .json file which contains the dedicated dashboard setup.

#### Important Note
- If grafana doesn't let you upload .json file then you should copy and paste the content of .json file in the `Import  via dashboard JSON model` frame and then press load.
- In the provided .json file it is assumed that the username is `localadmin` and the name of the bucket is `docker_nvidia_bucket` or `Desktop_GPU`. If otherwise please change those values in the entire .json file with the ones that match your setup.

3. In the `Dashboards` menu select the name of the imported dashboard.

You may see that every panel displays “No data”. In that case commit the following changes in order to enable the “No data” panels:

- Hover your mouse over a panel and click the right top button with the three vertical dots to expand the drop down menu and select `edit`

- Make sure that in `Data source` field is selected the name of your bucket and in the flux language code you see the correct name of your bucket, username

- Then click the “Query inspector” button and on the side menu that will appear click the “refresh” button. You should now see your metrics displayed. Exit the side menu and click “Apply” on the top right area.

- Repeat the steps above to every panel that displays “no data”

- Set the refresh rate to `300ms` to enable fast panel data updates.

