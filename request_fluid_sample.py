import asyncio
from os import environ
from onlinepvt.models import RequestFluidResult, ApiCallResult, ExceptionInfo, ApiFluid, EosModel, CpModel, PropertyReferencePoint, ProblemDetails
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


def print_fluid(fluid: ApiFluid):
    print(f"Fluid: {fluid.name}")
    print(f"Comment: {fluid.comment}")
    eos = "PC-SAFT" if fluid.eos == EosModel.PCSAFT else "coPC-SAFT"
    print(f"EoS: {eos}")
    model = "Polynomial" if fluid.solvent_cp == CpModel.POLYNOMIAL else "DIPPR"
    print(f"Solvent Cp: {model}")
    model = "Polynomial" if fluid.polymer_cp == CpModel.POLYNOMIAL else "DIPPR"
    print(f"Polymer Cp: {model}")
    ref_point = "Original"
    if fluid.property_reference_point == PropertyReferencePoint.IDEAL_GAS:
        ref_point = "Ideal Gas"
    elif fluid.property_reference_point == PropertyReferencePoint.STANDARD_STATE:
        ref_point = "Standard State"
    print(f"Property reference point: {ref_point}")

    print(f"No standard components: {len(fluid.standards)}")
    print(f"No polymers: {len(fluid.polymers)}")


async def request_fluid():
    client = create_client()

    input = client.get_request_fluid_input()
    input.fluid_id = "9E9ABAD5-C6CA-427F-B5E7-15AB3F7CF076"

    result: RequestFluidResult = await client.request_fluid_async(input)
    # Always do the cleanup
    await client.cleanup()

    if (isinstance(result, ProblemDetails)):
        print_problem_details(result)
    elif (result.api_status == ApiCallResult.SUCCESS):
        print_fluid(result.fluid)
    else:
        print_exception_info(result.exception_info)

loop = asyncio.get_event_loop()
loop.run_until_complete(request_fluid())
