from fastapi import APIRouter
router = APIRouter()


input_dict = {
    1: "John",
    2: "Robert",
    3: "Allen"
}

@router.get("/name-read/{input_id}")
def read_name(input_id: int):
    if input_id in input_dict:
        return {f"Candidate name is: {input_dict[input_id]}"}
    else:
        return {f"Candidate not found"}

@router.post("/name-create")
def create_name(input_id: int):
    if input_id not in input_dict:
        input_dict[input_id] = "Unknown"
        return {"Added Record Successfully": input_dict}
    else:
        return {"Already have in input_dict"}

@router.put("/name-read-put/{input_id}")
def update_name(input_id: int, name: str):
    if input_id in input_dict:
        input_dict[input_id] = name
        return {"Updated Record Successfully": input_dict}
    else:
        return {"Not found in input_dict"}

@router.patch("/name-read-patch/{input_id}")
def update_name_using_patch(input_id: int, name: str):
    if input_id in input_dict:
        input_dict[input_id] = name
        return {"Updated Record Successfully": input_dict}
    else:
        return {"Not found in input_dict"}

@router.delete("/name-delete/{input_id}")
def delete_name(input_id: int):
    if input_id in input_dict:
        del input_dict[input_id]
        return {"Deleted Record Successfully": input_dict}
    else:
        return {"Not found in input_dict"}




