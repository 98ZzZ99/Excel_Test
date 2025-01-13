import os
import datetime
import pandas as pd
from typing import Optional, Union
from langchain.agents import tool


def _process_worker_data(file_path: str) -> pd.DataFrame:
    """
    Read Excel and calculate the results, returning a DataFrame containing all worker information.
    """
    df = pd.read_excel(file_path, index_col=None)

    required_columns = ["ID", "start", "end", "number"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing one or more required columns: {required_columns}")

    results = []
    for _, row in df.iterrows():
        worker_id = str(row["ID"]).zfill(5)
        start_time = row["start"]
        end_time = row["end"]
        number_completed = row["number"]

        # Convert start_time and end_time to datetime.time objects
        if not isinstance(start_time, datetime.time):
            start_time = pd.to_datetime(start_time).time()
        if not isinstance(end_time, datetime.time):
            end_time = pd.to_datetime(end_time).time()

        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        work_time = end_minutes - start_minutes
        if work_time <= 0:
            # Skip this worker's data or continue processing
            continue

        work_hour = work_time // 60
        work_min = work_time % 60
        work_duration = f"{work_hour:02d}:{work_min:02d}"
        kpi = number_completed / work_time

        results.append({
            "ID": worker_id,
            "start": f"{start_time.hour:02d}:{start_time.minute:02d}",
            "end": f"{end_time.hour:02d}:{end_time.minute:02d}",
            "work": work_duration,
            "KPI": round(kpi, 4)
        })

    if not results:
        raise ValueError("No valid results were processed from the Excel file")

    results_df = pd.DataFrame(results)
    results_df['ID'] = results_df['ID'].astype(str)
    results_df.sort_values("KPI", ascending=False, inplace=True)

    return results_df


# Multi-parameter tool, not compatible with ZeroShotAgent!!!
# @tool("load_excel_data", return_direct=False)
# def load_excel_data_tool(
#         file_path: str,
#         worker_id: Optional[str] = None
# ) -> Union[str, dict]:
#     """
#     Read Excel file and return worker data:
#     - If worker_id is not provided, the information of all workers (ID, start, end, work, KPI) is returned.
#     - If a worker_id is provided, only the specific information of that worker will be returned
#
#     Args:
#         file_path (str): Excel file path
#         worker_id (str): Specify the worker ID (optional)
#
#     Returns:
#         Union[str, dict]: Returns JSON or string; or returns an error message
#     """
#     try:
#         df = _process_worker_data(file_path)
#     except Exception as e:
#         return f"Error processing Excel file: {str(e)}"
#
#     if worker_id:
#         # Query the specified ID
#         worker_data = df[df["ID"] == worker_id]
#         if worker_data.empty:
#             return f"No worker found with ID: {worker_id}"
#         # Convert to json or string output, here we return dict
#         return worker_data.to_dict(orient="records")
#     else:
#         # If worker_id is not specified, data of all workers will be returned.
#         return df.to_dict(orient="records")


@tool("load_excel_data", return_direct=False)
def load_excel_data_tool(input_str: str) -> Union[str, dict]:
    """
    Change to string input.
    Input format example:
        "file_path=E:/LLMTest/Test.xlsx; worker_id=23456"
    The tool parses the string and extracts the parameters.
    """
    try:
        # Parsing the input string
        inputs = dict(item.split("=") for item in input_str.split(";"))
        file_path = inputs.get("file_path")
        worker_id = inputs.get("worker_id", None)

        # Standardize file paths
        file_path = os.path.normpath(file_path) # Very important to prevent slashes and backslashes from causing problems

        df = _process_worker_data(file_path)
        if worker_id:
            worker_data = df[df["ID"] == worker_id]
            if worker_data.empty:
                return f"No worker found with ID: {worker_id}. Available IDs: {df['ID'].tolist()}"
            return {"message": "Worker data loaded successfully", "data": worker_data.to_dict(orient="records")}
        else:
            return {"message": "All worker data loaded successfully", "data": df.to_dict(orient="records")}
    except Exception as e:
        return f"Error processing input: {str(e)}"



@tool("get_top_bottom_kpi", return_direct=False)
def get_top_bottom_kpi_tool(input_str: str) -> Union[str, dict]:
    """
    Return the data of three workers with the highest KPI and three workers with the lowest KPI.
    Input format example:
        "file_path=E:/LLMTest/Test.xlsx"
    """
    try:
        inputs = dict(item.split("=") for item in input_str.split(";"))
        file_path = inputs.get("file_path")

        # Standardize file paths
        file_path = os.path.normpath(file_path)

        df = _process_worker_data(file_path)
        top_3 = df.head(3).to_dict(orient="records")
        bottom_3 = df.tail(3).to_dict(orient="records")
        return {"top_3_workers": top_3, "bottom_3_workers": bottom_3}
    except Exception as e:
        return f"Error processing input: {str(e)}"


