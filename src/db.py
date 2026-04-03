import datetime
from enum import Enum

from bson import objectid
from pymongo import MongoClient


class NotFoundError(Exception):
    """Exception raised for data not found

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SortTranscripts(Enum):
    DATE_INCREASING = ("created_at", 1)
    DATE_DECREASING = ("created_at", -1)
    NAME_INCREASING = ("filename", 1)
    NAME_DECREASING = ("filename", -1)


class TranscriptDB:
    def __init__(self, client: MongoClient):
        self.client = client
        self.db = self.client["whisper"]
        self.collection = self.db["transcriptions"]

    def insert_item(
        self, filename: str, language: str, result_text: str, result_segments: list
    ):
        created_at = datetime.datetime.now()
        self.collection.insert_one(
            {
                "filename": filename,
                "language": language,
                "text": result_text,
                "segments": result_segments,
                "created_at": created_at,
            }
        )

    def get_all(
        self,
        sort_by: SortTranscripts = SortTranscripts.DATE_INCREASING,
    ) -> dict[str, list]:
        sort_feature, sort_value = sort_by.value
        data = self.collection.find().sort(sort_feature, sort_value)

        return {"history": [{**d, "_id": str(d["_id"])} for d in data]}

    def get_item(self, id: str):
        data = self.collection.find_one({"_id": objectid.ObjectId(id)})
        if not data:
            raise NotFoundError("Did not found a document with given id")
        data["_id"] = str(data["_id"])
        return data
