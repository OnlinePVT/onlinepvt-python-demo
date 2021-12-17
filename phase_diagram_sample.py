import asyncio
from os import environ
import matplotlib.pyplot as plt
from onlinepvt.models import CalculationComposition, ExceptionInfo, ApiCallResult, ProblemDetails
from onlinepvt.online_pvt_client import OnlinePvtClient


def create_client():
    # safest is to store secrets in Environment Variables
    user_id = environ.get("ONLINEPVT_USER_ID")
    access_secret = environ.get("ONLINEPVT_ACCESS_SECRET")
    return OnlinePvtClient("https://api.onlinepvt.com", user_id, access_secret)


def print_exception_info(exception_info: ExceptionInfo):
    print(f"Date: {exception_info.date}")
    print(f"Message Type: {exception_info.message_type}")
    print(f"Message: {exception_info.message}")
    print("")
    print(f"Stack Trace: {exception_info.stack_trace}")


def print_problem_details(details: ProblemDetails):
    print("------ A problem occured --------")
    print(f"Title: {details.title}")
    print(f"Type: {details.type}")
    print(f"Status: {details.status}")
    print(f"Detail: {details.detail}")
    print(f"Instance: {details.instance}")
    print(f"Additional properties: {details.additional_properties}")


async def call_phase_diagram():
    client = create_client()

    input = client.get_phasediagam_standard_input()
    input.fluid_id = "9E9ABAD5-C6CA-427F-B5E7-15AB3F7CF076"
    input.components = [CalculationComposition(mass=0.78), CalculationComposition(
        mass=0.02), CalculationComposition(mass=0.2)]

    result = await client.call_calculation_phasediagram_standard_async(input)
    # Always do the cleanup
    await client.cleanup()

    if (isinstance(result, ProblemDetails)):
        print_problem_details(result)
    elif (result.api_status == ApiCallResult.SUCCESS):
        plt.title("Phase diagram")
        plt.xlabel(f"Temperature [{result.curve.temperature_units}]")
        plt.ylabel(f"Pressure [{result.curve.pressure_units}]")

        if (len(result.curve.phaseenvelope) > 0):
            plt.plot(list(map(lambda point: point.temperature, result.curve.phaseenvelope)), list(
                map(lambda point: point.pressure, result.curve.phaseenvelope)), label=f"Phase Envelope")
        if (len(result.curve.vlle) > 0):
            plt.plot(list(map(lambda point: point.temperature, result.curve.vlle)), list(
                map(lambda point: point.pressure, result.curve.vlle)), label=f"VLLE")
        if (len(result.curve.sle) > 0):
            plt.plot(list(map(lambda point: point.temperature, result.curve.sle)), list(
                map(lambda point: point.pressure, result.curve.sle)), label=f"SLE")
        if (len(result.curve.slve) > 0):
            plt.plot(list(map(lambda point: point.temperature, result.curve.slve)), list(
                map(lambda point: point.pressure, result.curve.slve)), label=f"SLVE")

        plt.legend()
        plt.show()
    else:
        print_exception_info(result.exception_info)


loop = asyncio.get_event_loop()
loop.run_until_complete(call_phase_diagram())
