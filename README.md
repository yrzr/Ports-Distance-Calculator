# Python-Ports-Distance-Calculator

Description from original author:

> A distance calculator that is able to return the distance between two ports based on the derived sea route.

> Same as the R version. The python script directly uses the raster map (cost map) I transformed by using R. The script first transform the raster map into an array. By using the route_through_array function provided by scikit-image, the least cost route was able to be derived and stored as an array for further distance calculation.

Optimized the algorithm and re-construct the code based on the original author's work, and used the UN/LOCODE dataset to extract global port information.

## usage

```bash
$ docker compose build
$ docker compose up -d
[+] Running 1/0
 ✔ Container Ports-Distance-Calculator-app-1  Running
```

or use pre-build docker image:

```bash
$ docker run -d --name ports-distance-calculator --publish 5000:5000 yrzr/ports-distance-calculator
```

Examples:

- Get port information:

```bash

$ curl "http://127.0.0.1:5000/get_port_info?code=HKGOM"
{"code":"HKGOM","function":"-----6--","latitude":22.3,"longitude":114.18333333333334,"name":"Hung Hom","name_wo_diacritics":"Hung Hom"}
```

- Calculate the distance between two ports:

```bash
$ curl -X POST http://127.0.0.1:5000/calculate_distance -H "Content-Type: application/json" -d '{ "from_code": "HKGOM", "to_code": "USZJI"}'
{"distance_km":12784.59082643056}
```

- Calculate the distance between two coordinates:

```bash
$ curl -X POST http://127.0.0.1:5000/calculate_distance -H "Content-Type: application/json" -d '{"from_longitude": 114.18333333333334, "from_latitude": 22.3, "to_longitude": -180.1, "to_latitude": 34.53333333333333}'
{"error":"Longitude must be between -180 and 180."}
```
