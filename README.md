# Myfitnesspal custom component
This custom component gets fitness data from your account. Please note that the component uses an underlying scraping API that can change at any time and use at your own risk. **The author takes no liability of usage**.

# Usage

## Copy and paste
*If you use HACS, skip this step!*
The component can be used by copying everything under the `custom_component` folder to your `custom_component`, i.e. the `my_fitnesspal` folder.

### Configure through integrations (prefered way)
Check under configuration/integrations. Add the `Myfitnesspal` integration.

### Configure with old school yaml
Not supported

### Configuration properties
|property|description|
|---|---|
|name|Name of sensor
|username|Your user name at myfitnesspal
|password|Your password at myfitnesspal
|   |   |


## HACS component
You can use HACS [Se this link for more information](https://github.com/custom-components/hacs). Add `https://github.com/helto4real/custom_component_myfitnesspal` to custom repository under `SETTINGS`. Select integration as type.

Configure through the integrations page or old school yaml as described above.
