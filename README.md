# DCG Dependency Analyzer Generator

## Overview
The [**DCG Dependency Analyzer**](https://dcgdependencyanalyzer.vercel.app/) is a UI tool designed to analyze dependencies between various database objects in an Oracle database. It helps users understand relationships between views, procedures, functions, and other database objects. The tool is primarily intended for analyzing code object dependencies and exporting the results as JSON for visualization.

## Features
- Extracts and analyzes dependencies between Oracle database objects.
- Provides structured output to simplify relationship analysis.
- Supports filtering and searching for specific dependencies.
- Generates detailed reports for further analysis.

## Prerequisites
Before using the DCG Dependency Analyzer, ensure the following prerequisites are met:
- Python 3.x installed
- Oracle Instant Client installed
- Required Python packages installed

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/dcgadmin/dcg-codedependency-generator.git
   cd dcg-codedependency-generator
   ```
2. Install Python virtual environment:
   ```sh
   python -m venv <EnvironmentName>
   ```

3. Activate the virtual environment:
   - **Windows**:
     ```sh
     .\<EnvironmentName>\Scripts\activate
     ```
   - **Linux/Mac**:
     ```sh
     source <EnvironmentName>/bin/activate
     ```

4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

5. Set up Oracle Instant Client and configure the necessary environment variables:
   ```sh
   export ORACLE_HOME=/path/to/oracle/instant/client
   export PATH=$ORACLE_HOME:$PATH
   export LD_LIBRARY_PATH=$ORACLE_HOME
   ```

## Configuration
Update the env file (`.env`) with your Oracle database credentials:

### **1. Standard Connection**
If you are using a host-based connection, update the `.env` file as follows:
```txt
USERNAME=<<username>>
PASSWORD=<<password>>
HOST=<<host>>
PORT=<<port>>
SERVICE_NAME=<<servicename>>
```

### **2. TNS Connection**
If you are using a TNS string for connection, update the `.env` file as follows:
```txt
USERNAME=<<username>>
PASSWORD=<<password>>
TNS_STRING=<<tnsstring>>
```

## Usage
Run the script to analyze dependencies:
```sh
python3 dcganalyzer.py dependency-analyzer --help
```

### Command-line Options
| Option         | Description |
|---------------|-------------|
| `--list_objects` | Lists all objects with dependencies in the schema |
| `--object_name OBJECT_NAME` | Mentioned the object name to get the dependency details |
| `--generate_config ` | Generate Oracle dependency json file |
| `--schemaname ` | Schema name to generate dependency json |
| `--include-table ` | Include Table objects as part of Dependency, Default False |

Example:
#### List all objects in the Oracle Schema
```sh
python3 dcganalyzer.py dependency-analyzer --schemaname <<SCHEMANAME>> --list-objects

Database Objects List : ['PROCEDURE_A', 'PROCEDURE_B', 'PACKAGE_GLOBAL_VARIABLE_TEST', 'SPORT_TEAM_ID_TRG', 'PLAYER_ID_TRG', 'SPORTING_EVENT_ID_TRG', 'GENERATE_TICKETS', 'TICKETMANAGEMENT', 'SPORTING_EVENT_TICKET_INFO', 'TRIGGER0', 'PROCEDURE_C', 'PROCEDURE_D', 'SPORT_TEAM_SEQ', 'PLAYER_SEQ', 'SPORTING_EVENT_SEQ', 'SPORTING_EVENT_TICKET_SEQ', 'SPORTING_EVENT_INFO', 'TRIGGER1']
```

#### List all dependencies within a Object in Oracle.
```sh
python3 dcganalyzer.py dependency-analyzer --schemaname <<SCHEMANAME>> --object-name <<OBJECT-NAME>>
```
```console
Parent object : PROCEDURE_A
Dependencies
+-----------+---------+----------------------------------------------------+
| Type      |   Count | Names                                              |
+===========+=========+====================================================+
| PROCEDURE |       4 | PROCEDURE_B, PROCEDURE_C, PROCEDURE_C, PROCEDURE_D |
+-----------+---------+----------------------------------------------------+
```

#### Generate Dependency JSON for Oracle Schema
```sh
python3 dcganalyzer.py dependency-analyzer --schemaname <<SCHEMANAME>> --generate_json
```
```console
Dependency json file is generate successfully : /home/dcgcore/codedependencyanalyzer/backend/dms_sample_dependency.json
```

#### Generate Dependency JSON for Oracle Schema with Tables
```sh
python3 dcganalyzer.py dependency-analyzer --schemaname <<SCHEMANAME>> --generate_json --include-table
```
```console
Dependency json file is generate successfully : /home/dcgcore/codedependencyanalyzer/backend/dms_sample_dependency.json
```

## Output
The tool generates dependency JSON using `--generate-config` option, that is used to upload on DCG Dependency Analyzer UI.

## Troubleshooting
- Ensure your Oracle credentials are correct.
- Make sure Oracle Instant Client is installed and configured correctly.
- Check if required Python packages are installed.

## Credit
Tool is built upon ideas from AWS’s blog post on database object dependency analysis.
Check out the original work --> 🔗 [Here](https://aws.amazon.com/blogs/database/analyze-amazon-rds-for-oracle-database-object-dependencies/)  


## Contact
For any issues or feature requests, Please contact us on contact@datacloudgaze.com.

