# Myfitnesspal custom component
This custom component gets fitnessdata from your account. Please advice that the component uses underlying scraping API:s that can change at any time and used at your own risk. **The author takes no liability of usage**.

# Usage

### Configure trough integrations (prefered way)
Check under configuration/integrations. Add the `Myfitnesspal` integration.

### Configure with old school yaml
You can setup through configuration.yaml:

```yaml
sensor:
  - platform: my_fitnesspal
    name: name                # The name of sensor
    username: my_username     # Your user name at myfitnesspal
    password: my_password     # Your password
```

### Configuration properties
|property|description|
|---|---|
|name|Name of sensor
|username|Your user name at myfitnesspal
|password|Your password at myfitnesspal
|   |   |

