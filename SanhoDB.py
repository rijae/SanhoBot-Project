import json
import os


class SanhoDB:
    @staticmethod
    def setup_data():
        if not os.path.isdir("./Data"):
            os.mkdir(
                path="./Data"
            )
        os.chdir(
            path="./Data"
        )

        if not os.path.isdir("./Temp"):
            os.mkdir(
                path="./Temp"
            )

        if not os.path.isdir("./Users"):
            os.mkdir(
                path="./Users"
            )

    @staticmethod
    def user_data_exists(
        user_id: int
    ):
        return os.path.isfile(
            path=f"./Users/{user_id}.json"
        )

    @staticmethod
    def create_user_data(
        user_id: int
    ):
        user_json_file_path = f"./Users/{user_id}.json"
        if not SanhoDB.user_data_exists(user_id):
            open(
                file=user_json_file_path,
                mode="w"
            ).close()

            with open(
                file=user_json_file_path,
                mode="w",
                encoding="utf-8"
            ) as user_json_file_init:
                json.dump(
                    obj={
                        "level": 1,
                        "exp": 0,
                        "bag": {
                            "money": 1000,
                            "item_list": [
                                {
                                    "item_type": "나무 단도 Wooden Dagger",
                                    "item_count": 1
                                },
                                {
                                    "item_type": "사과 Apple",
                                    "item_count": 10
                                }
                            ]
                        }
                    },
                    fp=user_json_file_init,
                    indent=4,
                    ensure_ascii=False
                )

            return 0
        else:
            return -1

    @staticmethod
    def load_user_data(
        user_id: int
    ):
        user_json_file_path = f"./Users/{user_id}.json"

        if not SanhoDB.user_data_exists(user_id):
            SanhoDB.create_user_data(user_id)

        with open(
            file=user_json_file_path,
            mode="r",
            encoding="utf-8"
        ) as user_json_file_loader:
            return json.load(
                fp=user_json_file_loader
            )

    @staticmethod
    def dump_user_data(
        user_id: int,
        obj: dict
    ):
        user_json_file_path = f"./Users/{user_id}.json"

        if not SanhoDB.user_data_exists(user_id):
            SanhoDB.create_user_data(user_id)

        with open(
            file=user_json_file_path,
            mode="w",
            encoding="utf-8"
        ) as user_json_file_dumper:
            json.dump(
                obj=obj,
                fp=user_json_file_dumper,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def add_user_item(
        item: dict,
        user_id: int
    ):
        data = SanhoDB.load_user_data(user_id)

        if "item_type" in item and "item_count" in item:
            for item_index, item_stack in enumerate(data["bag"]["item_list"]):
                if item_stack["item_type"] == item["item_type"]:
                    data["bag"]["item_list"][item_index]["item_count"] += item["item_count"]
                    break
                if item_index == len(data["bag"]["item_list"]) - 1:
                    data["bag"]["item_list"].append({
                        "item_type": item["item_type"],
                        "item_count": item["item_count"]
                    })
                    break

            SanhoDB.dump_user_data(
                obj=data,
                user_id=user_id
            )
        else:
            return -1

    @staticmethod
    def remove_user_item(
        item: dict,
        user_id: int
    ):
        data = SanhoDB.load_user_data(user_id)

        if "item_type" in item and "item_count" in item:
            left_item_count = item["item_count"]

            for item_index, item_stack in enumerate(data["bag"]["item_list"]):
                if left_item_count == 0:
                    SanhoDB.dump_user_data(
                        obj=data,
                        user_id=user_id
                    )

                if item_stack["item_type"] == item["item_type"]:
                    if item_stack["item_count"] < left_item_count:
                        left_item_count -= item_stack["item_count"]
                        item_stack["item_count"] = 0
                    else:
                        item_stack["item_count"] -= left_item_count
                        left_item_count = 0

                data["bag"]["item_list"][item_index] = item_stack

            return -2
        else:
            return -1
