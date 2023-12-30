# predictive-homeassistant

## Pre-Conditions
* Homeassistant
* External Postgres DB
* Python installed

## Use Case
This piece of software should grep data of the Home Assistant Database and puts it into a CSV file that it could be used as learning data
for a regression prediction model. In order to archive this, you could specify one target entity. This software will check the
state changes and add to it the states of the other specified entities at this point of time.

## Feature Generation

### Cleaning data
The AI needs to have his inout data in numbers. For this the following transformations are done:
* Off -> 0
* On -> 1

Missing steps are:
* Events on nearly the same time should be merged
* Feature with missing state before should be removed

### Feature itself
The features could be generated automatically with the use of the arg parameters.
The following options you have:
* State of the target entity
* Minute of the day of target entity state change
* Other states of entity at this point of time
* The time delta in seconds between the target entity state change an the related other entity 

## Example Arguments
--database homeassistant_db --host 192.168.0.2 --user myusername --pass xxx --port 5432 --start 2023-12-21-16:05:00 --end 2023-12-21-16:35:00 --entities light.badschrabklampe sensor.badezimmer_light_level --minute_of_day 1 --entities_time_delta binary_sensor.badezimmer_motion

### --start and --end 
These are optional, if they are not provided the tool will use all available data.

### --entities
The first entity here is the target one. Of all following, the state is added to the feature. 

### --entities_time_delta
Is also optional. When you define here an entity it is used in the feature with the related state but also the seconds between
the state of the target entity and the defined one in this list

### --minutes_of_day
This parameter defines if the minute of the target entity state change should be added
* 0 for no
* 1 for yes