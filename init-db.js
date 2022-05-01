db = db.getSiblingDB("project_db");
db.project_tb.drop();
db.users.drop()

db.project_tb.insertMany([
    {
        "_id": "1",
        "type": "QUERY",
        "attributes": {
            "code": "drop database",
            "result": "might be sql injection"
        },
        "parent": null,
        "children": []
    },
    {
        "_id": "2",
        "type": "QUERY",
        "attributes": {
            "code": "drop database",
            "result": "might be sql injection"
        },
        "parent": null,
        "children": []
    },
    {
        "_id": "3",
        "type": "QUERY",
        "attributes": {
            "code": "drop database",
            "result": "might be sql injection"
        },
        "parent": "1",
        "children": []
    },
]);
