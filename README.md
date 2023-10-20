# Me Suenas Project

<div align="center">
    <img src="logo.png" alt="Logo" width="800">
</div>

## Overview
Me Suenas is an open-source project inspired by a personal experience of the original author. The phrase "Me suenas" was what the significant other told the developer, which translates to "I think I know you from before". This project explores the possibility of having crossed paths with a friend or significant other before officially meeting them. By utilizing exported Google Location History data in JSON format, this project analyzes and identifies when and where such encounters might have occurred.

To get started, both individuals need to export their Google Location History data by visiting [Google Takeout](https://takeout.google.com/), deselecting all options, selecting only Google Location History, and downloading the JSON file with default settings.

## Environment Setup

1. **Python Version:**
   Ensure you have Python 3.11.5 installed. You can download it from the [official website](https://www.python.org/downloads/release/python-3115/).

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/me_suenas.git
   cd me_suenas

3. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
    If you are using Windows, run the following command instead:
    ```bash
    venv\Scripts\activate
    ```
    You should see `(venv)` appear at the beginning of your terminal prompt indicating that you are working inside the virtual environment.

4. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuring Kedro

# Update Data Catalog
Open the catalog.yml file located in the conf/base/ directory. Copy it to the conf/local/ directory. Then, update the file paths for data_x_raw and data_y_raw to point to the respective directories containing the exported Google Location History data for each person.

# Update Parameters
Open the parameters.yml file, also located in the conf/base/ directory. Copy it to the conf/local/ directory. Then, update the following parameters:

- x_name: Name of the person corresponding to data_x.
- y_name: Name of the person corresponding to data_y.
- accuracy_level: Desired accuracy level for distance calculations.
- time_margin: Time margin (in minutes) for time calculations.
- first_meeting_date: Date of the first official meeting in the format 'YYYY-MM-DD HH:MM:SS'.

## Running the Project
With the environment set up and the Kedro configuration updated, you're now ready to run the project:
    ```bash
    kedro run
    ```

Wait for the process to complete, and then check the data/encounters/ directory for the output CSV file containing the identified encounters.

**Contributions, feedback, and issues are welcome! Feel free to open an issue or submit a pull request.**