# predictive-homeassistant

## Pre-Conditions
* Homeassistant
* External Postgres DB
* Python installed

## Use Case
This piece of software should grep data of the Home Assistant Database and puts it into a CSV file that it could be used as learning data
for a regression prediction model. In order to archive this, you could specify one target entity. This software will check the
state changes and add to it the states of the other specified entities at this point of time.

### Cleaning data

Missing is:
* Events on nearly the same time should be merged
* Feature with missing state before should be removed
### Feature

## Example Arguments
--name homeassistant_db --host 192.0.0.2 --user username --pass xxx --port 5432 --start 2023-12-05-15:30:00 --end 2023-12-21-18:30:00 --entities binary_sensor.badezimmer_motion light.badschrabklampe input_boolean.sleeping

The Arguments --start and --end are optional, if they are not provided the tool will use all available data.