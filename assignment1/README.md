# Bookmark Application
The application is built using Flask and SqliteDict. It also uses Caching to make data retrieval more efficient

## Installation

### Adding dummy Bookmarks to the DB
To generate a bunch of dummy data and add it to the DB, run the following
```python
cd assignment1/data
python generate_json_data.py
```
The dummy data that has been stored to the DB is also cloned into a data.json file in the same directory for easy access. Note: Any other data added to the DB using the POST request will not be visible in the data.json file

### Running the application
```bash
cd assignment1
pipenv shell
pipenv install
python runserver.py
```
Once the server starts open http://0.0.0.0:5000/ on a web browser to get the home page


## API Endpoints

### GET /
Application home page. Open it on the browser
![Screen Shot 2020-09-23 at 10 54 12](https://user-images.githubusercontent.com/9063088/94050461-261df380-fd8b-11ea-9479-010b14a9f2d2.png)

### GET /dashboard

Open this URL on the browser to get the Flask Monitoring Dashboard.

Username: admin </br>
Pwd: admin

_Response_

```
200 OK
```

### POST /api/bookmarks

_Request_

```
{
    "name": "Pinterest",
    "url": "https://www.pinterest.com/pin/27373510214883341/",
    "description": "Innovation Engine"
}
```

_Response_

201 Created

```
{"id": "1238479123749123750912734"}
```

If the URL is already in the DB, the POST API will return HTTP 400 error.

_Response_

400 Bad Request

```
{'error': '400 Bad Request'}
```

### GET /api/bookmarks/1238479123749123750912734

```
{
    "id": "abc123",
    "name": "Pinterest",
    "url": "https://www.pinterest.com/pin/27373510214883341/",
    "description": "Innovation Engine"
}
```
Every time you hit the GET request, the count of the bookmark will be incremented

If the request bookmark id does not exist in the system, the API will return:

_Response_

404 Not Found
```
{'error': '404 Not found'}
```

### GET /api/bookmarks/1238479123749123750912734/qrcode

200 OK

Return QR Code PNG image. To access the QR Code, open the URL in the browser

![Screen Shot 2020-09-23 at 10 50 13](https://user-images.githubusercontent.com/9063088/94050081-a132da00-fd8a-11ea-8545-5ce9ff757087.png)

### DELETE /api/bookmarks/1238479123749123750912734

204 No Content

### GET /api/bookmarks/1238479123749123750912734/stats

First make this request on Postman without passing an ETag in the Request Header. This should return the count of the above bookmark

_Response Body_

```
{"count": "1"}
```
_Response Header_

```
200 OK
ETag: 1
```

Now use the count value as the Etag header in the next request on Postman and submit the request

_Request Header_

```
ETag: 1
```

_Response Header_

```
304 Not Modified
ETag: 1
```

Now submit the GET bookmark request to increment the count and try to submit the /stats endpoint with old ETag

_Response Header_
```
200 OK
ETag: 2
```
_Response Body_
```
{"count": "2"}
```
