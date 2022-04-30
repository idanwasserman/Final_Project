db = db.getSiblingDB("project_db");
db.project_tb.drop();

db.project_tb.insertMany([
    {
        "_id": "1",
        "type": "USER",
        "attributes": {
            "name": "idan",
            "email": "idan@gmail.com",
            "password": "123456"
        },
        "parent": null,
        "children": ["3"]
    },
    {
        "_id": "2",
        "type": "USER",
        "attributes": {
            "name": "meron",
            "email": "meron@gmail.com",
            "password": "abcdef"
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