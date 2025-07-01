
# Vehicle Signal Simulation with KUKSA Data Broker

This guide explains how to set up and connect the **KUKSA Data Broker** with the **VSS Simulation Application** for simulating and interacting with Vehicle Signals.

---

## Prerequisites

- Docker installed and running
- VSS Simulation Application installed
- Internet connection to pull KUKSA images

---

## Steps to Connect Simulation App to KUKSA Data Broker

### 1. Start the KUKSA Data Broker

Run the following command to start the KUKSA Data Broker on your machine:

```bash
docker run -it --rm -p 55555:55555 ghcr.io/eclipse-kuksa/kuksa-databroker:main
```

After running the above command, the Data Broker will be accessible at:

```
127.0.0.1:55555
```

This IP and port will be used to connect the Simulation App to the Data Broker.

---

### 2. Start the VSS Simulation Application

- Launch the **VSS Simulation App**.
- Go to the **Data Broker** tab within the application.
- Click the **Connect** button.

A new window will appear prompting you to enter:

- **IP Address:** `127.0.0.1`
- **Port:** `55555`

After entering the details, click **Connect**.

---

### 3. Verify Connection & Simulate Signals

Once connected successfully:

✅ You will see a dropdown containing the list of available VSS signals.  
✅ Select any signal from the dropdown.  
✅ The respective signal information and input UI will be displayed.  
✅ Enter a value for the signal.  
✅ Click the **Send Signal** button to transmit the signal to the Data Broker.  

---

## 4. (Optional) Verify Using KUKSA Data Broker CLI

To independently send and receive VSS signal data for verification, run:

```bash
docker run -it --rm --net=host ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 127.0.0.1:55555
```

This CLI provides a way to:

- Read signals
- Write signals
- Confirm data exchange between the Simulation App and the Data Broker

---

## Notes

- Ensure that the Data Broker is running **before** attempting to connect the Simulation App.
- The provided setup uses `127.0.0.1` assuming both the Data Broker and Simulation App run on the same machine. Adjust the IP if running across different machines.

---

## Troubleshooting

| Issue             | Possible Solution                                      |
|-------------------|-------------------------------------------------------|
| Connection Failed | Ensure no firewall is blocking port `55555`.          |
| No Signals Listed | Check that the Data Broker started without errors.    |
| CLI Errors        | Verify the correct IP and port are provided to the CLI.|

---

## References

- [KUKSA Data Broker GitHub](https://github.com/eclipse/kuksa-databroker)
- [KUKSA CLI GitHub](https://github.com/eclipse/kuksa-databroker-cli)

---
