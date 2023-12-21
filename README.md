# predictive-homeassistant

## Pre-Conditions
* Homeassistant
* External Postgres DB
* Python installed

## Use Case
This piece of software should grep data of the Home Assistant Database and prepare it own a way that it could be processed
by TensorFlow.

## Example Arguments
--name homeassistant_db --host 192.0.0.2 --user username --pass xxx --port 5432 --start 2023-12-05-15:30:00 --end 2023-12-21-18:30:00 --entities binary_sensor.badezimmer_motion light.badschrabklampe input_boolean.sleeping

The Arguments --start and --end are optional, if they are not provided the tool will use all available data.